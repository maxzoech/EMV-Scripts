import os
import shutil

import inspect
import tempfile
import logging

from functools import wraps
from typing import Optional, List

from collections import namedtuple

from .func_params import extract_func_params


class Proxy:
    def __init__(self, owned=False):
        self.owned = owned

    @property
    def path(self):
        raise NotImplementedError("Implement in subclass")
    
    def __del__(self):
        try:
            if self.owned == True:
                os.remove(self.path)
                print(f"Removed file at: {self.path}")
        except:
            pass # Fail silently

    def __str__(self):
        is_owned = "owned" if self.owned else "unowned"
        return f"<{self.__class__.__name__} for {self.path} ({is_owned})>"


class TempFileProxy(Proxy):
    def __init__(self, file_ext=None):
        super().__init__(owned=True)
        self.file_ext = file_ext

        suffix = "" if file_ext is None else f".{file_ext}"
        self.temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)

    @property
    def path(self):
        return self.temp_file.name
    
    @classmethod
    def proxy_for_lines(cls, lines: List[str], *, file_ext):
        proxy = TempFileProxy(file_ext)
        with open(proxy.temp_file.name, "w") as f:
            f.write("".join(lines))

        return proxy
    
    def reasign(self, new_ext: str):
        assert self.file_ext is None

        new_path = self.path + f".{new_ext}"
        if not os.path.exists(new_path):
            raise FileNotFoundError(f"No file found at '{new_path}'. Make sure the file extension matches. \
                                    If the external program writes files to a different known location, \
                                    initialize ReferenceProxy directly.")
    
        return ReferenceProxy(new_path, owned=True)

class ReferenceProxy(Proxy):
    def __init__(self, path: os.PathLike, owned=False):
        super().__init__(owned)
        self._path = path

    @property
    def path(self):
        return self._path


OutputInfo = namedtuple("OutputInfo", ["file_ext"])

def _replace_with_proxy(name, value):
    if isinstance(value, Proxy):
        return value
    
    if isinstance(value, OutputInfo):
        new_proxy = TempFileProxy(file_ext=value.file_ext)
        return new_proxy
    
    raise ValueError(f"Value for {name} must be a Proxy or OutputInfo object if map_outputs=True")


def proxify(f, map_inputs=True, map_outputs=True):

    signature = inspect.signature(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f.__wrapped__(*args, **kwargs)
        except AttributeError as e:
            logging.warning(
                "Could not check function arguments at call site; this" \
                "may lead to undefined behaviour and may be due " \
                "to an additional function wrapper: Please make sure to " \
                "decorate your wrapper with @functools.wraps(f)"
            )

        func_args = extract_func_params(args, kwargs, signature.parameters)
        func_args = { k.name: v for k, v in func_args.items() }

        # Replace input proxy objects with their path
        if map_inputs:
            func_args = { k: v.path if isinstance(v, Proxy) else v for k, v in func_args.items() }

        output_proxies = []
        if map_outputs:
            func_args = { k: TempFileProxy(v.file_ext) if isinstance(v, OutputInfo) else v for k, v in func_args.items() }

            for k, v in func_args.items():
                if isinstance(v, Proxy):
                    output_proxies.append(v)
                    func_args[k] = v.path


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