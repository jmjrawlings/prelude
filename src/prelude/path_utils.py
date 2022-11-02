"""
File/Directory helpers
"""

from typing import Union
from pathlib import Path

FilePath = Path
DirPath = Path
PathLike = Union[str, Path]


def path(arg: PathLike, create=False, overwrite=False, directory=False, check_exists=True) -> Path:
    """
    Returns the given path

    create: bool
        If true, the file or dir will be created

    overwrite: bool
        If true, existing paths will be overwritten

    check_exists: bool
        If true, an exception will be thrown if the path does not exist
    """
    
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


def filepath(arg: PathLike, create=False, overwrite=False, check_exists=False) -> FilePath:
    """
    Returns the given file path
    """
    return path(arg, create=create, overwrite=overwrite, directory=False, check_exists=check_exists)


def dirpath(arg: PathLike, create=False, overwrite=False, check_exists=False):
    """
    Returns the given directory path
    """
    return path(arg, create=create, overwrite=overwrite, directory=True, check_exists=check_exists)


def existing_file(arg: PathLike, **kwargs) -> FilePath:
    """
    Returns the given filepath and ensures it exists
    """
    return filepath(arg, check_exists=True, **kwargs)


def existing_dir(arg: PathLike, **kwargs) -> DirPath:
    """
    Returns the given directory and ensures it exists
    """
    return dirpath(arg, check_exists=True, **kwargs)


def exists(arg: PathLike) -> bool:
    """
    Does the given path exist?
    """
    return path(arg).exists()    