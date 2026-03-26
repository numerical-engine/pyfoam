from pyfoam.mesh.core import coreMesher
import os
import shutil
from pyfoam.system.blockMeshDict import run_blockMesh, write_blockMeshDict
from pyfoam.system.meshQualityDict import write_meshQualityDict
from pyfoam import utils
import subprocess

class snappyHexMesh(coreMesher):
    """Mesh generator using snappyHexMesh.

    Attributes:
        boundary_types (dict[str,str]): Dictionary defining the boundary types.
        stlFile (str): Path to the STL file.
        blockmesh_props (dict[str, any]): Properties for the blockMeshDict which keys are,
            scale (float): Scale factor for blockMesh.
            x_range (tuple[float, float]): X-axis range for blockMesh.
            y_range (tuple[float, float]): Y-axis range for blockMesh.
            z_range (tuple[float, float]): Z-axis range for blockMesh.
            x_num (int): Number of cells in the X direction for blockMesh.
            y_num (int): Number of cells in the Y direction for blockMesh.
            z_num (int): Number of cells in the Z direction for blockMesh.
    """
    def __init__(self,
                boundary_types:dict[str,str],
                stlFile:str,
                locationInMesh:list[float],
                blockmesh_props:dict[str, any],
                stage_tag:dict[str, str] = {"castellatedMesh": "true", "snap": "true", "addLayers": "false"},
                castellatedMeshControls_props:dict = None,
                snapControls_prop:dict = None,
                addLayersControls_prop:dict = None,
                )->None:
        super().__init__(boundary_types)
        self.stlFile = stlFile
        self.stlName = self.stlFile.split("/")[-1][:-4]
        self.blockmesh_props = blockmesh_props
        self.stage_tag = stage_tag

        self.stl_surfacename = [key for key in self.boundary_types.keys() if key not in ("top", "bottom", "east", "west", "north", "south")]
        self.castellatedMeshControls_props = self.default_castellatedMeshControls(locationInMesh) if castellatedMeshControls_props is None else castellatedMeshControls_props
        self.snapControls_prop = self.default_snapControls() if snapControls_prop is None else snapControls_prop
        self.addLayersControls_prop = self.default_addLayersControls() if addLayersControls_prop is None else addLayersControls_prop

    def default_addLayersControls(self)->dict:
        return {
            "relativeSizes": "true",
            "layers":{},
            "expansionRatio": 1.0,
            "finalLayerThickness": 0.3,
            "minThickness": 0.1,
            "nGrow": 0,
            "featureAngle": 60,
            "slipFeatureAngle": 30,
            "nRelaxIter": 3,
            "nSmoothSurfaceNormals": 1,
            "nSmoothNormals": 3,
            "nSmoothThickness": 10,
            "maxFaceThicknessRatio": 0.5,
            "maxThicknessToMedialRatio": 0.3,
            "minMedialAxisAngle": 90,
            "nBufferCellsNoExtrude": 0,
            "nLayerIter": 50
        }

    def default_snapControls(self)->dict:
        return {
            "nSmoothPatch": 3,
            "tolerance": 2.0,
            "nSolveIter": 30,
            "nRelaxIter": 5,
            "nFeatureSnapIter": 10,
            "implicitFeatureSnap": "false",
            "explicitFeatureSnap": "true",
            "multiRegionFeatureSnap": "false"
        }

    def default_castellatedMeshControls(self, locationInMesh:list[float])->dict:
        
        
        return {
            "maxLocalCells" : 100000,
            "maxGlobalCells" : 2000000,
            "minRefinementCells" : 10,
            "maxLoadUnbalance" : 0.10,
            "nCellsBetweenLevels" : 2,
            "features" : " ( )", #Hard coding. Assuming no features.
            "refinementSurfaces":{
                self.stlName:{
                    "level":"(0 0)",
                    "regions":{
                        name:{
                            "level":"(0 0)",
                            "patchInfo":{
                                "type":self.boundary_types[name],
                            }
                        }
                        for name in self.stl_surfacename
                    }
                }
            },
            "resolveFeatureAngle" : 30.0,
            "refinementRegions" : {},
            "allowFreeStandingZoneFaces" : "true",
            "locationInMesh" : utils.tupleToDict(locationInMesh),
        }

    def write(self, case_dir:str)->None:
        os.makedirs(f"{case_dir}/constant/triSurface", exist_ok=False)
        shutil.copy2(self.stlFile, f"{case_dir}/constant/triSurface")

        boundary_types_blockMesh = {key:self.boundary_types[key] for key in ["top", "bottom", "north", "south", "east", "west"]}
        write_blockMeshDict(case_dir,
                            scale=self.blockmesh_props["scale"],
                            x_range=self.blockmesh_props["x_range"],
                            y_range=self.blockmesh_props["y_range"],
                            z_range=self.blockmesh_props["z_range"],
                            x_num=self.blockmesh_props["x_num"],
                            y_num=self.blockmesh_props["y_num"],
                            z_num=self.blockmesh_props["z_num"],
                            boundary_types=boundary_types_blockMesh)

        write_meshQualityDict(case_dir)
        with open(f"{case_dir}/system/snappyHexMeshDict", "w") as file:
            utils.write_format(file, {"version": 2.0, "format": "ascii", "class": "dictionary", "location": "system", "object": "snappyHexMeshDict"}, "FoamFile")
            file.write(f"castellatedMesh\t{self.stage_tag['castellatedMesh']};\n")
            file.write(f"snap\t{self.stage_tag['snap']};\n")
            file.write(f"addLayers\t{self.stage_tag['addLayers']};\n")
            utils.write_format(file, {f"{self.stlName}.stl": {"type": "triSurfaceMesh", "name":self.stlName}}, "geometry")
            utils.write_format(file, self.castellatedMeshControls_props, "castellatedMeshControls")
            utils.write_format(file, self.snapControls_prop, "snapControls")
            utils.write_format(file, self.addLayersControls_prop, "addLayersControls")
            file.write("meshQualityControls\n{\n")
            file.write("#include \"meshQualityDict\"\n")
            file.write("nSmoothScale\t4;\n")
            file.write("errorReduction\t0.75;\n")
            file.write("}\n")
            file.write("mergeTolerance\t1e-6;\n")
    
    def run(self, case_dir:str)->None:
        self.write(case_dir)
        run_blockMesh(case_dir)
        subprocess.run(["snappyHexMesh", "-case", case_dir, "-overwrite"], stdout=subprocess.DEVNULL)
    
    def get_boundary_names(self)->list[str]:
        boundary_names = ["top", "bottom", "north", "south", "east", "west"]

        if len(self.stl_surfacename) == 1:
            boundary_names.append(self.stlName)
        else:
            for stl_sn in self.stl_surfacename:
                boundary_names.append(f"{self.stlName}_{stl_sn}")
        
        return boundary_names