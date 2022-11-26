import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QVector3D
from PyQt6.QtTest import QTest

from Mesh import Mesh


class Viewer(gl.GLViewWidget):  # allows to track camera's movement and clicks.

    def __init__(self):
        super().__init__()
        self.displayed_mesh = []
        self.camera_distance = 40
        self.setCameraParams(distance=self.camera_distance, fov=60)
        self.grid = gl.GLGridItem()
        self.addItem(self.grid)
        self.intersection_triangle = np.empty((3, 3))

    def set_displayed_mesh(self, mesh, data):
        self.addItem(mesh)
        self.displayed_mesh.append([mesh, data])

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.aiming_line()

    def show_stl(self, file_name):
        file = Mesh(file_name)
        self.set_displayed_mesh(file.mesh, file.data)
        # Moves the grid so that the mesh sits on it
        self.grid.scale(int(file.dimensions["width"] / 10), int(file.dimensions["length"] / 10), 1)
        self.grid.translate(0, 0, int(file.dimensions["height"] / -2))
        # Moves the camera to account for mesh's size.
        distances = [file.dimensions['width'] / np.tan(np.pi * 0.1666),
                     file.dimensions['length'] / np.tan(np.pi * 0.1666),
                     file.dimensions['height'] / np.tan(np.pi * 0.1666)]
        self.camera_distance = max(distances)
        self.setCameraParams(distance=self.camera_distance)

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
        for face_vertex in face_vertexes:  # Browse from bottom to top
            if self.ray_triangle_intersection(point_of_view, dir_vector_to_center, face_vertex):
                distances.append([self.check_distance(face_vertex), face_vertex])
            index += 1
        closest = min(distances, key=lambda x: x[0])  # distance = [ distance, face_vertex ]
        selected_face = closest[1]
        self.select_face(selected_face)

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

    def select_face(self, face):
        data = gl.MeshData(vertexes=np.array(face), faces=[[0, 1, 2]])
        face_mesh = gl.GLMeshItem(meshdata=data, smooth=False, drawFaces=True, color=(1, 0, 0, 1))
        self.addItem(face_mesh)

        # Getting the center of the face == center of rotation of the camera.
        center = (face[0] + face[1] + face[2]) / 3
        center = QVector3D(center[0], center[1], center[2])

        #  Getting the normal of the face == direction of the camera.
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        normal = QVector3D(normal[0], normal[1], normal[2])

        # Computing elevation and azimuth of the camera from the normal.
        x0, y0, z0 = center.x(), center.y(), center.z()
        x, y, z = x0 + normal.x(), y0 + normal.y(), z0 + normal.z()
        final_elevation = np.arccos(z / np.sqrt(x ** 2 + y ** 2 + z ** 2))
        final_elevation = np.pi / 2 - final_elevation
        final_azimuth = np.sign(y) * np.arccos(x / np.sqrt(x ** 2 + y ** 2))
        final_elevation, final_azimuth = np.rad2deg(final_elevation), np.rad2deg(final_azimuth)

        current_camera_parameters = self.cameraParams()
        current_elevation, current_azimuth = current_camera_parameters["elevation"], current_camera_parameters[
            "azimuth"]

        elevation_travel = np.linspace(current_elevation, final_elevation, 50)
        azimuth_travel = np.linspace(current_azimuth, final_azimuth, 50)
        distance_travel = np.linspace(current_camera_parameters["distance"], self.camera_distance, 50)
        center_x_travel = np.linspace(current_camera_parameters["center"][0], center.x(), 50)
        center_y_travel = np.linspace(current_camera_parameters["center"][1], center.y(), 50)
        center_z_travel = np.linspace(current_camera_parameters["center"][2], center.z(), 50)

        for elevation, azimuth, distance, center_x, center_y, center_z in zip(elevation_travel, azimuth_travel,
                                                                              distance_travel, center_x_travel,
                                                                              center_y_travel, center_z_travel):
            self.setCameraParams(elevation=elevation, azimuth=azimuth, distance=distance, center=QVector3D(center_x,center_y,center_z))
            self.update()
            QTest.qWait(10)
