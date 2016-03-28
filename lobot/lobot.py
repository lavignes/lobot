from asyncio import AbstractEventLoop
from collections import OrderedDict
from typing import Optional
import asyncio
import json
import re

from .irc.protocol import IRCProtocol, IRCProtocolFactory, IRCProtocolDelegate
from .plugins.plugin import Plugin, _Bridge
from .plugin_manager import PluginManager
from .irc.message import Prefix


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

    def __init__(self, loop: Optional[AbstractEventLoop], config_path: str):
        self._proto = None
        self._loop = loop
        self._config_path = config_path
        self._plugin_manager = PluginManager()
        self._reload_config()
        self._connect()

    def _reload_config(self):
        with open(self._config_path) as config:
            self._config = json.load(config, object_pairs_hook=OrderedDict)
        self._nick = self._config['lobot']['nick']
        self._nick_pattern = re.compile('^@?' + self._nick + ':?', flags=re.IGNORECASE)

    def _reload_plugins(self):
        for module in self._config['lobot']['plugins']:
            for plugin in self._plugin_manager.load_module(module):
                plugin._attach(module, self)
                asyncio.ensure_future(plugin.on_load())

    def _connect(self):
        factory = IRCProtocolFactory(self)
        future = self._loop.create_connection(factory, host='localhost', port=6666)
        asyncio.ensure_future(future)

    def _process_listeners(self, plugin: Plugin, prefix: Prefix, target: str, message: str):
        # Process plugins using the @listen decorator
        for listener in self._plugin_manager.find_attributes(plugin, '_listener_patterns'):
            for pattern in getattr(listener, '_listener_patterns'):
                match = pattern.match(message)
                if match:
                    asyncio.ensure_future(listener(plugin, prefix.nick, target, message, match))
                    break

    def _process_commanders(self, plugin: Plugin, prefix: Prefix, target: str, message: str):
        # Check for private messages or messages that start with our nick
        message, count = self._nick_pattern.subn('', message)
        if count == 0 and self._nick != target:
            return
        message = message.lstrip()
        # Process plugins using the @command decorator
        for commander in self._plugin_manager.find_attributes(plugin, '_commander_patterns'):
            for pattern in getattr(commander, '_commander_patterns'):
                match = pattern.match(message)
                if match:
                    asyncio.ensure_future(commander(plugin, prefix.nick, target, message, match))
                    break

    async def proto_connected(self, proto: IRCProtocol):
        self._proto = proto
        proto.cmd_nick(self._nick)
        proto.cmd_user(self._config['lobot']['username'], 'localhost', 'localhost', self._nick)
        proto.cmd_join(self._config['lobot']['channels'])
        self._reload_plugins()
        for plugin in self._plugin_manager.plugins:
            asyncio.ensure_future(plugin.on_connected())

    async def proto_disconnected(self):
        for plugin in self._plugin_manager.plugins:
            asyncio.ensure_future(plugin.on_disconnected())

    async def proto_kick(self, prefix: Prefix, channel: str, nick: str, message: Optional[str]=None):
        pass

    async def proto_join(self, prefix: Prefix, channel: str):
        for plugin in self._plugin_manager.plugins:
            if prefix.nick == self._nick:
                asyncio.ensure_future(plugin.on_join(channel))
            else:
                asyncio.ensure_future(plugin.on_they_join(prefix.nick, channel))

    async def proto_part(self, prefix: Prefix, channel: str, message: Optional[str]=None):
        pass

    async def proto_ping(self, server: str):
        self._proto.cmd_pong(server)

    async def proto_privmsg(self, prefix: Prefix, target: str, message: str):
        if prefix.nick == self._nick:
            return
        for plugin in self._plugin_manager.plugins:
            self._process_listeners(plugin, prefix, target, message)
            self._process_commanders(plugin, prefix, target, message)
            if target == self._nick:
                asyncio.ensure_future(plugin.on_private_msg(prefix.nick, message))
            else:
                asyncio.ensure_future(plugin.on_msg(prefix.nick, target, message))

    async def proto_topic(self, prefix: Prefix, channel: str, message: Optional[str]=None):
        pass
