# dynamic_init.py
import os
import sys
import types
import importlib
import importlib.util
import inspect
from functools import lru_cache

def _module_of(obj):
    try:
        return inspect.getmodule(obj)
    except Exception:
        return None

def _callables_defined_in(mod: types.ModuleType):
    names = []
    for n in dir(mod):
        if n.startswith("_"):
            continue
        obj = getattr(mod, n, None)
        if callable(obj) and _module_of(obj) is mod:
            names.append(n)
    return sorted(set(names))

@lru_cache(maxsize=256)
def _resolve_functions_module_name(base_pkg: str) -> str | None:
    """
    Try importing '<base_pkg>.functions' as a normal module/package.
    Returns its module name if importable, else None.
    """
    try:
        importlib.import_module(f"{base_pkg}.functions")
        return f"{base_pkg}.functions"
    except Exception:
        return None

def _load_functions_module_by_path(base_pkg: str) -> types.ModuleType | None:
    """
    Fallback: load sibling 'functions.py' by file path if not a package import.
    """
    try:
        base_mod = importlib.import_module(base_pkg)
        base_dir = os.path.dirname(base_mod.__file__)
    except Exception:
        return None

    fn_py = os.path.join(base_dir, "functions.py")
    if not os.path.isfile(fn_py):
        return None

    spec = importlib.util.spec_from_file_location(f"{base_pkg}.functions", fn_py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def attach_functions(self, *, base_pkg: str | None = None, hot_reload: bool = False):
    """
    Attach all functions exported by '<base_pkg>.functions' to 'self'.
    If base_pkg is None, infer from the class' module (sibling 'functions').
    """
    if base_pkg is None:
        # infer sibling package of the class' module
        cls_mod = self.__class__.__module__
        base_pkg = cls_mod.rsplit(".", 1)[0] if "." in cls_mod else cls_mod

    modname = _resolve_functions_module_name(base_pkg)
    mod = None

    if modname:
        mod = importlib.import_module(modname)
    else:
        mod = _load_functions_module_by_path(base_pkg)

    if mod is None:
        # Nothing to attach; leave a breadcrumb
        setattr(self, "_init_funcs_error", f"No functions module found for {base_pkg}")
        return self

    if hot_reload:
        try:
            mod = importlib.reload(mod)
        except Exception:
            pass

    names = getattr(mod, "__all__", None)
    if not names:
        names = _callables_defined_in(mod)

    for name in names:
        fn = getattr(mod, name, None)
        if callable(fn):
            setattr(self, name, fn)

    return self
