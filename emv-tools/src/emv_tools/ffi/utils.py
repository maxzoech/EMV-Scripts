import os
import sys
from subprocess import Popen, PIPE

import ast
import inspect
from typing import Dict, Any, Callable

import itertools
import functools
from functools import partial

class ScipionError(Exception):

    def __init__(self, returncode: int, message: str, func_name: str):
        super().__init__()

        self.returncode = returncode
        self.message = message
        self.func_name = func_name

    def __str__(self):
        return f"{self.message}\nExternal call to {self.func_name} failed with exit code {self.returncode}"


def _func_is_empty(func):

    source = inspect.getsource(func)
    tree = ast.parse(source)
    
    # Find the function definition in the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body = node.body

            return len(body) == 1 and isinstance(body[0], ast.Pass)
    
    return False  # In case no FunctionDef was found


def _param_to_cmd_args(param: inspect.Parameter):
    is_keyword = param.kind == inspect.Parameter.KEYWORD_ONLY
    prefix = "--" if is_keyword else "-"

    return prefix+param.name

def foreign_function(f, args_map=None, **run_args):
    is_empty = _func_is_empty(f)
    if not is_empty:
        raise RuntimeError(f"Forward declared external scipion function {f.__name__} must be only contain a single pass statement.")

    run_args.setdefault("shell", True)
    # run_args["stdout"]=PIPE
    run_args["stderr"]=PIPE

    if args_map is None:
        args_map = {}

    params = inspect.signature(f)
    params = {k: param.replace(name=args_map[k]) if k in args_map else param for k, param in params.parameters.items()}

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        _ = f(*args, **kwargs) # Call function for Python to throw error if args and kwargs aren't passed correctly

        defaults = {
            k: param
            for k, param in params.items()
            if param.default is not param.empty
        }

        args_dict = dict(zip(params.values(), args))
        kwargs_dict = { params[k]: v for k, v in kwargs.items() }

        merged_args = {
            **args_dict,
            **kwargs_dict,
        }

        for v in defaults.values():
            merged_args.setdefault(v, v.default)
        
        raw_args = [[_param_to_cmd_args(p), v] for p, v in merged_args.items()]
        raw_args = itertools.chain.from_iterable(raw_args)
        
        raw_args = [
            "scipion", "run", f.__name__, *raw_args
        ]

        cmd = " ".join(raw_args)
        proc = Popen(cmd, **run_args)
        _, err = proc.communicate() # Blocks until finished
        if proc.returncode != 0:
            raise ScipionError(proc.returncode, err.decode("utf-8"), f.__name__)
        
        return proc.returncode

    return wrapper

__all__ = [
    foreign_function
]
