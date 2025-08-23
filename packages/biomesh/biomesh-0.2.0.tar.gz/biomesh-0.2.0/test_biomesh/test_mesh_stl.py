import biomesh
import pathlib
import meshio
import pytest

_my_script_dir = pathlib.Path(__file__).parent


def test_combine_stl():
    mesh = biomesh.combine_colored_stl_files(
        _my_script_dir / "data" / "p1.stl",
        _my_script_dir / "data" / "p2.stl",
        _my_script_dir / "data" / "p3.stl",
    )

    meshio.write("test.mesh", mesh)


def test_mesh_stl():

    mesh = biomesh.mesh_colored_stl_files(
        _my_script_dir / "data" / "p1.stl",
        _my_script_dir / "data" / "p2.stl",
        _my_script_dir / "data" / "p3.stl",
        mesh_size=2.0,
    )

    assert mesh.cells_dict["line"].shape[0] == pytest.approx(482, 10)
    assert mesh.cells_dict["line"].shape[1] == 2

    assert mesh.cells_dict["triangle"].shape[0] == pytest.approx(23047, 1000)
    assert mesh.cells_dict["triangle"].shape[1] == 3

    assert mesh.cells_dict["tetra"].shape[0] == pytest.approx(77869, 1000)
    assert mesh.cells_dict["tetra"].shape[1] == 4

    assert mesh.points.shape[0] == pytest.approx(18000, 1000)
    assert mesh.points.shape[1] == 3
