######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.3                                                                                 #
# Generated on 2025-08-21T22:44:50.402459                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

