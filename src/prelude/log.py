import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
FORMAT = "%(levelname)s|%(pathname)s:%(lineno)d|%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(
        omit_repeated_times=False,
        markup=True,
        rich_tracebacks=True,
        show_level=False,
        show_time=False
    )]
)

def get(name=''):
    return logging.getLogger(name)

default = logging.getLogger("rich")

info = default.info
err = default.error
warning = default.warning
exc = default.exception
debug = default.debug