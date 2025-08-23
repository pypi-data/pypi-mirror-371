import gmsh
import pathlib
import pygmsh


class GmshApi:

    def __init__(self):
        pass

    def __enter__(self):
        gmsh.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gmsh.finalize()


def remesh_file(
    file_path: pathlib.Path, surface_loops: list[set[int]], mesh_size: float
):
    with GmshApi():
        # read mesh file
        gmsh.merge(str(file_path))

        # create topology and geometry
        gmsh.model.mesh.createTopology()
        gmsh.model.mesh.createGeometry()

        # create surface loops
        for surface_ids in surface_loops:
            surface_loop = gmsh.model.geo.addSurfaceLoop(list(surface_ids))
            gmsh.model.geo.addVolume([surface_loop])

        # synchronize added surface loops
        gmsh.model.geo.synchronize()

        field_id = gmsh.model.mesh.field.add("MathEval", 1)
        gmsh.model.mesh.field.setString(field_id, "F", str(mesh_size))
        gmsh.model.mesh.field.setAsBackgroundMesh(field_id)

        # generate 3D mesh
        gmsh.model.mesh.generate(3)

        return pygmsh.helpers.extract_to_meshio()
