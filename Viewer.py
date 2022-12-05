from math import copysign

import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QVector3D, QColor
from PyQt6.QtTest import QTest
from pyqtgraph.Vector import Vector

from Mesh import Mesh


class Viewer(gl.GLViewWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.displayed_items = []
        self.dimensions_stl = None
        self.camera_distance = 40
        self.setCameraParams(distance=self.camera_distance, fov=60)
        self.center = Vector(0, 0, 0)
        self.axis = gl.GLAxisItem()  # blue axis = x, yellow = y, green = z
        self.axis.setVisible(False)
        self.set_displayed_items(self.axis, None, "axis")
        self.grid = gl.GLGridItem()
        self.grid.setVisible(False)
        self.set_displayed_items(self.grid, None, "grid")
        self.aiming_dot = gl.GLScatterPlotItem(pos=self.cameraParams()['center'], size=10, color=(1, 0, 0, 1))
        self.set_displayed_items(self.aiming_dot, None, "aiming_dot")
        self.intersection_triangle = np.empty((3, 3))

    def set_displayed_items(self, item, data, name):
        self.addItem(item)
        self.displayed_items.append({'mesh': item, 'data': data, 'name': name})

    def remove_displayed_items(self, name):
        for displayed_item in self.displayed_items:
            if displayed_item["name"] == name:
                self.removeItem(displayed_item['mesh'])
                self.displayed_items.remove(displayed_item)

        if name == "grid":
            self.grid = gl.GLGridItem()
            self.grid.setVisible(False)
            self.set_displayed_items(self.grid, None, "grid")

        if name == "axis":
            self.axis = gl.GLAxisItem()
            self.axis.setVisible(False)
            self.set_displayed_items(self.axis, None, "axis")

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        current_center = self.cameraParams()["center"]
        self.aiming_dot.setData(pos=current_center)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.RightButton and len(
                self.displayed_items) > 1:  # to make sure a mesh is loaded
            self.aiming_line()

    def show_stl(self, file_name):
        file = Mesh(file_name)
        self.dimensions_stl = file.get_dimensions()
        self.set_displayed_items(file.mesh, file.data, "stl")
        # Scale and move the grid and axis so that the mesh sits on it
        self.axis.scale(int(self.dimensions_stl["width"] / 5), int(self.dimensions_stl["length"] / 5),
                        int(self.dimensions_stl["height"] / 5))
        self.grid.scale(int(self.dimensions_stl["width"] / 10), int(self.dimensions_stl["length"] / 10), 1)
        self.grid.translate(0, 0, int(self.dimensions_stl["height"] / -2))
        # Moves the camera to account for mesh's size.
        distances = [self.dimensions_stl['width'] / np.tan(np.pi * 0.1666),
                     self.dimensions_stl['length'] / np.tan(np.pi * 0.1666),
                     self.dimensions_stl['height'] / np.tan(np.pi * 0.1666)]
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
        face_vertexes = None
        for mesh in self.displayed_items:
            if mesh['name'] == "stl":
                face_vertexes = mesh['data'].vertexes(
                    indexed='faces')  # [ [ [ x1,y1,z1 ] , [x2,y2,z2 ] , [x3,y3,z3] ] , [x1,y1,z1] ...] ]
                break

        distances = []
        index = 0
        for face_vertex in face_vertexes:  # Browse from bottom to top
            if self.ray_triangle_intersection(point_of_view, dir_vector_to_center, face_vertex):
                distances.append([self.check_distance(face_vertex), face_vertex])
            index += 1
        if len(distances) > 0:  # if there is an intersection
            closest = min(distances, key=lambda x: x[0])  # distance = [ distance, face_vertex ]
            selected_face = closest[1]
            self.select_face(selected_face, (0, 0, 1, 1))
            self.rotate_camera(selected_face)

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
            [np.linalg.norm(self.cameraPosition() - triangle[0]),
             np.linalg.norm(self.cameraPosition() - triangle[1]),
             np.linalg.norm(self.cameraPosition() - triangle[2])])
        return distance

    def select_face(self, face, color):
        data = gl.MeshData(vertexes=np.array(face), faces=[[0, 1, 2]])
        face_mesh = gl.GLMeshItem(meshdata=data, smooth=False, drawFaces=True, color=color)
        self.remove_displayed_items("face")
        self.set_displayed_items(face_mesh, data, "face")

    def rotate_camera(self, face):  # TODO fix weird rotation on some vertical faces.
        # Getting the center of the face to align it with the center of rotation of the camera.
        center = (face[0] + face[1] + face[2]) / 3
        center = QVector3D(center[0], center[1], center[2])

        #  Getting the normal of the face to align it with direction of the camera.
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        normal = QVector3D(normal[0], normal[1], normal[2])

        # Computing elevation and azimuth of the camera from the normal.
        x0, y0, z0 = center.x(), center.y(), center.z()
        x, y, z = x0 + normal.x(), y0 + normal.y(), z0 + normal.z()
        final_elevation = np.arccos(z / np.sqrt(x ** 2 + y ** 2 + z ** 2))
        final_elevation = np.pi / 2 - final_elevation
        final_azimuth = np.sign(y) * np.arccos(x / np.sqrt(x ** 2 + y ** 2))
        final_elevation, final_azimuth = np.rad2deg(final_elevation), np.rad2deg(final_azimuth)

        # Smoothing camera's movement
        current_camera_parameters = self.cameraParams()
        current_elevation, current_azimuth = current_camera_parameters["elevation"], current_camera_parameters[
            "azimuth"]
        elevation_travel = np.linspace(current_elevation, final_elevation, 50)
        if abs(final_azimuth - current_azimuth) > 180:
            if final_azimuth > current_azimuth:
                final_azimuth -= 360
            else:
                final_azimuth += 360
        azimuth_travel = np.linspace(current_azimuth, final_azimuth, 50)
        distance_travel = np.linspace(current_camera_parameters["distance"], self.camera_distance, 50)
        center_x_travel = np.linspace(current_camera_parameters["center"][0], center.x(), 50)
        center_y_travel = np.linspace(current_camera_parameters["center"][1], center.y(), 50)
        center_z_travel = np.linspace(current_camera_parameters["center"][2], center.z(), 50)

        for elevation, azimuth, distance, center_x, center_y, center_z in zip(elevation_travel, azimuth_travel,
                                                                              distance_travel, center_x_travel,
                                                                              center_y_travel, center_z_travel):
            self.setCameraParams(elevation=elevation, azimuth=azimuth, distance=distance,
                                 center=Vector(center_x, center_y, center_z))
            self.update()
            QTest.qWait(10)

    def angle_from_vectors(self, vector1, vector2):
        normalized_vector1, normalized_vector2 = (vector1 / np.linalg.norm(vector1)).reshape(3), (
                vector2 / np.linalg.norm(vector2)).reshape(3)
        cross_product = np.cross(normalized_vector1, normalized_vector2)
        if any(cross_product):  # in case the two vectors are collinear
            dot_product = np.dot(normalized_vector1, normalized_vector2)
            normalized_cross_product = np.linalg.norm(cross_product)
            result = np.array([[0, -cross_product[2], cross_product[1]], [cross_product[2], 0, -cross_product[0]],
                               [-cross_product[1], cross_product[0], 0]])
            rotation_matrix = np.eye(3) + result + result.dot(result) * (
                    (1 - dot_product) / (normalized_cross_product ** 2))
            collinear = False
        else:
            rotation_matrix = np.eye(3)
            collinear = True

        r11, r12, r13 = rotation_matrix[0]
        r21, r22, r23 = rotation_matrix[1]
        r31, r32, r33 = rotation_matrix[2]

        if r33 != 0:  # Those are only useful in case of perpendicular vectors.
            x_angle = np.arctan(-r23 / r33)
            y_angle = np.arctan(r13 * np.cos(x_angle) / r33)
        else:
            x_angle = np.arctan(copysign(1, -r23) * np.inf)  # copysign(1,x) returns the sign of x
            y_angle = np.arctan(copysign(1, r13 * np.cos(x_angle)) * np.inf)
        if r11 != 0:
            z_angle = np.arctan(-r12 / r11)
        else:
            z_angle = np.arctan(copysign(1, -r12) * np.inf)

        x_angle = x_angle * 180 / np.pi
        y_angle = y_angle * 180 / np.pi
        z_angle = z_angle * 180 / np.pi

        angles = [x_angle, y_angle, z_angle]
        return angles, collinear

    def show_char(self, files):
        """

        Function for custom formatting
        pg.SpinBox(value=4567, step=1, int=True, bounds=[0, None], format='0x{value:X}',
                   regex='(0x)?(?P<number>[0-9a-fA-F]+)$',
                   evalFunc=lambda s: ast.literal_eval('0x' + s)))
        """
        normal, face_center = QVector3D(0, 0, 0), np.array(3)
        for item in self.displayed_items:
            if item["name"] == "face":
                face = item['mesh'].vertexes[0]
                face_center = (face[0] + face[1] + face[2]) / 3
                normal = np.cross(face[1] - face[0], face[2] - face[0])
                normal = QVector3D(normal[0], normal[1], normal[2])
                normal.normalize()
                break
        angles, collinear = self.angle_from_vectors(np.array([0, 0, 1]), np.array([normal.x(), normal.y(), normal.z()]))
        if not collinear:  # if selected face is not parallel to the grid
            writing_direction = QVector3D.crossProduct(normal, QVector3D(0, 0, 1))
        else:
            writing_direction = QVector3D(1, 0, 0)

        for file_number in range(
                len(files)):  # opening the mesh, moving it to the center of the face, and rotating it to align with it.
            file_name = files[file_number]
            if file_name != "space" and file_name != "*":
                file = Mesh(file_name, char=True)
                file.mesh.setColor(QColor(255, 0, 0))
                file_volume = self.dimensions_stl["width"] * self.dimensions_stl["length"] * self.dimensions_stl[
                    "height"]
                file_volume = file_volume ** 0.33
                file.mesh.scale(file_volume / 100, file_volume / 100, file_volume / 100)
                distance_between_char = (-len(files) + 1 + (int(len(files) - 1)) + file_number) * file_volume / 10
                file.mesh.translate(face_center[0] + int(writing_direction[0] * distance_between_char),
                                    face_center[1] + int(writing_direction[1] * distance_between_char), face_center[2])
                file.mesh.rotate(90, 1, 0, 0, local=True)  # fixes initial orientation
                file.mesh.rotate(angles[0], 1, 0, 0, local=True)
                file.mesh.rotate(angles[1], 0, 1, 0, local=True)
                file.mesh.rotate(angles[2], 0, 0, 1, local=True)
                self.set_displayed_items(file.mesh, file.data, "char")
