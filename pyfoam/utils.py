import _io

def write_format(file:_io.TextIOWrapper, data:dict, name:str, done:bool = True)->None:
    """Writes the formatted data to the given file.

    Args:
        file (_io.TextIOWrapper): The file to write.
        data (dict): The data to write.
        name (str): The name of the data block.
        done (bool, optional): Whether this is the last block. Defaults to True.
    """
    file.write(f"{name}{{")
    for key in data.keys():
        if isinstance(data[key], dict):
            write_format(file, data[key], key, done = False)
        else:
            file.write(f"{key} {data[key]};")
    file.write("}")
    if done:
        file.write("\n")

def tupleToDict(tup:tuple[int|float])->str:
    """Convert a tuple of integers or floats to a dictionary representation.

    Args:
        tup (tuple[int | float]): A tuple of integers or floats.
    Returns:
        str: A string representation of the dictionary.
    """
    s = "("
    for t in tup:
        s += f"{t} "
    s = s[:-1]+")"
    return s


def write_list(file:_io.TextIOWrapper, data:list[str], name:str)->None:
    s = name+" ( "
    for d in data[:-1]:
        assert isinstance(d, str), "All elements in the list must be strings."
        s += f"{d} "
    s += f"{data[-1]} );\n"
    file.write(s)