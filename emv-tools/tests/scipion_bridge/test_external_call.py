from emv_tools.scipion_bridge.external_call import foreign_function

from emv_tools.utils.providers.container import Container
from pytest_mock import MockerFixture


@foreign_function
def xmipp_to_something(inputs: str, outputs: str, *, keyword_param: int) -> int:
    pass


def test_basic_foreign_function(mocker: MockerFixture):

    container = Container()
    container.wire(modules=[__name__])

    exec_mock = mocker.Mock()

    with container.shell_exec.override(exec_mock):
        xmipp_to_something("/some/input", "/some/output", keyword_param=42)

        exec_mock.assert_called_with(
            "xmipp_to_something",
            [
                "scipion",
                "run",
                "xmipp_to_something",
                "-inputs",
                "/some/input",
                "-outputs",
                "/some/output",
                "--keyword_param",
                "42",
            ],
            {"shell": True, "stderr": -1},
        )


if __name__ == "__main__":
    test_basic_foreign_function()
