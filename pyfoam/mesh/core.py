class coreMesher:
    def __init__(self, boundary_types:dict[str, str]) -> None:
        self.boundary_types = boundary_types
    def write(self, case_dir:str)->None:
        raise NotImplementedError("This method should be implemented in subclasses.")
    def run(self, case_dir:str)->None:
        raise NotImplementedError("This method should be implemented in subclasses.")
    def clean(self, case_dir:str)->None:
        raise NotImplementedError("This method should be implemented in subclasses.")