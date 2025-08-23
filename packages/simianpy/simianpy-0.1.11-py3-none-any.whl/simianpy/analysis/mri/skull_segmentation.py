import sys
import numpy as np
import nibabel as nib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QFileDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import ndimage
from skimage.segmentation import watershed

class SegmentationGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MRI Skull Segmentation Tool")
        self.resize(800, 800)

        self.volume = None
        self.slice_idxs = [0, 0, 0]  # [sagittal, coronal, axial]
        self.threshold = 50
        self.marker_mode = "Foreground"
        self.markers = []

        # Layout
        layout = QVBoxLayout()

        # Load button
        load_btn = QPushButton("Load NIfTI File")
        load_btn.clicked.connect(self.load_nifti)
        layout.addWidget(load_btn)

        # Threshold slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setValue(self.threshold)
        self.slider.valueChanged.connect(self.update_threshold)
        layout.addWidget(QLabel("Threshold"))
        layout.addWidget(self.slider)

        # Marker mode buttons
        marker_layout = QHBoxLayout()
        fg_btn = QPushButton("Foreground Mode")
        bg_btn = QPushButton("Background Mode")
        fg_btn.clicked.connect(lambda: self.set_marker_mode("Foreground"))
        bg_btn.clicked.connect(lambda: self.set_marker_mode("Background"))
        marker_layout.addWidget(fg_btn)
        marker_layout.addWidget(bg_btn)
        layout.addLayout(marker_layout)

        # Segmentation button
        seg_btn = QPushButton("Run Segmentation")
        seg_btn.clicked.connect(self.run_segmentation)
        layout.addWidget(seg_btn)

        # Matplotlib figure with 3 panels
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Sliders for each panel
        self.slice_sliders = []
        slider_labels = ["Sagittal (X)", "Coronal (Y)", "Axial (Z)"]
        for i, label in enumerate(slider_labels):
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(label))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(0)  # will be set after loading data
            slider.setValue(0)
            slider.valueChanged.connect(lambda value, idx=i: self.update_slice_idx(idx, value))
            hbox.addWidget(slider)
            layout.addLayout(hbox)
            self.slice_sliders.append(slider)

        # Table for markers
        self.marker_table = QTableWidget(0, 5)
        self.marker_table.setHorizontalHeaderLabels(["X", "Y", "Z", "Label", "Delete"])
        self.marker_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.marker_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(QLabel("Markers"))
        layout.addWidget(self.marker_table)

        self.setLayout(layout)

        self.canvas.mpl_connect("button_press_event", self.on_click)

    def load_nifti(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open NIfTI File", "", "NIfTI files (*.nii *.nii.gz)")
        if file_name:
            nii = nib.load(file_name)
            self.volume = nii.get_fdata()
            shape = self.volume.shape
            self.slice_idxs = [shape[0] // 2, shape[1] // 2, shape[2] // 2]
            # Set slider ranges
            for i, slider in enumerate(self.slice_sliders):
                slider.setMaximum(shape[i] - 1)
                slider.setValue(self.slice_idxs[i])
            self.markers = []
            self.update_plot()

    def update_slice_idx(self, axis, value):
        if self.volume is not None:
            self.slice_idxs[axis] = value
            self.update_plot()

    def update_threshold(self, value):
        self.threshold = value
        self.update_plot()

    def set_marker_mode(self, mode):
        self.marker_mode = mode

    def on_click(self, event):
        if self.volume is None:
            return
        if event.inaxes is None:
            return
        # Determine which panel was clicked
        ax_idx = None
        for i, ax in enumerate(self.figure.axes):
            if event.inaxes == ax:
                ax_idx = i
                break
        if ax_idx is None:
            return
        x = int(event.xdata)
        y = int(event.ydata)
        # Map x, y to the correct axis
        if ax_idx == 0:  # Sagittal (X)
            coords = (self.slice_idxs[0], x, y)
        elif ax_idx == 1:  # Coronal (Y)
            coords = (x, self.slice_idxs[1], y)
        elif ax_idx == 2:  # Axial (Z)
            coords = (x, y, self.slice_idxs[2])
        else:
            return
        self.markers.append((*coords, self.marker_mode))
        self.refresh_marker_table()
        self.update_plot()

    def refresh_marker_table(self):
        self.marker_table.setRowCount(len(self.markers))
        for i, (x, y, z, mode) in enumerate(self.markers):
            self.marker_table.setItem(i, 0, QTableWidgetItem(str(x)))
            self.marker_table.setItem(i, 1, QTableWidgetItem(str(y)))
            self.marker_table.setItem(i, 2, QTableWidgetItem(str(z)))
            # ComboBox for label
            combo = QComboBox()
            combo.addItems(["Foreground", "Background"])
            combo.setCurrentText(mode)
            combo.currentTextChanged.connect(lambda value, row=i: self.change_marker_label(row, value))
            self.marker_table.setCellWidget(i, 3, combo)
            # Delete button
            btn = QPushButton("Delete")
            btn.clicked.connect(lambda _, row=i: self.delete_marker(row))
            self.marker_table.setCellWidget(i, 4, btn)

    def change_marker_label(self, row, value):
        if 0 <= row < len(self.markers):
            x, y, z, _ = self.markers[row]
            self.markers[row] = (x, y, z, value)
            self.update_plot()

    def delete_marker(self, row):
        if 0 <= row < len(self.markers):
            del self.markers[row]
            self.refresh_marker_table()
            self.update_plot()

    def update_plot(self):
        self.figure.clear()
        axes = [self.figure.add_subplot(1, 3, i + 1) for i in range(3)]
        titles = ["Sagittal (X)", "Coronal (Y)", "Axial (Z)"]
        if self.volume is not None:
            # Sagittal (X): x fixed, show y vs z
            x = self.slice_idxs[0]
            sagittal = self.volume[x, :, :]
            mask_sag = sagittal > self.threshold
            axes[0].imshow(sagittal.T, cmap='gray', origin='lower')
            axes[0].contour(mask_sag.T, colors='r', alpha=0.5)
            axes[0].set_title(titles[0])

            # Coronal (Y): y fixed, show x vs z
            y = self.slice_idxs[1]
            coronal = self.volume[:, y, :]
            mask_cor = coronal > self.threshold
            axes[1].imshow(coronal.T, cmap='gray', origin='lower')
            axes[1].contour(mask_cor.T, colors='r', alpha=0.5)
            axes[1].set_title(titles[1])

            # Axial (Z): z fixed, show x vs y
            z = self.slice_idxs[2]
            axial = self.volume[:, :, z]
            mask_axi = axial > self.threshold
            axes[2].imshow(axial.T, cmap='gray', origin='lower')
            axes[2].contour(mask_axi.T, colors='r', alpha=0.5)
            axes[2].set_title(titles[2])

            # Plot markers for each panel
            for idx, ax in enumerate(axes):
                for mx, my, mz, mode in self.markers:
                    color = 'g' if mode == "Foreground" else 'b'
                    if idx == 0 and mx == x:
                        ax.plot(my, mz, marker='o', color=color)
                    elif idx == 1 and my == y:
                        ax.plot(mx, mz, marker='o', color=color)
                    elif idx == 2 and mz == z:
                        ax.plot(mx, my, marker='o', color=color)

        self.figure.tight_layout()
        self.canvas.draw()

    def run_segmentation(self):
        if self.volume is None:
            return

        mask = self.volume > self.threshold
        distance = ndimage.distance_transform_edt(mask)

        # Create marker volume
        markers_vol = np.zeros_like(mask, dtype=np.int32)
        for idx, (x, y, z, mode) in enumerate(self.markers, start=1):
            if mode == "Foreground":
                markers_vol[x, y, z] = 1
            elif mode == "Background":
                markers_vol[x, y, z] = 2

        labels = watershed(-distance, markers_vol, mask=mask)

        # Show segmentation for each panel
        self.figure.clear()
        axes = [self.figure.add_subplot(1, 3, i + 1) for i in range(3)]
        titles = ["Sagittal (X)", "Coronal (Y)", "Axial (Z)"]
        x, y, z = self.slice_idxs
        axes[0].imshow(labels[x, :, :].T, cmap='nipy_spectral', origin='lower')
        axes[0].set_title(titles[0])
        axes[1].imshow(labels[:, y, :].T, cmap='nipy_spectral', origin='lower')
        axes[1].set_title(titles[1])
        axes[2].imshow(labels[:, :, z].T, cmap='nipy_spectral', origin='lower')
        axes[2].set_title(titles[2])
        self.figure.tight_layout()
        print(f"Number of segments: {np.unique(labels).size - 1}")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SegmentationGUI()
    window.show()
    sys.exit(app.exec_())
