"""
File/Directory helpers
"""

from typing import Union
from pathlib import Path

FilePath = Path
DirPath = Path

def path(arg: Union[str, Path], create=False, overwrite=False, directory=False, check_exists=True) -> Path:

    if isinstance(arg, Path):
        p = arg
    else:
        p = Path(arg)

    if create and (not p.exists() or overwrite):
        if directory:
            p.mkdir(parents=True, exist_ok=overwrite)
        else:
            p.touch(exist_ok=overwrite)

    if check_exists and not p.exists():
        raise FileNotFoundError(f'The path {p} does not exist')

    if p.exists() and directory and not p.is_dir():
        raise ValueError(f'Path {p} is not a directory')

    return p


def filepath(arg: Union[str, Path], create=False, overwrite=False, check_exists=False) -> FilePath:
    return path(arg, create=create, overwrite=overwrite, directory=False, check_exists=check_exists)


def dirpath(arg: Union[str, Path], create=False, overwrite=False, check_exists=False):
    return path(arg, create=create, overwrite=overwrite, directory=True, check_exists=check_exists)


def existing_file(arg, **kwargs) -> FilePath:
    return filepath(arg, check_exists=True, **kwargs)


def existing_dir(arg, **kwargs) -> DirPath:
    return dirpath(arg, check_exists=True, **kwargs)


def exists(arg):
    return path(arg).exists()    