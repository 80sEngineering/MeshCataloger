import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, \
    QLabel
from PyQt6.QtCore import QSize, QPoint
import pyqtgraph.opengl as gl
import stl
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.setFixedSize(QSize(500, 500))

        self.mesh_viewer = Viewer()
        self.grid = gl.GLGridItem()
        self.init_mesh_viewer()
        view_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
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
        self.mesh_viewer.addItem(file.mesh)
        # Moves the grid so that the mesh sits on it
        self.grid.scale(int(file.dimensions["width"] / 10), int(file.dimensions["length"] / 10), 1)
        self.grid.translate(0, 0, int(file.dimensions["height"] / -2))
        # Moves the camera to account for mesh's size.
        distances = [file.dimensions['width'] / np.tan(np.pi * 0.1666),
                     file.dimensions['length'] / np.tan(np.pi * 0.1666),
                     file.dimensions['height'] / np.tan(np.pi * 0.1666)]
        self.mesh_viewer.setCameraParams(distance=max(distances))


class Viewer(gl.GLViewWidget):  # allows to track camera's movement and clicks.

    def __init__(self):
        super().__init__()
        self.clicked_position = QPoint()

    def wheelEvent(self, event):  # zoom
        super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clicked_position.x, self.clicked_position.y = event.pos().x(), event.pos().y()
        self.aiming_line()

    # to get camera params, use self.cameraParams()

    def aiming_line(self):
        first_point = self.cameraPosition()
        second_point = self.cameraParams()["center"]
        dir_vector = second_point - first_point

        line = gl.GLLinePlotItem(pos=[first_point, second_point], width=10, antialias=True, color=(0, 1, 0, 1))
        self.addItem(line)

    def ray_triangle_intersection(self, start, direction, triangle):
        # break down triangle into the individual points
        point1, point2, point3 = triangle
        eps = 0.000001

        # compute edges
        edge1 = point2 - point1
        edge2 = point3 - point1
        cross_product = np.cross(direction, edge2)
        det = edge1.dot(cross_product)

        if abs(det) < eps:  # no intersection
            return False
        inverted_det = 1.0 / det
        tvec = start - point1
        u = tvec.dot(cross_product) * inverted_det

        if u < 0.0 or u > 1.0:  # if not intersection
            return False

        qvec = np.cross(tvec, edge1)
        v = direction.dot(qvec) * inverted_det
        if v < 0.0 or u + v > 1.0:  # if not intersection
            return False

        t = edge2.dot(qvec) * inverted_det
        if t < eps:
            return False

        return True, np.array([t, u, v])


class Mesh:
    def __init__(self, file_name):
        self.file = stl.mesh.Mesh.from_file(file_name)
        self.mesh = self.convert_to_stl()
        self.dimensions = self.get_dimensions()
        self.center_mesh()

    def convert_to_stl(self):
        points = self.file.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        mesh = gl.MeshData(faces=faces, vertexes=points)
        mesh = gl.GLMeshItem(meshdata=mesh, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        return mesh

    def get_dimensions(self):
        minx = maxx = miny = maxy = minz = maxz = None
        for point in self.file.points:
            if minx is None:
                minx = point[stl.Dimension.X]
                maxx = point[stl.Dimension.X]
                miny = point[stl.Dimension.Y]
                maxy = point[stl.Dimension.Y]
                minz = point[stl.Dimension.Z]
                maxz = point[stl.Dimension.Z]
            else:
                maxx = max(point[stl.Dimension.X], maxx)
                minx = min(point[stl.Dimension.X], minx)
                maxy = max(point[stl.Dimension.Y], maxy)
                miny = min(point[stl.Dimension.Y], miny)
                maxz = max(point[stl.Dimension.Z], maxz)
                minz = min(point[stl.Dimension.Z], minz)

        dimensions = {"width": maxx - minx,
                      "length": maxy - miny,
                      "height": maxz - minz,
                      "minx": minx,
                      "maxx": maxx,
                      "miny": miny,
                      "maxy": maxy,
                      "minz": minz,
                      "maxz": maxz}
        return dimensions

    def center_mesh(self):
        dx = -self.dimensions["minx"] - (self.dimensions["width"] / 2)
        dy = -self.dimensions["miny"] - (self.dimensions["length"] / 2)
        dz = -self.dimensions["minz"] - (self.dimensions["height"] / 2)
        self.mesh.translate(dx, dy, dz)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
