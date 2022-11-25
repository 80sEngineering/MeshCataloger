import stl
import numpy

ball = stl.mesh.Mesh.from_file('Ball.stl')
cube = stl.mesh.Mesh.from_file('Cube.stl')

def combine(object1,object2):
    combined = stl.mesh.Mesh(numpy.concatenate([object1.data, object2.data]))
    combined.save('combined.stl', mode=stl.Mode.ASCII)