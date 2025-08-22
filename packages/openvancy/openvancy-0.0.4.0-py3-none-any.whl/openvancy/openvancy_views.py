import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Forzar backend XCB en Wayland (evita crash con Wayland)
os.environ["QT_QPA_PLATFORM"] = os.environ.get("QT_QPA_PLATFORM", "xcb")

# --- Qt / UI ---
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget, QGroupBox
)

# --- Visualización ---
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# --- OVITO ---
from ovito.io import import_file

# --- Trainer/Preparer ---
from openvancy.training.preparer import TrainingPreparer

# =====================
#  Gestión de params
# =====================
GUI_ROOT = Path(__file__).resolve().parent

def runtime_params_path() -> Path:
    """Garantiza que exista un input_params.json en el CWD.
    Si hay uno junto al módulo, lo copia al CWD la primera vez."""
    cwd_params = Path.cwd() / "input_params.json"
    if cwd_params.exists():
        return cwd_params
    src_params = GUI_ROOT / "input_params.json"
    if src_params.exists():
        shutil.copy(src_params, cwd_params)
        return cwd_params
    # Si no hay ninguno, crea uno mínimo
    cwd_params.write_text(json.dumps({"CONFIG": [{}]}, indent=4))
    return cwd_params

PARAMS_FILE = runtime_params_path()

def load_params() -> dict:
    try:
        return json.loads(PARAMS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"CONFIG": [{}]}

def save_params(params: dict, target_path: Path | None = None) -> Path:
    if target_path is None:
        target_path = Path.cwd() / "input_params.json"
    target_path.write_text(json.dumps(params, indent=4), encoding="utf-8")
    return target_path

# =====================
#  Render común (OVITO)
# =====================

def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    """Dibuja celda y puntos. Colorea por 'Cluster' si existe.
    """
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    # Celda: matriz 3x4 (columnas: a1,a2,a3,origin)
    M = np.asarray(data.cell.matrix, dtype=float)
    a1, a2, a3, origin = M[:, 0], M[:, 1], M[:, 2], M[:, 3]
    corners = [
        origin,
        origin + a1,
        origin + a2,
        origin + a3,
        origin + a1 + a2,
        origin + a1 + a3,
        origin + a2 + a3,
        origin + a1 + a2 + a3,
    ]
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

    # Partículas
    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    # Cluster (opcional)
    cluster_vals = None
    for name in ("Cluster", "cluster", "c_Cluster", "c_cluster", "ClusterID", "cluster_id"):
        if name in data.particles:
            prop = data.particles[name]
            arr = prop.array if hasattr(prop, "array") else prop
            cluster_vals = np.asarray(arr).astype(int).reshape(-1)
            break

    cluster_idx = None
    unique_clusters = None
    if cluster_vals is not None and cluster_vals.shape[0] == positions.shape[0]:
        unique_clusters = np.unique(cluster_vals)
        map_idx = {val: i for i, val in enumerate(unique_clusters)}
        cluster_idx = np.vectorize(map_idx.get, otypes=[int])(cluster_vals)

    # 3D
    plotter.clear()
    for i, j in edges:
        plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

    if cluster_idx is not None:
        pts = pv.PolyData(positions)
        pts["cluster"] = cluster_idx
        plotter.add_mesh(pts, scalars="cluster", render_points_as_spheres=True,
                         point_size=8, cmap="tab20", show_scalar_bar=False)
    else:
        plotter.add_mesh(pv.PolyData(positions), color="black",
                         render_points_as_spheres=True, point_size=8)

    plotter.reset_camera(); plotter.set_scale(1, 1, 1)

    # 2D (XY)
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)

    if cluster_idx is not None:
        ax.scatter(positions[:, 0], positions[:, 1], s=10, c=cluster_idx, cmap="tab20",
                   vmin=0, vmax=len(unique_clusters)-1)
    else:
        ax.scatter(positions[:, 0], positions[:, 1], s=10, color="k")

    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box'); ax.grid(True, linewidth=0.3)
    fig.canvas.draw()

