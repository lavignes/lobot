from abc import ABC, abstractmethod
from typing import Callable, Any
import asyncio
import re


from ..irc.protocol import IRCProtocol


__all__ = [
    'listen',
    'command',
    'Plugin'
]


_Listener = Callable[[Any, str, str, str, Any], asyncio.Future]
_FLAGSMAP = {'i': re.IGNORECASE, 's': re.DOTALL}


def _raw_wrap(pattern: str, attribute: str, flags: str='') -> Callable[[_Listener], _Listener]:
    def wrap(listener: _Listener) -> _Listener:
        if not hasattr(listener, attribute):
            setattr(listener, attribute, [])
        re_flags = 0
        for c in flags:
            re_flags |= _FLAGSMAP.get(c, 0)
        getattr(listener, attribute).append(re.compile(pattern, flags=re_flags))
        return listener
    return wrap


def listen(pattern: str, flags: str='') -> Callable[[_Listener], _Listener]:
    return _raw_wrap(pattern, '_listener_patterns', flags)


def command(pattern: str, flags: str='') -> Callable[[_Listener], _Listener]:
    return _raw_wrap(pattern, '_commander_patterns', flags)


class _Bridge(ABC):
    @property
    @abstractmethod
    def proto(self) -> IRCProtocol:
        raise NotImplementedError

    @property
    @abstractmethod
    def loop(self) -> asyncio.AbstractEventLoop:
        raise NotImplementedError

    @property
    @abstractmethod
    def config(self) -> dict:
        raise NotImplementedError

    @property
    @abstractmethod
    def nick(self) -> str:
        raise NotImplementedError


class Plugin(object):
    def _attach(self, module_path: str, bridge: _Bridge):
        self._module_path = module_path
        self._bridge = bridge

    @property
    def nick(self) -> str:
        return self._bridge.nick

    @property
    def config(self) -> dict:
        return self._bridge.config.get(self._module_path)

    def say(self, target: str, message: str):
        self._bridge.proto.cmd_privmsg(target, message)

    def reply(self, nick: str, me_or_chan: str, message: str):
        if me_or_chan == self._bridge.nick:
             self._bridge.proto.cmd_privmsg(nick, message)
        else:
             self._bridge.proto.cmd_privmsg(me_or_chan, message)

    async def on_load(self):
        pass

    async def on_connected(self):
        pass

    async def on_disconnected(self):
        pass

    async def on_command(self, nick: str, target: str, message: str):
        pass

    async def on_msg(self, nick: str, channel: str, message: str):
        pass

    async def on_private_msg(self, nick: str, message: str):
        pass

    async def on_join(self, channel: str):
        pass

    async def on_they_join(self, nick: str, channel: str):
        pass