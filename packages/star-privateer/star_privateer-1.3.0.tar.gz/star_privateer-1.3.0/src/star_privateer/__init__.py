from importlib.metadata import version

__version__ = version ('star_privateer')

from .rotation_pipeline import *

from .wavelets import *

from .correlation import *

from .lomb_scargle import *

from .rooster import *

from .aux import *

from .morphology import *

import star_privateer.timeseries 

import star_privateer.catalogs 

import star_privateer.rooster_instances 

import star_privateer.constants 

import sys, os
if sys.version_info < (3, 9):
    import importlib_resources as resources
else :
    from importlib import resources

def normalize_path(path):
    # type: (Any) -> str
    """Normalize a path by ensuring it is a string.

    If the resulting string contains path separators, an exception is raised.
    """
    str_path = str(path)
    parent, file_name = os.path.split(str_path)
    if parent:
        raise ValueError(f'{path!r} must be only a file name')
    return file_name

def internal_path (package, resource) :
  """
  A context manager providing a file path object to the resource.

  If the resource does not already exist on its own on the file system,
  a temporary file will be created. If the file was created, the file
  will be deleted upon exiting the context manager (no exception is
  raised if the file was deleted prior to the context manager
  exiting).

  See:
  https://github.com/python/importlib_resources/blob/66ea2dc7eb12b1be2322b7ad002cefb12d364dff/importlib_resources/_legacy.py
  """ 
  return resources.as_file(resources.files(package) / normalize_path(resource))
