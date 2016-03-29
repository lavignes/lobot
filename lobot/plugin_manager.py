from typing import List, Iterable, Tuple
from types import ModuleType
import importlib

from .plugins import Plugin
from .plugins.plugin import _Listener


class Module(object):
    @property
    def plugins(self) -> List[Plugin]:
        return self._plugins

    @property
    def module(self) -> ModuleType:
        return self._module

    def __init__(self, module: ModuleType):
        self._module = module
        self._plugins = []
        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, Plugin):
                self._plugins.append(obj())
        if len(self._plugins) == 0:
            raise ImportError('No plugins found in ' + module)


class PluginManager(object):
    @property
    def modules(self) -> Iterable[Tuple[str, Module]]:
        return self._modules.items()

    @property
    def plugins(self) -> List[Plugin]:
        plugins = []
        for path, module in self._modules.items():
            plugins += module.plugins
        return plugins

    def __init__(self):
        self._modules = {}

    def _import_new(self, module_path: str) -> Tuple[str, Module]:
        try: # Absolute import
            wrapped = Module(importlib.import_module(module_path))
        except ImportError:
            try: # Relative import
                module_path = 'lobot.plugins.' + module_path
                wrapped = Module(importlib.import_module(module_path))
            except ImportError:
                raise
        return module_path, wrapped

    def find_attributes(self, plugin: Plugin, attribute: str) -> List[_Listener]:
        return [method for method in plugin.__class__.__dict__.values() if hasattr(method, attribute)]

    def load_module(self, module_path: str) -> List[Plugin]:
        if module_path in self._modules:
            module = self._modules[module_path].module
            importlib.reload(module)
            wrapped = Module(module)
        else:
            module_path, wrapped = self._import_new(module_path)
        self._modules[module_path] = wrapped
        return wrapped.plugins
