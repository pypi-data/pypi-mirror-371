######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.1.0+obcheckpoint(0.2.4);ob(v1)                                                    #
# Generated on 2025-08-21T17:03:57.353681                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from .exception import MetaflowException as MetaflowException

class PyLintWarn(metaflow.exception.MetaflowException, metaclass=type):
    ...

class PyLint(object, metaclass=type):
    def __init__(self, fname):
        ...
    def has_pylint(self):
        ...
    def run(self, logger = None, warnings = False, pylint_config = []):
        ...
    ...

