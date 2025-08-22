# training_graph.py (B con pipeline idéntico al de A)
from __future__ import annotations

from pathlib import Path
from typing import Optional
import csv
import numpy as np

# OVITO
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier,
    ClusterAnalysisModifier,
)

# Convex Hull (área/volumen)
from scipy.spatial import ConvexHull, QhullError

# Config v1 inyectada (NO reabrimos el JSON)
from openvancy.utils.config_loader import Config as V1Config


class AtomicGraphGenerator:
    """
    Versión B que **replica exactamente** el pipeline de A.

    - No reabre input_params.json; recibe `cfg: V1Config`.
    - Importa el dump una sola vez.
    - Aplica el **mismo orden de modificadores** que A:
        1) ExpressionSelection → DeleteSelected
        2) ConstructSurface(select_surface_particles=True)
        3) InvertSelection → DeleteSelected (quedarse solo con la superficie)
        4) ClusterAnalysis (para quedarnos con el cluster más grande, si hace falta)
    - Exporta dumps `graph_{i}_{a}.dump` y CSV con columnas: vacancys, cluster_size, surface_area, filled_volume.
    """

    def __init__(
        self,
        *,
        cfg: V1Config,
        input_path: Optional[str | Path] = None,
        expression: Optional[str] = None,
        # radio de vecindad para análisis de clusters (coincidir con A)
        neighbor_radius: float = 3.25,
        # parámetros ConstructSurface (coincidir con A)
        smoothing_level: int = 0,
        iterations: int = 1,
        alpha_radius: Optional[float] = None,
        # control de salidas
        export_dumps: bool = True,
        dumps_dirname: str = "dump/training",
        csv_name: str = "training_graph.csv",
        # lazos
        max_graph_size: Optional[int] = None,
        training_file_index: Optional[int] = None,
    ):
        if isinstance(cfg, dict):
            self.cfg = V1Config.from_dict(cfg)  # por si llega como dict
        else:
            self.cfg: V1Config = cfg

        self.input_path = Path(input_path) if input_path else Path(self.cfg.paths.defect_inputs[0])
        self.outputs_root = Path(self.cfg.paths.outputs_root)
        self.dump_dir = self.outputs_root / dumps_dirname
        self.csv_path = self.outputs_root / "csv" / csv_name

        self.expression = expression or getattr(self.cfg, "selection", {}).get("expression", "False")
        # NOTA: "False" no selecciona nada → DeleteSelected no borra nada (seguro por defecto)

        self.neighbor_radius = neighbor_radius
        self.smoothing_level = smoothing_level
        self.iterations = iterations
        self.alpha_radius = alpha_radius

        self.export_dumps = export_dumps
        self.max_graph_size = max_graph_size if max_graph_size is not None else getattr(self.cfg.training, "max_graph_size", 1)
        self.training_file_index = (
            training_file_index if training_file_index is not None else getattr(self.cfg.training, "training_file_index", 1)
        )

        self.pipeline = None

    # ----------------------------- utilitarios -----------------------------
    def _ensure_dirs(self):
        (self.outputs_root / "csv").mkdir(parents=True, exist_ok=True)
        if self.export_dumps:
            self.dump_dir.mkdir(parents=True, exist_ok=True)

    def _import_once(self):
        if not self.input_path.exists():
            raise FileNotFoundError(f"No existe el archivo de entrada: {self.input_path}")
        # Igual que A → multiple_frames=True si A lo hacía, aquí lo dejamos en True por compatibilidad
        self.pipeline = import_file(str(self.input_path), multiple_frames=True)

    # ------------------------------ pipeline A -----------------------------
    def _apply_pipeline_A(self):
        p = self.pipeline
        p.modifiers.clear()

        # (1) ExpressionSelection → DeleteSelected   (A BORRA lo seleccionado)
        p.modifiers.append(ExpressionSelectionModifier(expression=self.expression))
        p.modifiers.append(DeleteSelectedModifier())

        # (2) ConstructSurface(select_surface_particles=True)
        p.modifiers.append(
            ConstructSurfaceModifier(
                method=ConstructSurfaceModifier.Method.AlphaShape,
                select_surface_particles=True,
                smoothing_level=self.smoothing_level,
                radius=self.alpha_radius if self.alpha_radius is not None else 2.7,
                iterations=self.iterations,
            )
        )
        # (3) InvertSelection → DeleteSelected   (quedarse SOLO con superficie)
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())

        # (4) ClusterAnalysis (quedarse con el cluster más grande)
        p.modifiers.append(
            ClusterAnalysisModifier(
                cutoff=self.neighbor_radius,
                sort_by_size=True,
                cluster_coloring=False,
                compute_com=True,
            )
        )

    # ---------------------------- mediciones -------------------------------
    @staticmethod
    def _largest_cluster_size(data) -> int:
        if "Cluster" not in data.particles:
            return int(len(data.particles.positions))
        cl = data.particles["Cluster"].array
        if cl.size == 0:
            return 0
        # IDs de clusters empiezan en 1; cluster 1 es el más grande por sort_by_size=True
        return int(np.sum(cl == 1))

    @staticmethod
    def _convex_hull_area_volume(positions: np.ndarray) -> tuple[float, float]:
        if positions.shape[0] < 4:
            return float("nan"), float("nan")
        rank = np.linalg.matrix_rank(positions - positions.mean(axis=0))
        if rank < 3:
            return float("nan"), float("nan")
        try:
            hull = ConvexHull(positions)
            return float(hull.area), float(hull.volume)
        except QhullError:
            return float("nan"), float("nan")

    # ----------------------------- ejecución ------------------------------
    def run(self):
        self._ensure_dirs()
        self._import_once()

        header = ["vacancys", "cluster_size", "surface_area", "filled_volume"]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)

            # i: índice de vacancias; a: variación de grafo
            for i in range(1, int(self.training_file_index) + 1):
                for a in range(1, int(self.max_graph_size) + 1):
                    # Aplica el pipeline A
                    self._apply_pipeline_A()
                    data = self.pipeline.compute()

                    # Si queremos quedarnos solo con el cluster más grande, reducimos la nube
                    if "Cluster" in data.particles:
                        # Seleccionamos todo lo que NO es cluster 1 y lo borramos
                        self.pipeline.modifiers.append(
                            ExpressionSelectionModifier(expression="Cluster != 1")
                        )
                        self.pipeline.modifiers.append(DeleteSelectedModifier())
                        data = self.pipeline.compute()

                    positions = data.particles.positions.array.copy()
                    cluster_size = self._largest_cluster_size(data)
                    surface_area, filled_volume = self._convex_hull_area_volume(positions)

                    # Exportar dump
                    dump_path = None
                    if self.export_dumps:
                        dump_path = self.dump_dir / f"graph_{i}_{a}.dump"
                        export_file(
                            data,
                            str(dump_path),
                            "lammps/dump",
                            columns=[
                                "Particle Identifier",
                                "Particle Type",
                                "Position.X",
                                "Position.Y",
                                "Position.Z",
                            ],
                        )

                    # CSV
                    w.writerow([i, cluster_size, surface_area, filled_volume])

        return str(self.csv_path)


# Uso rápido de referencia (no ejecutar aquí si el proyecto importa este módulo)
# if __name__ == "__main__":
#     from openvancy.utils.config_loader import Config
#     cfg = Config.from_json("input_params.json")  # o desde tu pipeline real
#     gen = AtomicGraphGenerator(cfg=cfg)
#     out_csv = gen.run()
#     print("CSV:", out_csv)
