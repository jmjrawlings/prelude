from typing import Union, Any
from pathlib import Path

FilePath = Path
DirPath = Path

def path(arg: Union[str, Path], create=True, overwrite=False, directory=False) -> Path:
    if isinstance(arg, Path):
        return arg
    else:
        return Path(arg)


def filepath(arg: Union[str, Path], create=True, overwrite=True):
    return path(arg, create=create, overwrite=overwrite, directory=False)


def dirpath(arg: Union[str, Path], create=True, overwrite=True):
    return path(arg, create=create, overwrite=overwrite, directory=True)
