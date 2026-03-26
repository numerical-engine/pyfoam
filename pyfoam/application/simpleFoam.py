from pyfoam.application.core import coreFoam_steady
from pyfoam import utils

class simpleFoam(coreFoam_steady):
    """simpleFoamによる定常層流解析
    """
    phys_values = ("p", "U")
    application = "simpleFoam"
    def __init__(self,
                case_dir: str,
                mesher:"Mesher",
                phys_values_init:dict[str, any],
                nu:float = 1.5e-05,
                control_props:dict = None,
                fvSchemes_props:dict = None,
                fvSolution_props:dict = None,
                ) -> None:
        super().__init__(case_dir, mesher, phys_values_init, control_props, fvSchemes_props, fvSolution_props)
        self.nu = nu
    
    def default_fvSchemes(self)->dict[dict]:
        return {
            "ddtSchemes": {"default": "steadyState"},
            "gradSchemes": {"default":"Gauss linear"},
            "divSchemes": {"default":"none", "div(phi,U)":"bounded Gauss linearUpwind grad(U)", "div((nuEff*dev2(T(grad(U)))))":"Gauss linear"},
            "laplacianSchemes": {"default":"Gauss linear corrected"},
            "interpolationSchemes": {"default":"linear"},
            "snGradSchemes": {"default":"corrected"},
        }
    
    def default_fvSolution(self)->dict[dict]:
        return {
            "solvers":{
                "p":{"solver":"GAMG", "smoother":"GaussSeidel", "tolerance":1e-06, "relTol":0.1},
                "U":{"solver":"smoothSolver", "smoother":"symGaussSeidel", "tolerance":1e-05, "relTol":0.1},
            },
            "SIMPLE":{
                "consistent":"yes",
                "nNonOrthogonalCorrectors":0,
                "residualControl":{"p":1e-2, "U":1e-3}},
            "relaxationFactors":{"equations":{"p":0.9, "U":0.9}}
        }
    
    def write_transportProperties(self)->None:
        with open(f"{self.case_dir}/constant/transportProperties", "w") as file:
            utils.write_format(file, {"version": 2.0, "format": "ascii", "class": "dictionary", "location": "constant", "object": "transportProperties"}, "FoamFile")
            file.write("transportModel\tNewtonian;\n")
            file.write(f"nu\t{self.nu};")
    
    def write_initial_conditions(self)->None:
        with open(f"{self.case_dir}/0/U", "w") as file:
            utils.write_format(file, {"version": 2.0, "format": "ascii", "class": "volVectorField", "location": "0", "object": "U"}, "FoamFile")
            file.write("dimensions\t[0 1 -1 0 0 0 0];\n")
            file.write(f"internalField\tuniform {utils.tupleToDict(self.phys_values_init['U'])};\n")

            utils.write_format(file, self.boundaryConditions["U"], "boundaryField")
        
        with open(f"{self.case_dir}/0/p", "w") as file:
            utils.write_format(file, {"version": 2.0, "format": "ascii", "class": "volScalarField", "location": "0", "object": "p"}, "FoamFile")
            file.write("dimensions\t[0 2 -2 0 0 0 0];\n")
            file.write(f"internalField\tuniform {self.phys_values_init['p']};\n")
            utils.write_format(file, self.boundaryConditions["p"], "boundaryField")
        
    def write_momentumTransport(self)->None:
        with open(f"{self.case_dir}/constant/momentumTransport", "w") as file:
            utils.write_format(file, {"version": 2.0, "format": "ascii", "class": "dictionary", "location": "constant", "object": "momentumTransport"}, "FoamFile")
            file.write("simulationType\tlaminar;\n")
            utils.write_format(file, {"turbulence": "off"}, "RAS")
    
    def setup(self)->None:
        super().setup()
        self.write_momentumTransport()