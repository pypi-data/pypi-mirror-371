import importlib.metadata

import simtoolsz.mail as mail
import simtoolsz.utils as utils


try:
    __version__ = importlib.metadata.version("simtoolsz")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.6"

__all__ = [
    '__version__', 'mail', 'utils'

]