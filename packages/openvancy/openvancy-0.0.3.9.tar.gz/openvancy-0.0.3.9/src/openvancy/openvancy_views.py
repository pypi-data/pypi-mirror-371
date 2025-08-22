import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget,QGroupBox  
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from openvancy.training.preparer import *

# ---------- Gestión de input_params.json ----------
GUI_ROOT = Path(__file__).resolve().parent

def runtime_params_path():
    cwd_params = Path.cwd() / "input_params.json"
    if cwd_params.exists():
        return cwd_params
    src_params = GUI_ROOT / "input_params.json"
    if src_params.exists():
        shutil.copy(src_params, cwd_params)
        return cwd_params
    return src_params

PARAMS_FILE = runtime_params_path()

def load_params():
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}

def save_params(params, target_path: Path = None):
    if target_path is None:
        target_path = Path.cwd() / "input_params.json"
    target_path.write_text(json.dumps(params, indent=4))
    return target_path


# ---------- Función común de render (3D+2D) ----------
def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    """Dibuja celda + puntos igual que load_dump, coloreando por 'Cluster' si existe."""
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    # === Celda desde OVITO: columnas a1,a2,a3 y última columna origen ===
    M = np.asarray(data.cell.matrix, dtype=float)   # (3x4)
    a1, a2, a3, origin = M[:, 0], M[:, 1], M[:, 2], M[:, 3]

    corners = [
        origin,
        origin + a1,
        origin + a2,
        origin + a3,
        origin + a1 + a2,
        origin + a1 + a3,
        origin + a2 + a3,
        origin + a1 + a2 + a3
    ]
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

    # === Partículas ===
    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    # --- Detectar columna de clúster (varios alias posibles) ---
    cluster_vals = None
    for name in ("Cluster", "cluster", "c_Cluster", "c_cluster", "ClusterID", "cluster_id"):
        if name in data.particles:
            prop = data.particles[name]
            arr = prop.array if hasattr(prop, "array") else prop
            cluster_vals = np.asarray(arr).astype(int).reshape(-1)
            break

    # --- Remapeo a 0..K-1 para paleta discreta ---
    cluster_idx = None
    unique_clusters = None
    if cluster_vals is not None and cluster_vals.shape[0] == positions.shape[0]:
        unique_clusters = np.unique(cluster_vals)
        map_idx = {val: i for i, val in enumerate(unique_clusters)}
        # vectorizado seguro
        cluster_idx = np.vectorize(map_idx.get, otypes=[int])(cluster_vals)

    # === Vista 3D ===
    plotter.clear()
    for i, j in edges:
        plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

    if cluster_idx is not None:
        pts = pv.PolyData(positions)
        pts["cluster"] = cluster_idx
        plotter.add_mesh(
            pts,
            scalars="cluster",
            render_points_as_spheres=True,
            point_size=8,
            cmap="tab20",
            show_scalar_bar=False,   # oculto barra para muchos clústeres
        )
    else:
        plotter.add_mesh(
            pv.PolyData(positions),
            color="black",
            render_points_as_spheres=True,
            point_size=8
        )

    plotter.reset_camera()
    plotter.set_scale(1, 1, 1)

    # === Vista 2D ===
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)

    if cluster_idx is not None:
        # Paleta consistente con PyVista
        ax.scatter(
            positions[:, 0], positions[:, 1], s=10,
            c=cluster_idx, cmap="tab20",
            vmin=0, vmax=len(unique_clusters)-1
        )
    else:
        ax.scatter(positions[:, 0], positions[:, 1], s=10, color="k")

    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box')
    ax.grid(True, linewidth=0.3)
    fig.canvas.draw()


