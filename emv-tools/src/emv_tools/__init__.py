from . import scipion_bridge


def configure_default_environment():

    from .utils.providers.container import Container

    container = Container()
    container.wire(modules=[__name__, ".ffi.scipion"])
