import os
import pytest
import tempfile
from emv_tools.scipion_bridge.environment.cmd_exec import ShellExecProvider
from subprocess import PIPE


def test_shell_exec():

    provider = ShellExecProvider()

    output = provider(
        "python",
        [
            "python",
            "-c",
            '"import sys; sys.exit(0)"',
        ],
        run_args={"shell": True, "stdout": PIPE, "stderr": PIPE},
    )

    assert output == 0

    with pytest.raises(RuntimeError):
        output = provider(
            "python",
            [
                "python",
                "-c",
                '"import sys; sys.exit(42)"',
            ],
            run_args={"shell": True, "stdout": PIPE, "stderr": PIPE},
        )
