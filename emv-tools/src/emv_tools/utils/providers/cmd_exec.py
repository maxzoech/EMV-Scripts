from typing import List
from subprocess import Popen, PIPE


class ShellExecProvider:

    def run(self, func_name, args: List[str], run_args):
        cmd = " ".join(args)
        proc = Popen(cmd, **run_args)
        _, err = proc.communicate()  # Blocks until finished
        if proc.returncode != 0:

            message = err.decode("utf-8")
            error_msg = f"{message}\nExternal call to {func_name} failed with exit code {proc.returncode}"

            raise RuntimeError(error_msg)

        return proc.returncode