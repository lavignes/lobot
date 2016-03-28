from typing import Union, Optional, List, Any
from asyncio import Protocol, Transport, Future
from types import CoroutineType
from abc import ABC
import asyncio

from .message import Message, Prefix, MessageError
from .rfc import Command, ReplyCode, ErrorCode


def _chunk_bytes(l: bytes, n: int) -> bytes:
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _get_default(l: List[Any], index: int, default: Any=None) -> Any:
    try:
        return l[index]
    except IndexError:
        return default


class IRCProtocolFactory(object):
    def __init__(self, delegate: 'IRCProtocolDelegate'):
        self._delegate = delegate

    def __call__(self) -> 'IRCProtocol':
        return IRCProtocol(self._delegate)


class IRCProtocol(Protocol):
    def __init__(self, delegate: 'IRCProtocolDelegate'):
        self._transport = None
        self._delegate = delegate

    def connection_made(self, transport: Transport):
        self._transport = transport
        self._schedule(self._delegate.proto_connected(self))

    def data_received(self, data: bytes) -> None:
        for datum in data.rstrip(b'\r\n').split(b'\r\n'):
            try:
                message = Message(datum)
                self._dispatch(message)
            except MessageError:
                raise

    def connection_lost(self, error: Optional[Exception]):
        self._schedule(self._delegate.proto_disconnected())

    @staticmethod
    def _schedule(task: Union[CoroutineType, Future]):
        asyncio.ensure_future(task)

    def _send(self, command: Command, *args: List[str], long_arg: Optional[str]=None):
        message = command.value + ' ' + ' '.join(arg for arg in args if arg)
        encoded_message = message.encode()
        if long_arg is None:
            self._transport.write(encoded_message + b'\r\n')
        else:
            # IRC limits messages to 512 bytes. So we need to chunk the message
            chunk_size = 508 - len(encoded_message)
            for chunk in _chunk_bytes(long_arg.encode(), chunk_size):
                self._transport.write(encoded_message + b' :' + chunk + b'\r\n')

    def _dispatch(self, message: Message):
        # Parse the command
        command, reply, error = None, None, None
        try:
            command = Command(message.command)
        except ValueError:
            try:
                reply = ReplyCode(message.command)
            except ValueError:
                try:
                    error = ErrorCode(message.command)
                except ValueError:
                    pass
                else:
                    pass
            else:
                pass
        else:
            if command == Command.KICK:
                self._schedule(self._delegate.proto_kick(message.prefix,
                                                         message.args[0],
                                                         message.args[1],
                                                         _get_default(message.args, 2)))
            elif command == Command.JOIN:
                self._schedule(self._delegate.proto_join(message.prefix,
                                                         message.args[0]))
            elif command == Command.PART:
                self._schedule(self._delegate.proto_part(message.prefix,
                                                         message.args[0],
                                                         _get_default(message.args, 1)))
            elif command == Command.PING:
                self._schedule(self._delegate.proto_ping(message.args[0]))
            elif command == Command.PRIVMSG:
                self._schedule(self._delegate.proto_privmsg(message.prefix,
                                                            message.args[0],
                                                            message.args[1]))
            elif command == Command.TOPIC:
                self._schedule(self._delegate.proto_topic(message.prefix,
                                                          message.args[0],
                                                          _get_default(message.args, 1)))

    def cmd_kick(self, channel: str, nick: str, message: Optional[str]=None):
        self._send(Command.KICK, channel, nick, long_arg=message)

    def cmd_join(self, channels: List[str], passwords: Optional[List[str]]=None):
        password_string = None
        if passwords is not None:
            password_string = ','.join(passwords)
        self._send(Command.JOIN, ','.join(channels), password_string)

    def cmd_nick(self, nick: str):
        self._send(Command.NICK, nick)

    def cmd_part(self, channels: List[str], message: Optional[str]=None):
        self._send(Command.PART, ','.join(channels), long_arg=message)

    def cmd_pass(self, password: str):
        self._send(Command.PASS, password)

    def cmd_ping(self, server: str):
        self._send(Command.PING, server)

    def cmd_pong(self, server: str):
        self._send(Command.PONG, server)

    def cmd_privmsg(self, target: str, message: str):
        self._send(Command.PRIVMSG, target, long_arg=message)

    def cmd_topic(self, channel: str, message: Optional[str]=None):
        self._send(Command.TOPIC, channel, long_arg=message)

    def cmd_user(self, username: str, hostname: str, servername: str, realname: str):
        self._send(Command.USER, username, hostname, servername, long_arg=realname)


class IRCProtocolDelegate(ABC):
    async def proto_connected(self, proto: IRCProtocol):
        raise NotImplementedError

    async def proto_disconnected(self):
        raise NotImplementedError

    async def proto_kick(self, prefix: Prefix, channel: str, nick: str, message: Optional[str]=None):
        raise NotImplementedError

    async def proto_join(self, prefix: Prefix, channel: str):
        raise NotImplementedError

    async def proto_part(self, prefix: Prefix, channel: str, message: Optional[str]=None):
        raise NotImplementedError

    async def proto_ping(self, server: str):
        raise NotImplementedError

    async def proto_privmsg(self, prefix: Prefix, target: str, message: str):
        raise NotImplementedError

    async def proto_topic(self, prefix: Prefix, channel: str, message: Optional[str]=None):
        raise NotImplementedError
