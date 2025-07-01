from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from .cmd_exec import ShellExecProvider

class Container(containers.DeclarativeContainer):
    
    config = providers.Configuration()

    shell_exec = providers.Factory(
        ShellExecProvider
    )