# ---------- Widgets de viewers internos ----------
class DumpViewerWidget(QWidget):
    """Viewer genérico: igual que load_dump, con selector de archivo."""
    def __init__(self, parent=None):
        super().__init__(parent)
        top = QWidget()
        top_l = QHBoxLayout(top)
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_load = QPushButton("Load")
        top_l.addWidget(QLabel("File:"))
        top_l.addWidget(self.path_edit, 1)
        top_l.addWidget(self.btn_browse)
        top_l.addWidget(self.btn_load)

        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_browse.clicked.connect(self._browse)
        self.btn_load.clicked.connect(self._load_clicked)

    def _browse(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.path_edit.setText(abs_path)

    def _load_clicked(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Seleccione un archivo primero.")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def render_dump(self, p: str):
        self.path_edit.setText(p)
        render_dump_to(self.plotter, self.fig, p)


class KeyAreaSeqWidget(QWidget):
    """Viewer para outputs/dump/key_area_{i}.dump con controles de índice."""
    def __init__(self, parent=None, pattern: str = "outputs/dump/key_area_{i}.dump"):
        super().__init__(parent)
        self.pattern = pattern

        top = QWidget()
        top_l = QHBoxLayout(top)
        self.idx = QSpinBox()
        self.idx.setRange(0, 1_000_000)
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        self.btn_load = QPushButton("Load")
        self.path_lbl = QLineEdit()
        self.path_lbl.setReadOnly(True)

        top_l.addWidget(QLabel("key_area_{i}.dump   i="))
        top_l.addWidget(self.idx)
        top_l.addWidget(self.btn_prev)
        top_l.addWidget(self.btn_next)
        top_l.addWidget(self.btn_load)
        top_l.addWidget(QLabel("Archivo:"))
        top_l.addWidget(self.path_lbl, 1)

        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_prev.clicked.connect(lambda: self._step(-1))
        self.btn_next.clicked.connect(lambda: self._step(+1))
        self.btn_load.clicked.connect(self._load_idx)

        self._auto_seed_index()

    def _pattern_path(self, i: int) -> str:
        return self.pattern.format(i=i)

    def _auto_seed_index(self):
        for i in range(0, 10000):
            if Path(self._pattern_path(i)).exists():
                self.idx.setValue(i)
                self._load_idx()
                return
        self.path_lbl.setText("(no encontrado)")

    def _step(self, delta: int):
        new_i = max(0, self.idx.value() + delta)
        self.idx.setValue(new_i)
        self._load_idx()

    def _load_idx(self):
        p = self._pattern_path(self.idx.value())
        self.path_lbl.setText(p)
        if not Path(p).exists():
            QMessageBox.warning(self, "No existe", f"No se encontró:\n{p}")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))




