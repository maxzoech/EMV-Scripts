import os
import inspect
import tempfile
import logging

from functools import wraps
from typing import Optional, List

from collections import namedtuple

from .func_params import extract_func_params

class Proxy:
    def __init__(self, file_ext):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False)

    @property
    def path(self):
        return self.temp_file.name
    
    @classmethod
    def proxy_for_lines(cls, lines: List[str], *, file_ext):
        proxy = Proxy(file_ext)
        with open(proxy.temp_file.name, "w") as f:
            f.write("".join(lines))

        return proxy

    def __del__(self):
        try:
            os.remove(self.temp_file.name)
            # print(f"Removed file at: {self.temp_file.name}")
        except:
            pass # Fail silently

OutputInfo = namedtuple("OutputInfo", ["file_ext"])

def _replace_with_proxy(name, value):
    if isinstance(value, Proxy):
        return value
    
    if isinstance(value, OutputInfo):
        new_proxy = Proxy(file_ext=value.file_ext)
        return new_proxy
    
    raise ValueError(f"Value for {name} must be a Proxy or OutputInfo object if map_outputs=True")


def proxify(f, map_inputs=True, map_outputs=True):
    
    signature = inspect.signature(f)

    @wraps(f)
    def wrapper(*args, **kwargs):

        func_args = extract_func_params(args, kwargs, signature.parameters)
        func_args = { k.name: v for k, v in func_args.items() }

        # Replace input proxy objects with their path
        if map_inputs:
            func_args = { k: v.path if isinstance(v, Proxy) else v for k, v in func_args.items() }

        output_proxies = []
        if map_outputs:
            func_args = { k: Proxy(v.file_ext) if isinstance(v, OutputInfo) else v for k, v in func_args.items() }

            for k, v in func_args.items():
                if isinstance(v, Proxy):
                    output_proxies.append(v)
                    func_args[k] = v.path

        print(func_args)


        out_val = f(**func_args)
        if not (out_val == 0 or out_val == None):
            logging.warning(
                f"Wrapped function returns non-zero value; this value {out_val} will be discared"
            )

        if len(output_proxies) == 0:
            return None
        elif len(output_proxies):
            return output_proxies[0]
        else:
            return tuple(output_proxies)
        
    return wrapper