# =====================
#  Pestaña: Training
# =====================

class TrainingTab(QWidget):
    """
    Pestaña 'Training' para configurar generación de red perfecta y features.
    Guarda en params['CONFIG'][0]['training_setup'] con claves NUEVAS (snake_case):
      - surface_area {enabled, rc}
      - volume {enabled}
      - cluster_size {enabled, radius, orders}
      - convex_hull {enabled, area, volume}
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Cargar y normalizar params actuales
        self.params = load_params()
        self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        tr_raw = self.cfg.get('training_setup', {})
        tr = self._normalize_training_dict(tr_raw)

        root = QVBoxLayout(self)

        # ===== Red perfecta =====
        box_net = QGroupBox("Red perfecta de entrenamiento (.dump)")
        form_net = QFormLayout(box_net)

        self.combo_lattice = QComboBox(); self.combo_lattice.addItems(["fcc", "bcc"])
        self.combo_lattice.setCurrentText(tr.get('perfect_network', {}).get('lattice', "fcc"))

        self.spin_a0 = QDoubleSpinBox(); self._cfg_spin(self.spin_a0, 0.0, 50.0,
                                                        float(tr.get('perfect_network', {}).get('a0', 3.52)),
                                                        step=0.01, decimals=3)
        cells_def = tr.get('perfect_network', {}).get('cells', [1, 1, 1])
        self.spin_rx = QSpinBox(); self._cfg_spin(self.spin_rx, 1, 500, int(cells_def[0]))
        self.spin_ry = QSpinBox(); self._cfg_spin(self.spin_ry, 1, 500, int(cells_def[1]))
        self.spin_rz = QSpinBox(); self._cfg_spin(self.spin_rz, 1, 500, int(cells_def[2]))
        self.edit_atom = QLineEdit(tr.get('perfect_network', {}).get('atom', "Fe"))

        btn_gen = QPushButton("Generar red perfecta"); btn_gen.clicked.connect(self._generate_stub)

        form_net.addRow("Lattice:", self.combo_lattice)
        form_net.addRow("a₀ (Å):", self.spin_a0)
        form_net.addRow("Réplicas X:", self.spin_rx)
        form_net.addRow("Réplicas Y:", self.spin_ry)
        form_net.addRow("Réplicas Z:", self.spin_rz)
        form_net.addRow("Elemento:", self.edit_atom)
        form_net.addRow(btn_gen)
        root.addWidget(box_net)

        # ===== Configuración general de entrenamiento =====
        box_train = QGroupBox("Configuraciones de entrenamiento")
        form_train = QFormLayout(box_train)
        self.spin_iters = QSpinBox(); self._cfg_spin(self.spin_iters, 1, 1_000_000, int(tr.get('iterations', 1000)))
        self.spin_max_vacs = QSpinBox(); self._cfg_spin(self.spin_max_vacs, 0, 1_000_000, int(tr.get('max_vacancies', 0)))
        form_train.addRow("Iteraciones:", self.spin_iters)
        form_train.addRow("Vacancias máximas a retirar:", self.spin_max_vacs)
        root.addWidget(box_train)

        # ===== Features =====
        box_feat = QGroupBox("Features a extraer")
        feat_layout = QVBoxLayout(box_feat)

        # Surface Area (antes: coordinación)
        row_coord = QHBoxLayout()
        self.chk_coord = QCheckBox("Surface Area")
        self.spin_rc = QDoubleSpinBox(); self._cfg_spin(self.spin_rc, 0.0, 20.0,
                                                        float(tr.get('features', {}).get('surface_area', {}).get('rc', 2.00)),
                                                        step=0.01, decimals=2)
        row_coord.addWidget(self.chk_coord); row_coord.addStretch(); row_coord.addWidget(QLabel("rc (Å):")); row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Volume (antes: energy_potential)
        self.chk_energy = QCheckBox("Volume")
        feat_layout.addWidget(self.chk_energy)

        # Cluster Size (antes: Steinhardt)
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("Cluster Size")
        self.spin_qr = QDoubleSpinBox(); self._cfg_spin(self.spin_qr, 0.0, 20.0,
                                                        float(tr.get('features', {}).get('cluster_size', {}).get('radius', 2.70)),
                                                        step=0.01, decimals=2)
        row_s.addWidget(self.chk_steinhardt); row_s.addStretch(); row_s.addWidget(QLabel("r (Å):")); row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)

        row_orders = QHBoxLayout()
        self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8"); self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
            row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)

        # Convex Hull
        self.chk_hull = QCheckBox("Convex Hull")
        row_hull = QHBoxLayout(); self.chk_area = QCheckBox("Área"); self.chk_vol = QCheckBox("Volumen")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol)
        feat_layout.addWidget(self.chk_hull); feat_layout.addLayout(row_hull)
        root.addWidget(box_feat)

        # ===== Preview de red =====
        box_prev = QGroupBox("Preview de red"); prev_layout = QVBoxLayout(box_prev)
        self.lbl_atoms = QLabel("Átomos totales: -"); prev_layout.addWidget(self.lbl_atoms)
        self.preview_plotter = QtInteractor(box_prev); prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4, 4)); self.preview_canvas = FigureCanvas(self.preview_fig); prev_layout.addWidget(self.preview_canvas)
        root.addWidget(box_prev)

        # Señales → preview
        self.combo_lattice.currentTextChanged.connect(self.update_preview)
        self.spin_a0.valueChanged.connect(self.update_preview)
        self.spin_rx.valueChanged.connect(self.update_preview)
        self.spin_ry.valueChanged.connect(self.update_preview)
        self.spin_rz.valueChanged.connect(self.update_preview)
        self.update_preview()

        # ===== Botones =====
        row_btns = QHBoxLayout()
        btn_save = QPushButton("Guardar configuración")
        btn_load = QPushButton("Cargar configuración actual")
        btn_prepare = QPushButton("Preparar dataset")
        btn_save.clicked.connect(self.save_training_setup)
        btn_load.clicked.connect(self.load_from_params)
        btn_prepare.clicked.connect(self.on_prepare_training_clicked)
        row_btns.addWidget(btn_save); row_btns.addWidget(btn_load); row_btns.addWidget(btn_prepare)
        root.addLayout(row_btns)

        # Log local
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMinimumHeight(120)
        root.addWidget(self.log_box)

        # Estados iniciales de checks
        self.chk_coord.setChecked(tr.get('features', {}).get('surface_area', {}).get('enabled', True))
        self.chk_energy.setChecked(tr.get('features', {}).get('volume', {}).get('enabled', True))
        st = tr.get('features', {}).get('cluster_size', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True)); self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False)); self.chk_Q10.setChecked(orders.get('Q10', False)); self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = tr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False)); self.chk_area.setChecked(hull.get('area', True)); self.chk_vol.setChecked(hull.get('volume', True))

        # Habilitar subopciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled); self.spin_rc.setEnabled(self.chk_coord.isChecked())
        def _en_steinhardt(on: bool):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
                w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt); _en_steinhardt(self.chk_steinhardt.isChecked())
        def _en_hull(on: bool):
            for w in (self.chk_area, self.chk_vol):
                w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull); _en_hull(self.chk_hull.isChecked())

    # ===== Helpers =====
    def _cfg_spin(self, spin, mn, mx, val, step=1, decimals=None):
        spin.setRange(mn, mx)
        if isinstance(spin, QDoubleSpinBox):
            if decimals is not None:
                spin.setDecimals(decimals)
            spin.setSingleStep(step)
        else:
            spin.setSingleStep(int(step))
        spin.setValue(val)

    def _normalize_training_dict(self, tr: dict) -> dict:
        """Acepta nombres viejos y retorna dict con claves nuevas (snake_case)."""
        feats = (tr.get('features') or {})
        newf = {}
        # surface_area (antes: 'surface area', 'coordinacion', 'coordinación', 'coordination')
        sa = feats.get('surface_area') or feats.get('surface area') or feats.get('coordinacion') or feats.get('coordinación') or feats.get('coordination')
        if sa:
            newf['surface_area'] = {
                'enabled': bool(sa.get('enabled', True)),
                'rc': float(sa.get('rc', sa.get('radius', 2.0)))
            }
        # volume (corrige 'volumee', 'volumes', etc.)
        vol = feats.get('volume') or feats.get('volumee') or feats.get('volumes') or feats.get('Volumenss')
        if vol:
            newf['volume'] = {'enabled': bool(vol.get('enabled', True))}
        # cluster_size (antes: 'cluster size' o 'steinhardt')
        cs = feats.get('cluster_size') or feats.get('cluster size') or feats.get('steinhardt')
        if cs:
            newf['cluster_size'] = {
                'enabled': bool(cs.get('enabled', True)),
                'radius': float(cs.get('radius', 2.70)),
                'orders': dict(cs.get('orders', {'Q4': True, 'Q6': True}))
            }
        # convex_hull (corrige 'volumee')
        ch = feats.get('convex_hull')
        if ch:
            newf['convex_hull'] = {
                'enabled': bool(ch.get('enabled', False)),
                'area': bool(ch.get('area', True)),
                'volume': bool(ch.get('volume', ch.get('volumee', True)))
            }
        tr['features'] = newf
        return tr

    # ===== Acciones =====
    def save_training_setup(self):
        params = load_params(); cfg = params.setdefault('CONFIG', [{}])[0]
        features = {
            'surface_area': {
                'enabled': self.chk_coord.isChecked(),
                'rc': float(self.spin_rc.value()),
            },
            'volume': {
                'enabled': self.chk_energy.isChecked(),
            },
            'cluster_size': {
                'enabled': self.chk_steinhardt.isChecked(),
                'radius': float(self.spin_qr.value()),
                'orders': {
                    'Q4': self.chk_Q4.isChecked(), 'Q6': self.chk_Q6.isChecked(),
                    'Q8': self.chk_Q8.isChecked(), 'Q10': self.chk_Q10.isChecked(),
                    'Q12': self.chk_Q12.isChecked(),
                }
            },
            'convex_hull': {
                'enabled': self.chk_hull.isChecked(),
                'area': self.chk_area.isChecked(),
                'volume': self.chk_vol.isChecked(),
            },
        }
        setup = {
            'iterations': int(self.spin_iters.value()),
            'max_vacancies': int(self.spin_max_vacs.value()),
            'features': features,
            'perfect_network': {
                'lattice': self.combo_lattice.currentText(),
                'a0': float(self.spin_a0.value()),
                'cells': [int(self.spin_rx.value()), int(self.spin_ry.value()), int(self.spin_rz.value())],
                'atom': self.edit_atom.text().strip() or "Fe",
            }
        }
        cfg['training_setup'] = setup
        path = save_params(params)
        QMessageBox.information(self, "Training guardado", f"Se guardó training_setup en:\n{path}")

    def load_from_params(self):
        # Recarga completa por simplicidad
        self.__init__(self.parent)

    def _generate_stub(self):
        self.update_preview()
        QMessageBox.information(self, "Generar red perfecta",
                                "Preview actualizado con los parámetros actuales. Conectar aquí tu lógica de exportar .dump cuando lo tengas.")

    def on_prepare_training_clicked(self):
        params = load_params(); setup_dict = params['CONFIG'][0].get('training_setup', {})
        out_dir = Path('outputs/training')

        def log_to_gui(msg: str):
            try:
                self.log_box.appendPlainText(str(msg))
            except Exception:
                print(str(msg))

        # Mapeo a claves viejas SOLO para el trainer actual (back-compat)
        setup_for_trainer = self._map_new_to_old_for_trainer(setup_dict)
        prep = TrainingPreparer.from_setup_dict(setup_for_trainer, out_dir, logger=log_to_gui)
        try:
            prep.validate()
            prep.prepare_workspace()
            ref_dump = prep.generate_perfect_dump()  # opcional
            csv = prep.build_dataset_csv([ref_dump])  # reemplazá con tus dumps reales
            QMessageBox.information(self, "OK", f"Dataset generado:\n{csv}")
        except Exception as e:
            QMessageBox.critical(self, "Error en preparación", str(e))

    def _map_new_to_old_for_trainer(self, setup_dict: dict) -> dict:
        """Traduce nuevas claves (surface_area/cluster_size/...) a las viejas
        (coordination/steinhardt/...) para el TrainingPreparer legado.
        No modifica el JSON en disco."""
        s = json.loads(json.dumps(setup_dict))  # copia profunda
        f = s.get('features', {})
        mapped = {}
        if 'surface_area' in f:
            sa = f['surface_area']
            mapped['coordination'] = {'enabled': bool(sa.get('enabled', True)), 'rc': float(sa.get('rc', 2.0))}
        if 'volume' in f:
            v = f['volume']
            mapped['energy_potential'] = {'enabled': bool(v.get('enabled', True))}
        if 'cluster_size' in f:
            cs = f['cluster_size']
            mapped['steinhardt'] = {'enabled': bool(cs.get('enabled', True)), 'radius': float(cs.get('radius', 2.70)), 'orders': dict(cs.get('orders', {}))}
        if 'convex_hull' in f:
            ch = f['convex_hull']
            mapped['convex_hull'] = {'enabled': bool(ch.get('enabled', False)), 'area': bool(ch.get('area', True)), 'volume': bool(ch.get('volume', True))}
        s['features'] = mapped
        return s

    # ===== Preview helpers =====
    def _make_lattice_points(self, lattice: str, a0: float, rx: int, ry: int, rz: int) -> np.ndarray:
        lattice = (lattice or "fcc").strip().lower()
        if lattice not in ("fcc", "bcc"):
            lattice = "fcc"
        if lattice == "fcc":
            basis = np.array([[0.0, 0.0, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]], dtype=float)
        else:
            basis = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]], dtype=float)
        ii, jj, kk = np.mgrid[0:rx, 0:ry, 0:rz]
        cells = np.stack([ii.ravel(), jj.ravel(), kk.ravel()], axis=1).astype(float)
        pos = (cells[:, None, :] + basis[None, :, :]).reshape(-1, 3) * a0
        return pos

    def _draw_box_edges(self, ax2d, Lx, Ly, Lz):
        corners = np.array([[0,0,0],[Lx,0,0],[0,Ly,0],[0,0,Lz],[Lx,Ly,0],[Lx,0,Lz],[0,Ly,Lz],[Lx,Ly,Lz]], dtype=float)
        edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]
        self.preview_plotter.clear()
        for i, j in edges:
            self.preview_plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)
        ax2d.cla()
        for i, j in edges:
            x0, y0 = corners[i][0], corners[i][1]; x1, y1 = corners[j][0], corners[j][1]
            ax2d.plot([x0, x1], [y0, y1], '-', linewidth=1)
        ax2d.set_xlabel("X"); ax2d.set_ylabel("Y"); ax2d.set_aspect("equal", "box"); ax2d.grid(True, linewidth=0.3)

    def update_preview(self):
        try:
            lattice = self.combo_lattice.currentText().strip().lower()
            a0 = float(self.spin_a0.value()); rx = int(self.spin_rx.value()); ry = int(self.spin_ry.value()); rz = int(self.spin_rz.value())
            pts = self._make_lattice_points(lattice, a0, rx, ry, rz)
            n_atoms = int(pts.shape[0]); self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")
            Lx, Ly, Lz = rx*a0, ry*a0, rz*a0
            self._draw_box_edges(self.preview_fig.gca() if self.preview_fig.axes else self.preview_fig.add_subplot(111), Lx, Ly, Lz)
            self.preview_plotter.add_mesh(pv.PolyData(pts), color="black", render_points_as_spheres=True, point_size=6)
            self.preview_plotter.reset_camera(); self.preview_plotter.set_scale(1, 1, 1)
            ax2d = self.preview_fig.axes[0]; ax2d.scatter(pts[:, 0], pts[:, 1], s=6, color="k"); self.preview_canvas.draw()
        except Exception as e:
            self.lbl_atoms.setText(f"Error en preview: {e}")

# =====================
#  Pestaña: Procesado
# =====================

class ProcessingTab(QWidget):
    """
    Pestaña 'Procesado' para configurar el pipeline de inferencia
    sobre una muestra con número de vacancias desconocido.
    Guarda en params['CONFIG'][0]['processing_setup'] con las MISMAS claves nuevas que Training.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.params = load_params(); self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        pr = self.cfg.get('processing_setup', {})

        root = QVBoxLayout(self)

        # ===== Selección de muestra =====
        box_sample = QGroupBox("Muestra a procesar (.dump)"); form_s = QFormLayout(box_sample)
        self.edit_sample = QLineEdit(pr.get('sample_dump', ''))
        btn_browse = QPushButton("Buscar"); btn_browse.clicked.connect(self._browse_dump)
        hb = QHBoxLayout(); hb.addWidget(self.edit_sample, 1); hb.addWidget(btn_browse)
        self.spin_topk = QSpinBox(); self.spin_topk.setRange(1, 10); self.spin_topk.setValue(int(pr.get('top_k', 3)))
        form_s.addRow("Archivo .dump:", hb)
        form_s.addRow("Top-K predicciones:", self.spin_topk)
        root.addWidget(box_sample)

        # ===== Features =====
        box_feat = QGroupBox("Features a calcular en la muestra"); feat_layout = QVBoxLayout(box_feat)
        row_coord = QHBoxLayout(); self.chk_coord = QCheckBox("Surface Area")
        self.spin_rc = QDoubleSpinBox(); self.spin_rc.setRange(0.0, 20.0); self.spin_rc.setDecimals(2); self.spin_rc.setSingleStep(0.01)
        self.spin_rc.setValue(float(pr.get('features', {}).get('surface_area', {}).get('rc', 2.00)))
        row_coord.addWidget(self.chk_coord); row_coord.addStretch(); row_coord.addWidget(QLabel("rc (Å):")); row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)
        self.chk_energy = QCheckBox("Volume"); feat_layout.addWidget(self.chk_energy)
        row_s = QHBoxLayout(); self.chk_steinhardt = QCheckBox("Cluster Size")
        self.spin_qr = QDoubleSpinBox(); self.spin_qr.setRange(0.0,20.0); self.spin_qr.setDecimals(2); self.spin_qr.setSingleStep(0.01)
        self.spin_qr.setValue(float(pr.get('features', {}).get('cluster_size', {}).get('radius', 2.70)))
        row_s.addWidget(self.chk_steinhardt); row_s.addStretch(); row_s.addWidget(QLabel("r (Å):")); row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)
        row_orders = QHBoxLayout(); self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8"); self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12): row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)
        self.chk_hull = QCheckBox("Convex Hull"); row_hull = QHBoxLayout(); self.chk_area = QCheckBox("Área"); self.chk_vol = QCheckBox("Volumen")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol); feat_layout.addWidget(self.chk_hull); feat_layout.addLayout(row_hull)
        root.addWidget(box_feat)

        # ===== Preview de la muestra =====
        box_prev = QGroupBox("Preview de la muestra"); prev_layout = QVBoxLayout(box_prev)
        self.lbl_atoms = QLabel("Átomos totales: -"); prev_layout.addWidget(self.lbl_atoms)
        self.preview_plotter = QtInteractor(box_prev); prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4,4)); self.preview_canvas = FigureCanvas(self.preview_fig); prev_layout.addWidget(self.preview_canvas)
        btn_preview = QPushButton("Cargar preview"); btn_preview.clicked.connect(self.update_preview_from_dump); prev_layout.addWidget(btn_preview)
        root.addWidget(box_prev)

        # ===== Botones =====
        row_btns = QHBoxLayout(); btn_save = QPushButton("Guardar configuración"); btn_load = QPushButton("Cargar configuración actual"); btn_process = QPushButton("Procesar muestra")
        btn_save.clicked.connect(self.save_processing_setup); btn_load.clicked.connect(self.load_from_params); btn_process.clicked.connect(self._process_stub)
        row_btns.addWidget(btn_save); row_btns.addWidget(btn_load); row_btns.addWidget(btn_process); root.addLayout(row_btns)

        # Log
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMinimumHeight(120); root.addWidget(self.log_box); root.addStretch()

        # Estados iniciales de checks
        self.chk_coord.setChecked(pr.get('features', {}).get('surface_area', {}).get('enabled', True))
        self.chk_energy.setChecked(pr.get('features', {}).get('volume', {}).get('enabled', True))
        st = pr.get('features', {}).get('cluster_size', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True)); self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False)); self.chk_Q10.setChecked(orders.get('Q10', False)); self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = pr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False)); self.chk_area.setChecked(hull.get('area', True)); self.chk_vol.setChecked(hull.get('volume', True))

        # Habilitar subopciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled); self.spin_rc.setEnabled(self.chk_coord.isChecked())
        def _en_steinhardt(on: bool):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12): w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt); _en_steinhardt(self.chk_steinhardt.isChecked())
        def _en_hull(on: bool):
            for w in (self.chk_area, self.chk_vol): w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull); _en_hull(self.chk_hull.isChecked())

    # ---------- Acciones ----------
    def _browse_dump(self):
        filtros = "All Files (*);;Dump Files (*.dump)"; start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar muestra", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent); self.edit_sample.setText(abs_path)

    def save_processing_setup(self):
        params = load_params(); cfg = params.setdefault('CONFIG', [{}])[0]
        setup = {
            'sample_dump': self.edit_sample.text().strip(),
            'top_k': int(self.spin_topk.value()),
            'features': {
                'surface_area': {'enabled': self.chk_coord.isChecked(), 'rc': float(self.spin_rc.value())},
                'volume': {'enabled': self.chk_energy.isChecked()},
                'cluster_size': {
                    'enabled': self.chk_steinhardt.isChecked(),
                    'radius': float(self.spin_qr.value()),
                    'orders': {
                        'Q4': self.chk_Q4.isChecked(), 'Q6': self.chk_Q6.isChecked(),
                        'Q8': self.chk_Q8.isChecked(), 'Q10': self.chk_Q10.isChecked(),
                        'Q12': self.chk_Q12.isChecked()
                    }
                },
                'convex_hull': {'enabled': self.chk_hull.isChecked(), 'area': self.chk_area.isChecked(), 'volume': self.chk_vol.isChecked()},
            }
        }
        cfg['processing_setup'] = setup
        path = save_params(params)
        QMessageBox.information(self, "Procesado guardado", f"Se guardó processing_setup en:\n{path}")

    def load_from_params(self):
        self.__init__(self.parent)

    def update_preview_from_dump(self):
        p = self.edit_sample.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Elegí primero un .dump de muestra.")
            return
        try:
            pipeline = import_file(p); data = pipeline.compute(); n_atoms = int(data.particles.count)
            self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")
            render_dump_to(self.preview_plotter, self.preview_fig, p)
            self.preview_canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error en preview", str(e))

    def _process_stub(self):
        self.log_box.appendPlainText("Procesado: stub ejecutado. Conectar modelo + extracción de features + predicción.")
        QMessageBox.information(self, "Procesar muestra", "Stub de procesado ejecutado. Falta conectar lógica real.")

# =====================
#  Ventana principal
# =====================

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VacancyFinder-SiMAF – Training / Procesado")
        self.resize(1280, 800)
        tabs = QTabWidget()
        self.training_tab = TrainingTab(self); tabs.addTab(self.training_tab, "Training")
        self.processing_tab = ProcessingTab(self); tabs.addTab(self.processing_tab, "Procesado")
        self.setCentralWidget(tabs)

# =====================
#  Entry point
# =====================

def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
