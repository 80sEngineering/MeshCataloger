import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtCore import QPoint, Qt


class Viewer(gl.GLViewWidget):  # allows to track camera's movement and clicks.

    def __init__(self):
        super().__init__()
        self.clicked_position = QPoint()
        self.displayed_mesh = []
        self.intersection_triangle = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]]).reshape(3, 3)

    def wheelEvent(self, event):  # zoom
        super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.aiming_line()
        self.clicked_position.x, self.clicked_position.y = event.pos().x(), event.pos().y()


    # to get camera params, use self.cameraParams()

    def aiming_line(self):
        point_of_view = self.cameraPosition()
        center = self.cameraParams()["center"]
        dir_vector_to_center = center - point_of_view

        # show the line
        # line = gl.GLLinePlotItem(pos=[point_of_view, ], width=10, antialias=True, color=(0, 1, 0, 1))
        # self.addItem(line)

        # check_for_intersection
        face_vertexes = self.displayed_mesh[0][1].vertexes(
            indexed='faces')  # [ [ [ x1,y1,z1 ] , [x2,y2,z2 ] , [x3,y3,z3] ] , [x1,y1,z1] ...] ]
        distances = []
        index = 0
        for face_vertex in face_vertexes: # Browse from bottom to top
            if self.ray_triangle_intersection(point_of_view, dir_vector_to_center, face_vertex):
                distances.append([self.check_distance(face_vertex), face_vertex])
            index += 1
        closest = min(distances, key=lambda x: x[0]) # distance = [ distance, face_vertex ]
        selected_face = closest[1]
        self.color_face(selected_face)

    def ray_triangle_intersection(self, start, direction, triangle):
        point1, point2, point3 = triangle[0], triangle[1], triangle[2]

        eps = 0.000001

        edge1 = point2 - point1
        edge2 = point3 - point1

        direction = np.array([direction.x(), direction.y(), direction.z()])
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
        self.intersection_triangle = triangle
        return True

    def check_distance(self, triangle):
        distance = min(
            [np.linalg.norm(self.cameraPosition() - triangle[0]), np.linalg.norm(self.cameraPosition() - triangle[1]),
             np.linalg.norm(self.cameraPosition() - triangle[2])])
        return distance

    def color_face(self, face):
        data = gl.MeshData(vertexes=np.array(face), faces=[[0, 1, 2]])
        selected_face = gl.GLMeshItem(meshdata=data, smooth=False, drawFaces=True)
        self.addItem(selected_face)

    def set_displayed_mesh(self, mesh, data):
        self.addItem(mesh)
        self.displayed_mesh.append([mesh, data])
