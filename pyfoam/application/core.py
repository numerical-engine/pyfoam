import os
import subprocess

from pyfoam import utils

class coreFoam:
    phys_values = None
    application = None
    def __init__(self,
        case_dir:str,
        mesher:"Mesher",
        phys_values_init:dict[str, any],
        control_props:dict = None,
        fvSchemes_props:dict = None,
        fvSolution_props:dict = None)->None:

        self.case_dir = case_dir
        self.mesher = mesher
        self.control_props = self.default_controlDict() if control_props is None else control_props
        self.fvSchemes_props = self.default_fvSchemes() if fvSchemes_props is None else fvSchemes_props
        self.fvSolution_props = self.default_fvSolution() if fvSolution_props is None else fvSolution_props
        self.phys_values_init = phys_values_init

        self.boundaryConditions = {
            phys_v:{
                boundary_n:{
                    "type":None,
                }
                for boundary_n in self.mesher.get_boundary_names()
            }
            for phys_v in self.phys_values
        }
    
    def default_controlDict(self)->dict:
        raise NotImplementedError("Method 'default_controlDict' must be implemented in subclasses.")
    def default_fvSchemes(self)->dict[dict]:
        raise NotImplementedError("Method 'default_fvSchemes' must be implemented in subclasses.")
    def default_fvSolution(self)->dict[dict]:
        raise NotImplementedError("Method 'default_fvSolution' must be implemented in subclasses.")
    
    def set_controlDict(self, category:str, value:any)->None:
        self.control_props[category] = value

    def set_boundaryCondition(self, phys_v:str, boundary_n:str, b_type:str, value:str = None)->None:
        self.boundaryConditions[phys_v][boundary_n]["type"] = b_type
        if value is not None:
            self.boundaryConditions[phys_v][boundary_n]["value"] = value
    
    def create_dir(self)->None:
        """Create the necessary directories for the case.
        """
        os.makedirs(f"{self.case_dir}/constant", exist_ok=True)
        os.makedirs(f"{self.case_dir}/system", exist_ok=True)
        os.makedirs(f"{self.case_dir}/0", exist_ok=False)
    
    def create_mesh(self)->None:
        self.mesher.run(self.case_dir)
    
    def write_fvSchemes(self)->None:
        with open(f"{self.case_dir}/system/fvSchemes", "w") as file:
            utils.write_format(file, {"version" : 2.0, "format" : "ascii", "class" : "dictionary", "location" : "system", "object" : "fvSchemes"}, "FoamFile")
            for key, value in self.fvSchemes_props.items():
                utils.write_format(file, value, key)

    def write_fvSolution(self)->None:
        with open(f"{self.case_dir}/system/fvSolution", "w") as file:
            utils.write_format(file, {"version" : 2.0, "format" : "ascii", "class" : "dictionary", "location" : "system", "object" : "fvSolution"}, "FoamFile")
            for key, value in self.fvSolution_props.items():
                utils.write_format(file, value, key)
    
    def write_controlDict(self)->None:
        with open(f"{self.case_dir}/system/controlDict", "w") as file:
            utils.write_format(file, {"version" : 2.0, "format" : "ascii", "class" : "dictionary", "location" : "system", "object" : "controlDict"}, "FoamFile")
            file.write(f"application\t{self.application};\n")
            file.write(f"startFrom\t{self.control_props['startFrom']};\n")
            if self.control_props['startFrom'] == "startTime":
                file.write(f"startTime\t{self.control_props['startTime']};\n")
            file.write(f"stopAt\t{self.control_props['stopAt']};\n")
            if self.control_props['stopAt'] == "endTime":
                file.write(f"endTime\t{self.control_props['endTime']};\n")
            file.write(f"deltaT\t{self.control_props['deltaT']};\n")
            file.write(f"writeControl\t{self.control_props['writeControl']};\n")
            file.write(f"writeInterval\t{self.control_props['writeInterval']};\n")
            file.write(f"purgeWrite\t{self.control_props['purgeWrite']};\n")
            file.write(f"writeFormat\t{self.control_props['writeFormat']};\n")
            file.write(f"writePrecision\t{self.control_props['writePrecision']};\n")
            file.write(f"writeCompression\t{self.control_props['writeCompression']};\n")
            file.write(f"timeFormat\t{self.control_props['timeFormat']};\n")
            file.write(f"timePrecision\t{self.control_props['timePrecision']};\n")
            file.write(f"runTimeModifiable\t{self.control_props['runTimeModifiable']};\n")
    
    def write_transportProperties(self)->None:
        raise NotImplementedError("Method 'write_transportProperties' must be implemented in subclasses.")
    
    def write_initial_conditions(self)->None:
        raise NotImplementedError("Method 'write_initial_conditions' must be implemented in subclasses.")

    def setup(self)->None:
        self.create_dir()
        self.write_fvSchemes()
        self.write_fvSolution()
        self.write_controlDict()
        self.write_transportProperties()
        self.write_initial_conditions()
    
    def run(self, show_log:bool = False)->None:
        if show_log:
            subprocess.run([self.application, "-case", self.case_dir])
        else:
            subprocess.run([self.application, "-case", self.case_dir], stdout=subprocess.DEVNULL)


class coreFoam_steady(coreFoam):
    def default_controlDict(self):
        return {
            "startFrom" : "startTime",
            "startTime" : 0,
            "stopAt" : "endTime",
            "endTime" : 1000,
            "deltaT" : 1,
            "writeControl" : "timeStep",
            "writeInterval" : 1,
            "purgeWrite" : 1,
            "writeFormat" : "ascii",
            "writePrecision" : 6,
            "writeCompression" : "off",
            "timeFormat" : "general",
            "timePrecision" : 6,
            "runTimeModifiable" : "true"
        }

class coreFoam_transient(coreFoam):
    def default_controlDict(self):
        return {
            "startFrom" : "latestTime",
            "startTime" : 0,
            "stopAt" : "endTime",
            "endTime" : 1.0,
            "deltaT" : 0.01,
            "writeControl" : "timeStep",
            "writeInterval" : 1,
            "purgeWrite" : 0,
            "writeFormat" : "ascii",
            "writePrecision" : 6,
            "writeCompression" : "off",
            "timeFormat" : "general",
            "timePrecision" : 6,
            "runTimeModifiable" : "true"
        }