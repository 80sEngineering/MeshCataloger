import numpy as np
import pyqtgraph.opengl as gl
import stl


class Mesh:
    def __init__(self, file_name):
        self.file = stl.mesh.Mesh.from_file(file_name)
        self.data = self.convert_data()
        self.mesh = self.convert_to_stl()
        self.dimensions = self.get_dimensions()
        self.center_mesh()

    def convert_data(self):
        points = self.file.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        data = gl.MeshData(faces=faces, vertexes=points)
        return data

    def convert_to_stl(self):
        mesh = gl.GLMeshItem(meshdata=self.data, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1, 1, 1, 1))
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
        vertexes = []
        for vertex in self.data.vertexes():
            vertex[0] += dx
            vertex[1] += dy
            vertex[2] += dz
            vertexes.append(vertex)
        faces = np.arange(np.array(vertexes).shape[0]).reshape(-1, 3)
        self.mesh.setMeshData(meshdata=gl.MeshData(faces=faces, vertexes=vertexes))
        self.mesh.update()
