import os
import sys
import subprocess

import ast
import inspect
from typing import Dict, Any, Callable

import itertools
import functools
from functools import partial

class ScipionFunction:
    def __init__(self, f: Callable, args_map: Dict[str, str]):

        args = inspect.signature(f)

        self.func = f
        self.arg_names = [args_map[arg.name] if arg.name in args_map else arg.name for arg in args.parameters.values()]

        functools.update_wrapper(self, f)
    
    def __call__(self, *args, **kwargs) -> int:
        
        args_dict = dict(zip(self.arg_names, args))
        args_dict = {
            **args_dict,
            **kwargs
        }
        
        raw_args = itertools.chain.from_iterable([["--"+k, v] for k, v in args_dict.items()])

        print("Would run scipion call with")
        # 


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

def external(f, args_map=None, **run_args):
    is_empty = _func_is_empty(f)
    if not is_empty:
        raise RuntimeError(f"Forward declared external Scipion function {f.__name__} must be only contain a single pass statement.")

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
            "scipion", "run", *raw_args
        ]

        # cmd = " ".join(raw_args)
        return subprocess.run(raw_args, **run_args)

    return wrapper


@partial(external, args_map={"output": "o", "volume": "vol"}, shell=False)
def xmipp_pdb_label_from_volume(output, *, pdb, volume, mask, sampling, origin="default_origin"):
    pass


def main():
    
    exit_code = xmipp_pdb_label_from_volume(
        "/dev/null/deepres/atom.pub",
        pdb="pdb_path",
        volume="volume_path",
        mask="mask_path",
        sampling="sampling_path",
        origin="origin"
    )

    print("returned> ", exit_code)

#     # subprocess.run(["scipion", "run", "xmipp_pdb_label_from_volume"])

#     # os.system(
#     #     'scipion3'
#     # )

if __name__ == "__main__":
    main()