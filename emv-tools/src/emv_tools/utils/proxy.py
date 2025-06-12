import os
import inspect
import tempfile
import logging

from functools import wraps
from typing import Optional

from collections import namedtuple

from .func_params import extract_func_params

class Proxy:
    def __init__(self, file_ext):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False)

    @property
    def path(self):
        return self.temp_file.name

    def __del__(self):
        try:
            os.remove(self.temp_file.name)
            # print(f"Removed file at: {self.temp_file.name}")
        except:
            pass # Fail silently


OutputInfo = namedtuple("OutputInfo", ["arg_name", "file_ext"])

def proxify(f, outputs = None, discard_returned=None):
    
    signature = inspect.signature(f)

    def wrapper(*args, **kwargs):

        func_args = extract_func_params(args, kwargs, signature.parameters)
        func_args = { k.name: v for k, v in func_args.items() }

        # Replace proxy objects with their path
        func_args = { k: v.path if isinstance(v, Proxy) else v for k, v in func_args.items() }

        if outputs is not None:
            output_proxy = Proxy(outputs.file_ext)
            func_args[outputs.arg_name] = output_proxy.path


        out_val = f(**func_args)
        if outputs is None:
            return out_val
        else:
            if not (out_val == 0 or out_val == None) and not discard_returned == True:
                logging.warning(
                    f"Wrapped function returns non-zero value; this value {out_val} will be discared. Set discard_returned to True to silence this warning."
                )

            return output_proxy
    
    return wrapper