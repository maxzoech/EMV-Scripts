import os

from emv_tools.scipion_bridge.proxy import proxify, OutputInfo, TempFileProxy
from emv_tools.utils.providers.container import Container


class TempFileMock:

    def __init__(self):
        self.count = 0

    def new_temporary_file(self, suffix: str) -> os.PathLike:
        file = f"/tmp/temp_file_{self.count}{suffix}"
        self.count += 1

        return file

    def delete(path: os.PathLike):
        pass


def test_proxify():

    @proxify
    def foo(path: str):
        assert path == "/tmp/temp_file_0.vol"

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
        assert output.path == "/tmp/temp_file_0.txt"

        with open(output.path) as f:
            assert f.read() == "Hello, output!"


def test_multi_output_proxy():

    @proxify
    def foo(output_1, output_2):
        pass

    container = Container()
    container.wire(modules=[__name__])

    temp_file_mock = TempFileMock()
    with container.temp_file_provider.override(temp_file_mock):
        output = foo(OutputInfo("vol"), OutputInfo("vol"))

        assert output[0].path == "/tmp/temp_file_0.vol"
        assert output[1].path == "/tmp/temp_file_1.vol"


def test_proxy_attr():
    container = Container()
    container.wire(modules=[__name__])

    temp_file_mock = TempFileMock()

    with container.temp_file_provider.override(temp_file_mock):
        assert (
            str(TempFileProxy("vol"))
            == "<TempFileProxy for /tmp/temp_file_0.vol (owned)>"
        )