class TrainingTab(QWidget):
    """
    Pestaña 'Training' para configurar generación de red perfecta y features.
    Guarda en params['CONFIG'][0]['training_setup'].
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Cargar params actuales
        self.params = load_params()
        self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        tr = self.cfg.get('training_setup', {})

        root = QVBoxLayout(self)

        # ===== Sección: Red perfecta de entrenamiento =====
        box_net = QGroupBox("Red perfecta de entrenamiento (.dump)")
        form_net = QFormLayout(box_net)

        self.combo_lattice = QComboBox()
        self.combo_lattice.addItems(["fcc", "bcc"])
        self.combo_lattice.setCurrentText(tr.get('perfect_network', {}).get('lattice', "fcc"))

        self.spin_a0 = QDoubleSpinBox()
        self._cfg_spin(self.spin_a0, 0.0, 50.0, float(tr.get('perfect_network', {}).get('a0', 3.52)), step=0.01, decimals=3)

        cells_def = tr.get('perfect_network', {}).get('cells', [1, 1, 1])
        self.spin_rx = QSpinBox(); self._cfg_spin(self.spin_rx, 1, 500, int(cells_def[0]))
        self.spin_ry = QSpinBox(); self._cfg_spin(self.spin_ry, 1, 500, int(cells_def[1]))
        self.spin_rz = QSpinBox(); self._cfg_spin(self.spin_rz, 1, 500, int(cells_def[2]))

        self.edit_atom = QLineEdit(tr.get('perfect_network', {}).get('atom', "Fe"))

        btn_gen = QPushButton("Generar red perfecta")
        btn_gen.clicked.connect(self._generate_stub)

        form_net.addRow("Lattice:", self.combo_lattice)
        form_net.addRow("a₀ (Å):", self.spin_a0)
        form_net.addRow("Réplicas X:", self.spin_rx)
        form_net.addRow("Réplicas Y:", self.spin_ry)
        form_net.addRow("Réplicas Z:", self.spin_rz)
        form_net.addRow("Elemento:", self.edit_atom)
        form_net.addRow(btn_gen)

        root.addWidget(box_net)

        # ===== Sección: Configuración de entrenamiento =====
        box_train = QGroupBox("Configuraciones de entrenamiento")
        form_train = QFormLayout(box_train)

        self.spin_iters = QSpinBox()
        self._cfg_spin(self.spin_iters, 1, 1_000_000, int(tr.get('iterations', 1000)))

        self.spin_max_vacs = QSpinBox()
        self._cfg_spin(self.spin_max_vacs, 0, 1_000_000, int(tr.get('max_vacancies', 0)))

        form_train.addRow("Iteraciones:", self.spin_iters)
        form_train.addRow("Vacancias máximas a retirar:", self.spin_max_vacs)
        root.addWidget(box_train)

        # ===== Sección: Features =====
        box_feat = QGroupBox("Features a extraer")
        feat_layout = QVBoxLayout(box_feat)

        # Coordinación (rc)
        row_coord = QHBoxLayout()
        self.chk_coord = QCheckBox("surface area")
        self.spin_rc = QDoubleSpinBox()
        self._cfg_spin(self.spin_rc, 0.0, 20.0,
                       float(tr.get('features', {}).get('surface area', {}).get('radius', 2)),
                       step=0.01, decimals=2)
        row_coord.addWidget(self.chk_coord)
        row_coord.addStretch()
        row_coord.addWidget(QLabel("rc (Å):"))
        row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Energía potencial
        self.chk_energy = QCheckBox("volume")
        feat_layout.addWidget(self.chk_energy)

        # Steinhardt Q_l
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("cluster Size")
        self.spin_qr = QDoubleSpinBox()
        self._cfg_spin(self.spin_qr, 0.0, 20.0,
                       float(tr.get('features', {}).get('cluster size', {}).get('radius', 2.70)),
                       step=0.01, decimals=2)
        row_s.addWidget(self.chk_steinhardt)
        row_s.addStretch()
        row_s.addWidget(QLabel("r (Å):"))
        row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)

        row_orders = QHBoxLayout()
        self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8")
        self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
            row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)

        # Casco convexo
        self.chk_hull = QCheckBox("Casco convexo")
        row_hull = QHBoxLayout()
        self.chk_area = QCheckBox("Área"); self.chk_vol = QCheckBox("Volumen")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol)
        feat_layout.addWidget(self.chk_hull)
        feat_layout.addLayout(row_hull)

        root.addWidget(box_feat)
        # ===== Preview de red =====
        box_prev = QGroupBox("Preview de red")
        prev_layout = QVBoxLayout(box_prev)

        # Etiqueta con el total de átomos
        self.lbl_atoms = QLabel("Átomos totales: -")
        prev_layout.addWidget(self.lbl_atoms)

        # Vistas 3D y 2D
        self.preview_plotter = QtInteractor(box_prev)
        prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4, 4))
        self.preview_canvas = FigureCanvas(self.preview_fig)
        prev_layout.addWidget(self.preview_canvas)

        root.addWidget(box_prev)

        # === Señales para refrescar preview y contador ===
        self.combo_lattice.currentTextChanged.connect(self.update_preview)
        self.spin_a0.valueChanged.connect(self.update_preview)
        self.spin_rx.valueChanged.connect(self.update_preview)
        self.spin_ry.valueChanged.connect(self.update_preview)
        self.spin_rz.valueChanged.connect(self.update_preview)

        # Render inicial del preview
        self.update_preview()


        # ===== Botones guardar/cargar =====
        row_btns = QHBoxLayout()
        btn_save = QPushButton("Guardar configuración")
        btn_load = QPushButton("Cargar configuración actual")
        btn_prepare = QPushButton("Preparar dataset")  # ⬅️ nuevo
        btn_save.clicked.connect(self.save_training_setup)
        btn_load.clicked.connect(self.load_from_params)
        btn_prepare.clicked.connect(self.on_prepare_training_clicked)  # ⬅️ nuevo
        row_btns.addWidget(btn_save)
        row_btns.addWidget(btn_load)
        row_btns.addWidget(btn_prepare)  # ⬅️ nuevo
        root.addLayout(row_btns)

        # ===== Estados iniciales de checks =====
        self.chk_coord.setChecked(tr.get('features', {}).get('surface area', {}).get('enabled', True))
        self.chk_energy.setChecked(tr.get('features', {}).get('volume', {}).get('enabled', True))
        st = tr.get('features', {}).get('cluster size', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True))
        self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False))
        self.chk_Q10.setChecked(orders.get('Q10', False))
        self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = tr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False))
        self.chk_area.setChecked(hull.get('area', True))
        self.chk_vol.setChecked(hull.get('volumee', True))
        # Log local de la pestaña (debajo de los botones)
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(120)
        root.addWidget(self.log_box)

        # Habilitar/deshabilitar sub-opciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled)
        self.spin_rc.setEnabled(self.chk_coord.isChecked())

        def _en_steinhardt(on):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
                w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt)
        _en_steinhardt(self.chk_steinhardt.isChecked())

        def _en_hull(on):
            for w in (self.chk_area, self.chk_vol):
                w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull)
        _en_hull(self.chk_hull.isChecked())

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

    # ===== Acciones =====
    def save_training_setup(self):
        params = load_params()
        cfg = params.setdefault('CONFIG', [{}])[0]
        setup = {
            'iterations': int(self.spin_iters.value()),
            'max_vacancies': int(self.spin_max_vacs.value()),
            'features': {
                'surface area': {'enabled': self.chk_coord.isChecked(), 'rc': float(self.spin_rc.value())},
                'volume': {'enabled': self.chk_energy.isChecked()},
                'cluster size': {
                    'enabled': self.chk_steinhardt.isChecked(),
                    'radius': float(self.spin_qr.value()),
                    'orders': {
                        'Q4': self.chk_Q4.isChecked(), 'Q6': self.chk_Q6.isChecked(),
                        'Q8': self.chk_Q8.isChecked(), 'Q10': self.chk_Q10.isChecked(),
                        'Q12': self.chk_Q12.isChecked()
                    }
                },
                'convex_hull': {'enabled': self.chk_hull.isChecked(),
                                'area': self.chk_area.isChecked(),
                                'volumee': self.chk_vol.isChecked()},
            },
            'perfect_network': {
                'lattice': self.combo_lattice.currentText(),
                'a0': float(self.spin_a0.value()),
                'cells': [int(self.spin_rx.value()), int(self.spin_ry.value()), int(self.spin_rz.value())],
                'atom': self.edit_atom.text().strip() or "Fe",
            }
        }
        cfg['training_setup'] = setup
        path = save_params(params)
        QMessageBox.information(self, "Training guardado",
                                f"Se guardó training_setup en:\n{path}")

    def load_from_params(self):
        # Recarga simple (si cambió el JSON fuera de la pestaña)
        self.__init__(self.parent)

    def _generate_stub(self):
        # Por ahora solo fuerza un refresh visual.
        self.update_preview()
        QMessageBox.information(
            self, "Generar red perfecta",
            "Preview actualizado con los parámetros actuales. Conectar aquí tu lógica de exportar .dump cuando lo tengas."
        )


    def on_prepare_training_clicked(self):
        params = load_params()
        setup_dict = params['CONFIG'][0]['training_setup']
        out_dir = Path('outputs/training')

        def log_to_gui(msg: str):
            try:
                self.log_box.appendPlainText(str(msg))
            except Exception:
                print(str(msg))

        prep = TrainingPreparer.from_setup_dict(setup_dict, out_dir, logger=log_to_gui)
        try:
            prep.validate()
            prep.prepare_workspace()
            ref_dump = prep.generate_perfect_dump()  # opcional
            csv = prep.build_dataset_csv([ref_dump])  # reemplazá con tus dumps reales
            QMessageBox.information(self, "OK", f"Dataset generado:\n{csv}")
        except Exception as e:
            QMessageBox.critical(self, "Error en preparación", str(e))

    # ======== PREVIEW: generación de red y render ========
    def _make_lattice_points(self, lattice: str, a0: float, rx: int, ry: int, rz: int) -> np.ndarray:
        """
        Genera posiciones (N,3) para una red cúbica convencional replicada.
        - lattice: 'fcc' o 'bcc'
        - a0: parámetro de red (Å)
        - rx, ry, rz: réplicas en cada eje
        """
        lattice = (lattice or "fcc").strip().lower()
        if lattice not in ("fcc", "bcc"):
            lattice = "fcc"

        # Bases fraccionarias en la celda cúbica convencional
        if lattice == "fcc":
            basis = np.array([
                [0.0, 0.0, 0.0],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.5],
                [0.5, 0.5, 0.0],
            ], dtype=float)
        else:  # bcc
            basis = np.array([
                [0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5],
            ], dtype=float)

        # Grid de réplicas
        ii, jj, kk = np.mgrid[0:rx, 0:ry, 0:rz]
        cells = np.stack([ii.ravel(), jj.ravel(), kk.ravel()], axis=1).astype(float)  # (rx*ry*rz, 3)

        # Posiciones: (n_cells,1,3) + (1,n_basis,3)  -> broadcast -> (n_cells,n_basis,3)
        pos = cells[:, None, :] + basis[None, :, :]
        pos = pos.reshape(-1, 3) * a0
        return pos

    def _draw_box_edges(self, ax2d, Lx, Ly, Lz):
        # Esquinas del paralelepípedo (cubo replicado)
        corners = np.array([
            [0, 0, 0],
            [Lx, 0, 0],
            [0, Ly, 0],
            [0, 0, Lz],
            [Lx, Ly, 0],
            [Lx, 0, Lz],
            [0, Ly, Lz],
            [Lx, Ly, Lz]
        ], dtype=float)
        edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

        # 3D (PyVista)
        self.preview_plotter.clear()
        for i, j in edges:
            self.preview_plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

        # 2D (Matplotlib)
        ax2d.cla()
        for i, j in edges:
            x0, y0 = corners[i][0], corners[i][1]
            x1, y1 = corners[j][0], corners[j][1]
            ax2d.plot([x0, x1], [y0, y1], '-', linewidth=1)

        ax2d.set_xlabel("X"); ax2d.set_ylabel("Y")
        ax2d.set_aspect("equal", "box"); ax2d.grid(True, linewidth=0.3)

    def update_preview(self):
        """
        Recalcula posiciones según parámetros actuales y refresca:
        - Conteo de átomos totales
        - Vista 3D (PyVista) y 2D (Matplotlib)
        """
        try:
            lattice = self.combo_lattice.currentText().strip().lower()
            a0 = float(self.spin_a0.value())
            rx = int(self.spin_rx.value())
            ry = int(self.spin_ry.value())
            rz = int(self.spin_rz.value())

            # Generar posiciones
            pts = self._make_lattice_points(lattice, a0, rx, ry, rz)
            n_atoms = int(pts.shape[0])
            self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")

            # Tamaños de caja
            Lx, Ly, Lz = rx * a0, ry * a0, rz * a0

            # 3D
            self.preview_plotter.clear()
            # Caja
            self._draw_box_edges(self.preview_fig.gca() if self.preview_fig.axes else self.preview_fig.add_subplot(111),
                                 Lx, Ly, Lz)  # esto además resetea 2D
            # Puntos 3D
            self.preview_plotter.add_mesh(
                pv.PolyData(pts),
                color="black",
                render_points_as_spheres=True,
                point_size=6
            )
            self.preview_plotter.reset_camera()
            self.preview_plotter.set_scale(1, 1, 1)

            # 2D XY (sobre la figura que ya reseteamos dentro de _draw_box_edges)
            ax2d = self.preview_fig.axes[0]
            ax2d.scatter(pts[:, 0], pts[:, 1], s=6, color="k")
            self.preview_canvas.draw()

        except Exception as e:
            # Si algo falla, no rompemos la UI: mostramos el error en el label
            self.lbl_atoms.setText(f"Error en preview: {e}")





















class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VacancyFinder-SiMAF – Training / Procesado")
        self.resize(1280, 800)

        # Pestañas principales: Training y Procesado
        tabs = QTabWidget()

        # Ventana Training (ya la tenés)
        self.training_tab = TrainingTab(self)
        tabs.addTab(self.training_tab, "Training")

        # Nueva ventana: Procesado (muestra con #vacancias desconocido)
        self.processing_tab = ProcessingTab(self)
        tabs.addTab(self.processing_tab, "Procesado")

        self.setCentralWidget(tabs)

    
class ProcessingTab(QWidget):
    """
    Pestaña 'Procesado' para configurar el pipeline de inferencia
    sobre una muestra con número de vacancias desconocido.
    Guarda en params['CONFIG'][0]['processing_setup'].
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.params = load_params()
        self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        pr = self.cfg.get('processing_setup', {})

        root = QVBoxLayout(self)

        # ===== Selección de muestra =====
        box_sample = QGroupBox("Muestra a procesar (.dump)")
        form_s = QFormLayout(box_sample)

        self.edit_sample = QLineEdit(pr.get('sample_dump', ''))
        btn_browse = QPushButton("Buscar")
        btn_browse.clicked.connect(self._browse_dump)
        hb = QHBoxLayout(); hb.addWidget(self.edit_sample, 1); hb.addWidget(btn_browse)

        self.spin_topk = QSpinBox()
        self.spin_topk.setRange(1, 10)
        self.spin_topk.setValue(int(pr.get('top_k', 3)))

        form_s.addRow("Archivo .dump:", hb)  # QFormLayout acepta layouts directamente

        form_s.addRow("Top-K predicciones:", self.spin_topk)
        root.addWidget(box_sample)

        # ===== Features (igual que en Training, para garantizar consistencia) =====
        box_feat = QGroupBox("Features a calcular en la muestra")
        feat_layout = QVBoxLayout(box_feat)

        # Coordinación
        row_coord = QHBoxLayout()
        self.chk_coord = QCheckBox("surface area")
        self.spin_rc = QDoubleSpinBox()
        self.spin_rc.setRange(0.0, 20.0)
        self.spin_rc.setDecimals(2)
        self.spin_rc.setSingleStep(0.01)
        self.spin_rc.setValue(float(pr.get('features', {}).get('surface area', {}).get('radius', 2.00)))
        row_coord.addWidget(self.chk_coord)
        row_coord.addStretch()
        row_coord.addWidget(QLabel("rc (Å):"))
        row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Energía potencial
        self.chk_energy = QCheckBox("volume")
        feat_layout.addWidget(self.chk_energy)

        # Steinhardt
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("cluster size")
        self.spin_qr = QDoubleSpinBox(); self.spin_qr.setRange(0.0,20.0); self.spin_qr.setDecimals(2); self.spin_qr.setSingleStep(0.01)
        self.spin_qr.setValue(float(pr.get('features', {}).get('cluster size', {}).get('radius', 2.70)))
        row_s.addWidget(self.chk_steinhardt); row_s.addStretch(); row_s.addWidget(QLabel("rc (Å):")); row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)

        row_orders = QHBoxLayout()
        self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8"); self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
            row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)

        # Casco convexo
        self.chk_hull = QCheckBox("Casco convexo")
        row_hull = QHBoxLayout()
        self.chk_area = QCheckBox("Áreass"); self.chk_vol = QCheckBox("Volumenss")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol)
        feat_layout.addWidget(self.chk_hull); feat_layout.addLayout(row_hull)

        root.addWidget(box_feat)

        # ===== Preview de la muestra =====
        box_prev = QGroupBox("Preview de la muestra")
        prev_layout = QVBoxLayout(box_prev)
        self.lbl_atoms = QLabel("Átomos totales: -")
        prev_layout.addWidget(self.lbl_atoms)
        self.preview_plotter = QtInteractor(box_prev); prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4,4)); self.preview_canvas = FigureCanvas(self.preview_fig); prev_layout.addWidget(self.preview_canvas)
        btn_preview = QPushButton("Cargar preview")
        btn_preview.clicked.connect(self.update_preview_from_dump)
        prev_layout.addWidget(btn_preview)
        root.addWidget(box_prev)

        # ===== Botones =====
        row_btns = QHBoxLayout()
        btn_save = QPushButton("Guardar configuración")
        btn_load = QPushButton("Cargar configuración actual")
        btn_process = QPushButton("Procesar muestra")
        btn_save.clicked.connect(self.save_processing_setup)
        btn_load.clicked.connect(self.load_from_params)
        btn_process.clicked.connect(self._process_stub)  # stub
        row_btns.addWidget(btn_save); row_btns.addWidget(btn_load); row_btns.addWidget(btn_process)
        root.addLayout(row_btns)

        # Log local
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMinimumHeight(120)
        root.addWidget(self.log_box)
        root.addStretch()

        # Estados iniciales de checks
        self.chk_coord.setChecked(pr.get('features', {}).get('surface area', {}).get('enabled', True))
        self.chk_energy.setChecked(pr.get('features', {}).get('volume', {}).get('enabled', True))
        st = pr.get('features', {}).get('cluster size', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True))
        self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False))
        self.chk_Q10.setChecked(orders.get('Q10', False))
        self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = pr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False))
        self.chk_area.setChecked(hull.get('areas', True))
        self.chk_vol.setChecked(hull.get('volumes', True))

        # Habilitar subopciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled)
        self.spin_rc.setEnabled(self.chk_coord.isChecked())

        def _en_steinhardt(on):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
                w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt); _en_steinhardt(self.chk_steinhardt.isChecked())

        def _en_hull(on):
            for w in (self.chk_area, self.chk_vol):
                w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull); _en_hull(self.chk_hull.isChecked())

    # ---------- Acciones ----------
    def _wrap(self, w):
        box = QWidget(); l = QHBoxLayout(box); l.setContentsMargins(0,0,0,0); l.addWidget(w); return box

    def _browse_dump(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar muestra", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.edit_sample.setText(abs_path)

    def save_processing_setup(self):
        params = load_params()
        cfg = params.setdefault('CONFIG', [{}])[0]
        setup = {
            'sample_dump': self.edit_sample.text().strip(),
            'top_k': int(self.spin_topk.value()),
            'features': {
                'surface area': {'enabled': self.chk_coord.isChecked(), 'rc': float(self.spin_rc.value())},
                'volume': {'enabled': self.chk_energy.isChecked()},
                'cluster size': {
                    'enabled': self.chk_steinhardt.isChecked(),
                    'radius': float(self.spin_qr.value()),
                    'orders': {
                        'Q4': self.chk_Q4.isChecked(), 'Q6': self.chk_Q6.isChecked(),
                        'Q8': self.chk_Q8.isChecked(), 'Q10': self.chk_Q10.isChecked(),
                        'Q12': self.chk_Q12.isChecked()
                    }
                },
                'convex_hull': {'enabled': self.chk_hull.isChecked(),
                                'area': self.chk_area.isChecked(),
                                'volumee': self.chk_vol.isChecked()},
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
            # Render 3D/2D + conteo de átomos
            pipeline = import_file(p)
            data = pipeline.compute()
            n_atoms = int(data.particles.count)
            self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")
            # Render con tu función común
            render_dump_to(self.preview_plotter, self.preview_fig, p)
            self.preview_canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error en preview", str(e))

    def _process_stub(self):
        # Aquí conectarás tu pipeline real de inferencia.
        # Por ahora, solo deja registro y un aviso.
        self.log_box.appendPlainText("Procesado: stub ejecutado. Conectar modelo + extracción de features + predicción.")
        QMessageBox.information(self, "Procesar muestra", "Stub de procesado ejecutado. Falta conectar lógica real.")

def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
