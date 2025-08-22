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
from vfscript import vfs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from vfscript.training.preparer import *

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
        self.chk_coord = QCheckBox("Coordinación")
        self.spin_rc = QDoubleSpinBox()
        self._cfg_spin(self.spin_rc, 0.0, 20.0,
                       float(tr.get('features', {}).get('coordination', {}).get('rc', 3.25)),
                       step=0.01, decimals=2)
        row_coord.addWidget(self.chk_coord)
        row_coord.addStretch()
        row_coord.addWidget(QLabel("rc (Å):"))
        row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Energía potencial
        self.chk_energy = QCheckBox("Energía potencial por átomo")
        feat_layout.addWidget(self.chk_energy)

        # Steinhardt Q_l
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("Steinhardt Q_l")
        self.spin_qr = QDoubleSpinBox()
        self._cfg_spin(self.spin_qr, 0.0, 20.0,
                       float(tr.get('features', {}).get('steinhardt', {}).get('radius', 2.70)),
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
        btn_save.clicked.connect(self.save_training_setup)
        btn_load.clicked.connect(self.load_from_params)
        row_btns.addWidget(btn_save); row_btns.addWidget(btn_load)
        root.addLayout(row_btns)
        root.addStretch()

        # ===== Estados iniciales de checks =====
        self.chk_coord.setChecked(tr.get('features', {}).get('coordination', {}).get('enabled', True))
        self.chk_energy.setChecked(tr.get('features', {}).get('energy_potential', {}).get('enabled', True))
        st = tr.get('features', {}).get('steinhardt', {})
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
        self.chk_vol.setChecked(hull.get('volume', True))

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
                'coordination': {'enabled': self.chk_coord.isChecked(), 'rc': float(self.spin_rc.value())},
                'energy_potential': {'enabled': self.chk_energy.isChecked()},
                'steinhardt': {
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
                                'volume': self.chk_vol.isChecked()},
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
            # si tenés un QTextEdit de log:
            self.log_output.appendPlainText(str(msg))

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





















# ---------- Ventana principal ----------
class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("VacancyFinder-SiMAF   0.5.0.1")

        self.params = load_params()
        cfg = self.params.setdefault('CONFIG', [{}])[0]

        form_layout = QFormLayout()

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        form_layout.addRow("Progreso:", self.progress)

        # Log de salida (grande)
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow("Output Log:", self.log_output)

        # Checkboxes
        self.check_training = QCheckBox(); self.check_training.setChecked(cfg.get('training', False))
        self.check_geometric = QCheckBox(); self.check_geometric.setChecked(cfg.get('geometric_method', False))
        self.check_activate_relax = QCheckBox(); self.check_activate_relax.setChecked(cfg.get('activate_generate_relax', False))
        form_layout.addRow("Enable Training:", self.check_training)
        form_layout.addRow("Geometric Method:", self.check_geometric)
        form_layout.addRow("Activate Generate Relax:", self.check_activate_relax)

        # generate_relax
        gr = cfg.get('generate_relax', ["bcc", 1.0]) + [1, 1, 1, "Fe"]
        self.edit_lattice = QLineEdit(gr[0])
        self.spin_lattice_a = QDoubleSpinBox()
        self._configure_spin(self.spin_lattice_a, 0.0, 100.0, float(gr[1]), step=0.1, decimals=3)
        self.spin_rx = QSpinBox(); self._configure_spin(self.spin_rx, 1, 100, gr[2], step=1)
        self.spin_ry = QSpinBox(); self._configure_spin(self.spin_ry, 1, 100, gr[3], step=1)
        self.spin_rz = QSpinBox(); self._configure_spin(self.spin_rz, 1, 100, gr[4], step=1)
        self.edit_atom = QLineEdit(gr[5])

        form_layout.addRow("Lattice Type:", self.edit_lattice)
        form_layout.addRow("Lattice Param a:", self.spin_lattice_a)
        form_layout.addRow("Replicas X:", self.spin_rx)
        form_layout.addRow("Replicas Y:", self.spin_ry)
        form_layout.addRow("Replicas Z:", self.spin_rz)
        form_layout.addRow("Atom Type:", self.edit_atom)

        # Selectores de dump
        self.edit_relax = QLineEdit(cfg.get('relax', ''))
        btn_relax = QPushButton("Browse Relax")
        btn_relax.clicked.connect(lambda: self.browse_file(self.edit_relax))
        relax_layout = QHBoxLayout(); relax_layout.addWidget(self.edit_relax); relax_layout.addWidget(btn_relax)
        form_layout.addRow("Relax Dump:", self._wrap(relax_layout))

        self.edit_defect = QLineEdit(cfg.get('defect', [''])[0])
        btn_defect = QPushButton("Browse Defect")
        btn_defect.clicked.connect(lambda: self.browse_file(self.edit_defect))
        defect_layout = QHBoxLayout(); defect_layout.addWidget(self.edit_defect); defect_layout.addWidget(btn_defect)
        form_layout.addRow("Defect Dump:", self._wrap(defect_layout))

        # CSV
        self.csv_combo = QComboBox(); self.csv_combo.setEditable(True)
        self._refresh_csv_list()
        form_layout.addRow("Resultados CSV:", self.csv_combo)
        btn_csv = QPushButton("Cargar CSV"); btn_csv.clicked.connect(self.load_csv_results)
        form_layout.addRow(btn_csv)

        # Campos numéricos
        fields = [
            ("radius", QDoubleSpinBox, 0, 100, cfg.get('radius', 0.0), 3),
            ("cutoff", QDoubleSpinBox, 0, 100, cfg.get('cutoff', 0.0), 3),
            ("max_graph_size", QSpinBox, 0, 10000, cfg.get('max_graph_size', 0), 0),
            ("max_graph_variations", QSpinBox, 0, 10000, cfg.get('max_graph_variations', 0), 0),
            ("radius_training", QDoubleSpinBox, 0, 100, cfg.get('radius_training', 0.0), 3),
            ("training_file_index", QSpinBox, 0, 10000, cfg.get('training_file_index', 0), 0),
            ("cluster tolerance", QDoubleSpinBox, 0, 100, cfg.get('cluster tolerance', 0.0), 3),
            ("divisions_of_cluster", QSpinBox, 0, 10000, cfg.get('divisions_of_cluster', 0), 0),
            ("iteraciones_clusterig", QSpinBox, 0, 10000, cfg.get('iteraciones_clusterig', 0), 0),
        ]
        for name, cls, mn, mx, val, dec in fields:
            widget = cls()
            step = 0.1 if cls is QDoubleSpinBox else 1
            decimals = dec if cls is QDoubleSpinBox else None
            self._configure_spin(widget, mn, mx, val, step=step, decimals=decimals)
            setattr(self, f"spin_{name}".replace(' ', '_'), widget)
            form_layout.addRow(f"{name.replace('_',' ').title()}:", widget)

        # Botones
        btn_save = QPushButton("Save Settings"); btn_save.clicked.connect(self.save_settings_and_notify)
        btn_run = QPushButton("Run VacancyAnalysis"); btn_run.clicked.connect(self.run_vacancy_analysis)
        btn_total = QPushButton("Total Vacancies"); btn_total.clicked.connect(self.show_total_vacancies)  # ⬅️ nuevo

        hb = QHBoxLayout(); hb.addWidget(btn_save); hb.addWidget(btn_run)

        form_layout.addRow(hb)

        hb = QHBoxLayout()
        hb.addWidget(btn_save)
        hb.addWidget(btn_run)
        hb.addWidget(btn_total) 
        form_layout.addRow(hb)

        controls_widget = QWidget(); controls_widget.setLayout(form_layout)
        controls_widget.setFixedWidth(int(320 * 1.3))
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(controls_widget)

        # Panel derecho con pestañas (Main / Viewer 1 / Key Areas)
        tabs = QTabWidget()

        # --- Tab Main (tu viewer original) ---
        main_tab = QWidget(); main_layout = QVBoxLayout(main_tab)
        self.plotter = QtInteractor(main_tab); main_layout.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4)); self.canvas = FigureCanvas(self.fig); main_layout.addWidget(self.canvas)
        self.table = QTableWidget(); main_layout.addWidget(self.table)
        tabs.addTab(main_tab, "Main")

        # --- Tab Viewer 1 ---
        self.viewer1 = DumpViewerWidget()
        tabs.addTab(self.viewer1, "Viewer 1")

        # --- Tab Key Areas ---
        self.viewer2 = KeyAreaSeqWidget()
        tabs.addTab(self.viewer2, "Key Areas")

        # Layout principal
        main = QWidget(); hl = QHBoxLayout(main); hl.addWidget(scroll); hl.addWidget(tabs, 1)
        self.setCentralWidget(main)
        # --- Tab Key Areas ---
        self.viewer2 = KeyAreaSeqWidget()
        tabs.addTab(self.viewer2, "Key Areas")

        # --- Tab Training (nueva) ---
        self.training_tab = TrainingTab(self)
        tabs.addTab(self.training_tab, "Training")

        # Carga inicial
        dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
        if dump_path.exists():
            self.load_dump(str(dump_path))
            try:
                self.viewer1.render_dump(str(dump_path))
            except Exception:
                pass

    # ===== Utils UI =====
    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        w = QWidget(); w.setLayout(layout); return w

    def _configure_spin(self, spin, mn, mx, val, step=None, decimals=None):
        spin.setRange(mn, mx)
        if isinstance(spin, QDoubleSpinBox):
            if decimals is not None:
                spin.setDecimals(decimals)
            spin.setSingleStep(step if step is not None else 0.1)
        else:
            spin.setSingleStep(step if step is not None else 1)
        spin.setValue(val)

    def save_settings_and_notify(self):
        saved_path = self.save_settings()
        QMessageBox.information(self, "Settings Saved", f"Parameters saved to:\n{saved_path}")

    def save_settings(self):
        cfg = self.params['CONFIG'][0]
        cfg['training'] = self.check_training.isChecked()
        cfg['geometric_method'] = self.check_geometric.isChecked()
        cfg['activate_generate_relax'] = self.check_activate_relax.isChecked()
        cfg['generate_relax'] = [
            self.edit_lattice.text(),
            float(self.spin_lattice_a.value()),
            self.spin_rx.value(), self.spin_ry.value(), self.spin_rz.value(),
            self.edit_atom.text().strip() or 'Fe'
        ]
        cfg['relax'] = self.edit_relax.text()
        cfg['defect'] = [self.edit_defect.text()]
        for key in ['radius', 'cutoff', 'max_graph_size', 'max_graph_variations',
                    'radius_training', 'training_file_index', 'cluster tolerance',
                    'divisions_of_cluster', 'iteraciones_clusterig']:
            widget = getattr(self, f"spin_{key}".replace(' ', '_'))
            cfg[key] = widget.value()
        return save_params(self.params)
    def show_total_vacancies(self):
        """Abre una ventana con el total de vacancias de outputs/csv/results.csv."""
        try:
            path = Path.cwd() / 'outputs' / 'csv' / 'results.csv'
            if not path.exists():
                QMessageBox.warning(self, "Archivo no encontrado",
                                    f"No existe:\n{path.as_posix()}")
                return

            df = pd.read_csv(path)

            # columnas candidatas donde puede estar el número de vacancias por fila
            candidates = ["predicted_vacancy", "vacancys_est", "vacancys", "predicted", "vacancy"]
            col = next((c for c in candidates if c in df.columns), None)
            if col is None:
                QMessageBox.critical(
                    self, "Columna no encontrada",
                    "No se encontró ninguna de estas columnas en results.csv:\n"
                    + ", ".join(candidates)
                )
                return

            vals = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            total = float(vals.sum())
            total_int = int(np.ceil(total))  # redondeo hacia arriba por si hay decimales

            # Mensaje bonito
            msg = QMessageBox(self)
            msg.setWindowTitle("Total de vacancias")
            msg.setText(
                f"<h2 style='margin:0'>Total de vacancias: {total_int}</h2>"
            )
            msg.exec()
            print(f"Vacancias totales: {total_int}")

        except Exception as e:
            QMessageBox.critical(self, "Error calculando total", str(e))

    def _refresh_csv_list(self):
        csv_dir = Path.cwd() / 'outputs' / 'csv'
        self.csv_combo.clear()
        if csv_dir.exists():
            for f in sorted(csv_dir.glob('*.csv')):
                self.csv_combo.addItem(f.name)

    def load_csv_results(self):
        nombre = self.csv_combo.currentText()
        if not nombre:
            QMessageBox.warning(self, "Sin selección", "No has elegido ningún CSV.")
            return
        ruta = Path.cwd() / 'outputs' / 'csv' / nombre
        try:
            df = pd.read_csv(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", str(e))
            return
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        self.table.resizeColumnsToContents()

    def browse_file(self, line_edit):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            try:
                line_edit.setText(Path(abs_path).relative_to(GUI_ROOT).as_posix())
            except ValueError:
                line_edit.setText(abs_path)

    # --- Visual principal (misma lógica que viewers internos) ---
    def load_dump(self, dump_path):
        self.progress.setValue(0)
        try:
            render_dump_to(self.plotter, self.fig, dump_path)
            self.canvas.draw()
            self.progress.setValue(100)
        except Exception as e:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error al cargar dump", str(e))

    # --- Run del análisis ---
    def run_vacancy_analysis(self):
        self.log_output.clear()
        buf = io.StringIO()
        self.progress.setRange(0, 0)
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                vfs.VacancyAnalysis()
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.information(self, "Análisis completado", "VacancyAnalysis terminó correctamente.")
            self._refresh_csv_list()
            dump_path = Path.cwd() / 'outputs' / 'dump' / 'key_areas.dump'
            if dump_path.exists():
                self.load_dump(str(dump_path))
                try:
                    self.viewer1.render_dump(str(dump_path))
                except Exception:
                    pass
        except Exception:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            buf.write(traceback.format_exc())
            self.log_output.setPlainText(buf.getvalue())
            QMessageBox.critical(self, "Error en análisis", "Falló VacancyAnalysis. Revisa el log.")


def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
