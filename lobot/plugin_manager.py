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

    def find_attributes(self, plugin: Plugin, attribute: str) -> List[_Listener]:
        return [method for method in plugin.__class__.__dict__.values() if hasattr(method, attribute)]

    def load_module(self, module_path: str) -> List[Plugin]:
        module = None
        if module_path in self._modules:
            module = self._modules[module_path].module
            importlib.reload(module)
        else:
            if len(module_path.split('.')) == 1:
                module_path = "lobot.plugins." + module_path
            module = importlib.import_module(module_path)
        wrapped = Module(module)
        self._modules[module_path] = wrapped
        return wrapped.plugins
