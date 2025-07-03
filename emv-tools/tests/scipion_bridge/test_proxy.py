import os

from emv_tools.scipion_bridge.proxy import proxify, OutputInfo, TempFileProxy
from emv_tools.utils.providers.container import Container


class TempFileMock:
    def new_temporary_file(self, suffix: str) -> os.PathLike:
        return f"/tmp/temporary_proxy_file{suffix}"

    def delete(path: os.PathLike):
        pass


def test_proxify():

    @proxify
    def foo(path: str):
        assert path == "/tmp/temporary_proxy_file.vol"

    container = Container()
    container.wire(modules=[__name__])

    temp_file_mock = TempFileMock()

    with container.temp_file_provider.override(temp_file_mock):
        foo(TempFileProxy("vol"))


def test_output_proxy():
    @proxify
    def foo(output: str):
        with open(output, mode="w+") as f:
            f.write("Hello, output!")

    container = Container()
    container.wire(modules=[__name__])

    temp_file_mock = TempFileMock()
    with container.temp_file_provider.override(temp_file_mock):
        output = foo(OutputInfo("txt"))
        assert output.path == "/tmp/temporary_proxy_file.txt"

        with open(output.path) as f:
            assert f.read() == "Hello, output!"


def test_proxy_attr():
    container = Container()
    container.wire(modules=[__name__])

    temp_file_mock = TempFileMock()

    with container.temp_file_provider.override(temp_file_mock):
        assert (
            str(TempFileProxy("vol"))
            == "<TempFileProxy for /tmp/temporary_proxy_file.vol (owned)>"
        )
