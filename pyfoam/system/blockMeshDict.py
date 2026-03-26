from pyfoam import utils
import subprocess

def write_blockMeshDict(
        case_dir:str,
        scale:float,
        x_range:list[float],
        y_range:list[float],
        z_range:list[float],
        x_num:int,
        y_num:int,
        z_num:int,
        boundary_types:dict[str, str],
        )->None:
    """blockMeshDictファイルを作成

    立方体領域かつ正方格子を作成する機能しかない。

    Args:
        case_dir (str): ケースディレクトリ
        scale (float): スケール値
        x_range (list[float]): x軸方向の範囲(x_min, x_max)。
        y_range (list[float]): y軸方向の範囲(y_min, y_max)。
        z_range (list[float]): z軸方向の範囲(z_min, z_max)。
        x_num (int): z軸方向のセル数
        y_num (int): y軸方向のセル数
        z_num (int): z軸方向のセル数
        boundary_types (dict[str, str]): 境界の種類を指定する辞書。キーは()"top", "bottom", "north", "south", "east", "west")であり、値はOpenFOAMの境界条件のタイプ。
    """
    with open(f"{case_dir}/system/blockMeshDict", "w") as file:
        utils.write_format(file, {
            "version" : 2.0,
            "format" : "ascii",
            "class" : "dictionary",
            "location" : "system",
            "object" : "blockMeshDict"}, 
            "FoamFile")
        file.write(f"scale\t{scale};\n")
        vertices = [
            utils.tupleToDict((x_range[0], y_range[0], z_range[0])),
            utils.tupleToDict((x_range[1], y_range[0], z_range[0])),
            utils.tupleToDict((x_range[1], y_range[1], z_range[0])),
            utils.tupleToDict((x_range[0], y_range[1], z_range[0])),
            utils.tupleToDict((x_range[0], y_range[0], z_range[1])),
            utils.tupleToDict((x_range[1], y_range[0], z_range[1])),
            utils.tupleToDict((x_range[1], y_range[1], z_range[1])),
            utils.tupleToDict((x_range[0], y_range[1], z_range[1])),
        ]
        utils.write_list(file, vertices, "vertices")
        utils.write_list(file, ["hex", "(0 1 2 3 4 5 6 7)", f"({x_num} {y_num} {z_num}) simpleGrading (1 1 1)"], "blocks")
        utils.write_list(file, [""], "edges")

        faces = {"top": (4,5,6,7), "bottom": (0,3,2,1), "north": (3,7,6,2), "south": (1,5,4,0), "east": (0,4,7,3), "west": (2,6,5,1)}
        assert set(faces.keys()).issubset(boundary_types.keys())
        file.write("boundary (\n")
        for key in boundary_types.keys():
            file.write(f"{key}{{")
            file.write(f"type\t{boundary_types[key]};")
            file.write("faces ( ")
            file.write(f"{utils.tupleToDict(faces[key])}")
            file.write(" );")
            file.write("}\n")
        file.write(" );\n")
        utils.write_list(file, [""], "mergePatchPairs")

def run_blockMesh(case_dir:str,)->None:
    """blockMeshを実行する。

    Args:
        case_dir (str): ケースディレクトリ

    Note:
        * OpenFOAMの仕様上、blockMeshDictとcontroldDictがない状態だとエラーになる。
    """
    subprocess.run(["blockMesh", "-case", case_dir], stdout=subprocess.DEVNULL)