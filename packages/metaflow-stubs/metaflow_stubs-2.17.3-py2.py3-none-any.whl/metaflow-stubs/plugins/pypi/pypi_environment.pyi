######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.3                                                                                 #
# Generated on 2025-08-21T22:44:50.385268                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

