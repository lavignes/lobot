from asyncio import AbstractEventLoop
from collections import OrderedDict
from typing import Optional, Union
from types import CoroutineType
from asyncio import Future
import asyncio
import json
import sys
import re
import os

from .irc.protocol import IRCProtocol, IRCProtocolFactory, IRCProtocolDelegate
from .plugins.plugin import Plugin, _Bridge
from .plugin_manager import PluginManager
from .irc.message import Prefix


__all__ = [
    'Lobot'
]


class Lobot(IRCProtocolDelegate, _Bridge):
    @property
    def proto(self) -> IRCProtocol:
        return self._proto

    @property
    def config(self) -> dict:
        return self._config

    @property
    def nick(self) -> str:
        return self._nick

    @property
    def loop(self) -> str:
        return self._loop

    def __init__(self, loop: Optional[AbstractEventLoop], working_dir: str):
        self._proto = None
        self._loop = loop
        self._working_dir = working_dir
        self._plugin_manager = PluginManager()
        self._reload_config()
        self._connect()

    def _ensure_future(self, coro_or_future: Union[CoroutineType, Future]):
        asyncio.ensure_future(coro_or_future, loop=self._loop)

    def _reload_config(self):
        with open(os.path.join(self._working_dir, 'config.json')) as config:
            self._config = json.load(config, object_pairs_hook=OrderedDict)
        self._nick = self._config['lobot']['nick']
        self._nick_pattern = re.compile('^@?' + self._nick + ':?', flags=re.IGNORECASE)

    def _reload_plugins(self):
        plugs_path = os.path.join(self._working_dir, self._config['lobot']['plugdir'])
        sys.path.append(plugs_path)
        for module in self._config['lobot']['plugins']:
            for plugin in self._plugin_manager.load_module(module):
                plugin._attach(module, self)
                self._ensure_future(plugin.on_load())

    def _connect(self):
        factory = IRCProtocolFactory(self)
        future = self._loop.create_connection(factory,
                                              host=self._config['lobot']['host'],
                                              port=self._config['lobot']['port'],
                                              ssl=self._config['lobot']['ssl'])
        self._ensure_future(future)

    def _process_listeners(self, plugin: Plugin, prefix: Prefix, target: str, message: str):
        # Process plugins using the @listen decorator
        for listener in self._plugin_manager.find_attributes(plugin, '_listener_patterns'):
            for pattern in getattr(listener, '_listener_patterns'):
                match = pattern.search(message)
                if match:
                    self._ensure_future(listener(plugin, prefix.nick, target, message, match))
                    break

    def _process_commanders(self, plugin: Plugin, prefix: Prefix, target: str, message: str):
        # Check for private messages or messages that start with our nick
        message, count = self._nick_pattern.subn('', message)
        if count == 0 and self._nick != target:
            return
        message = message.lstrip()
        # Send on_command message
        self._ensure_future(plugin.on_command(prefix.nick, target, message))
        # Process plugins using the @command decorator
        for commander in self._plugin_manager.find_attributes(plugin, '_commander_patterns'):
            for pattern in getattr(commander, '_commander_patterns'):
                match = pattern.search(message)
                if match:
                    self._ensure_future(commander(plugin, prefix.nick, target, message, match))
                    break

    def proto_ensure_future(self, proto: IRCProtocol, coro_or_future: Union[CoroutineType, Future]):
        self._ensure_future(coro_or_future)

    async def proto_connected(self, proto: IRCProtocol):
        self._proto = proto
        proto.cmd_nick(self._nick)
        proto.cmd_user(self._config['lobot']['username'], 'localhost', 'localhost', self._nick)
        proto.cmd_join(self._config['lobot']['channels'])
        self._reload_plugins()
        for plugin in self._plugin_manager.plugins:
            self._ensure_future(plugin.on_connected())

    async def proto_disconnected(self, proto: IRCProtocol):
        self._proto = None
        for plugin in self._plugin_manager.plugins:
            self._ensure_future(plugin.on_disconnected())

    async def proto_kick(self, proto: IRCProtocol, prefix: Prefix, channel: str, nick: str, message: Optional[str]=None):
        pass

    async def proto_join(self, proto: IRCProtocol, prefix: Prefix, channel: str):
        for plugin in self._plugin_manager.plugins:
            if prefix.nick == self._nick:
                self._ensure_future(plugin.on_join(channel))
            else:
                self._ensure_future(plugin.on_they_join(prefix.nick, channel))

    async def proto_part(self, proto: IRCProtocol, prefix: Prefix, channel: str, message: Optional[str]=None):
        pass

    async def proto_ping(self, proto: IRCProtocol, server: str):
        proto.cmd_pong(server)

    async def proto_privmsg(self, proto: IRCProtocol, prefix: Prefix, target: str, message: str):
        if prefix.nick == self._nick:
            return
        for plugin in self._plugin_manager.plugins:
            self._process_listeners(plugin, prefix, target, message)
            self._process_commanders(plugin, prefix, target, message)
            if target == self._nick:
                self._ensure_future(plugin.on_private_msg(prefix.nick, message))
            else:
                self._ensure_future(plugin.on_msg(prefix.nick, target, message))

    async def proto_topic(self, proto: IRCProtocol, prefix: Prefix, channel: str, message: Optional[str]=None):
        pass
