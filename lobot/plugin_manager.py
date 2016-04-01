from typing import List, Iterable, Tuple
from types import ModuleType
import importlib

from .plugins import Plugin
from .plugins.plugin import _Listener


__all__ = [
    'Module',
    'PluginManager'
]


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
        for cls in module.__dict__.values():
            if isinstance(cls, type) and issubclass(cls, Plugin):
                self._plugins.append(cls())
        if len(self._plugins) == 0:
            raise ImportError('No plugins found in ' + module)


class PluginManager(object):
    @property
    def modules(self) -> Iterable[Tuple[str, Module]]:
        return self._modules.items()

    @property
    def plugins(self) -> List[Plugin]:
        plugins = []
        for module_path, module in self._modules.items():
            plugins += module.plugins
        return plugins

    def __init__(self):
        self._modules = {}

    def find_attributes(self, plugin: Plugin, attribute: str) -> List[_Listener]:
        return [method for method in plugin.__class__.__dict__.values() if hasattr(method, attribute)]

    def load_module(self, module_path: str) -> List[Plugin]:
        try:
            if module_path in self._modules:
                module = Module(importlib.reload(self._modules[module_path].module))
            else:
                module = Module(importlib.import_module(module_path))
        except ImportError:
            return []
        self._modules[module_path] = module
        return module.plugins
