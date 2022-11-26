import sys
from pathlib import Path

import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtCore import QSize, QPoint
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QWidget, \
    QFileDialog, QLabel

from Mesh import Mesh
from Viewer import Viewer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.setMinimumSize(QSize(500, 500))

        self.mesh_viewer = Viewer()
        self.grid = gl.GLGridItem()
        self.init_mesh_viewer()
        view_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
        self.init_mesh_viewer()
        view_layout.addWidget(self.mesh_viewer)
        view_layout.addLayout(bottom_layout)
        view = QWidget()
        view.setLayout(view_layout)
        self.setCentralWidget(view)

    def init_mesh_viewer(self):
        camera_params = {
            'distance': 40.0,
            'fov': 60
        }
        viewer_layout = QStackedLayout()
        self.mesh_viewer.setCameraParams(**camera_params)
        self.mesh_viewer.setCameraParams()
        self.mesh_viewer.addItem(self.grid)




    def init_button_and_text(self):
        file_button = QPushButton("Browse")
        layout = QHBoxLayout()
        file_button.setCheckable(True)
        file_button.setFixedSize(100, 50)
        file_button.clicked.connect(self.clicked_file_button)
        text = QLabel("Please select a file.")
        layout.addWidget(text)
        layout.addWidget(file_button)
        return layout

    def clicked_file_button(self):
        home_directory = str(Path.home())
        data = QFileDialog.getOpenFileName(self, 'Open file', home_directory, filter="*.stl")
        file_name = data[0]
        self.show_stl(file_name)

    def show_stl(self, file_name):
        file = Mesh(file_name)
        self.mesh_viewer.set_displayed_mesh(file.mesh, file.data)
        # Moves the grid so that the mesh sits on it
        self.grid.scale(int(file.dimensions["width"] / 10), int(file.dimensions["length"] / 10), 1)
        self.grid.translate(0, 0, int(file.dimensions["height"] / -2))
        # Moves the camera to account for mesh's size.
        distances = [file.dimensions['width'] / np.tan(np.pi * 0.1666),
                     file.dimensions['length'] / np.tan(np.pi * 0.1666),
                     file.dimensions['height'] / np.tan(np.pi * 0.1666)]
        self.mesh_viewer.setCameraParams(distance=max(distances))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
