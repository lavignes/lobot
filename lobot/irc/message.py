from typing import Optional, List


__all__ = [
    'MessageError',
    'Prefix',
    'Message'
]


class MessageError(Exception):
    pass


class Prefix(object):
    @property
    def nick(self) -> Optional[str]:
        return self._nick

    @property
    def username(self) -> Optional[str]:
        return self._user

    @property
    def host(self) -> Optional[str]:
        return self._host

    def __init__(self, data: bytes):
        nick, user, host = None, None, None
        if data.find(b'!') != -1:
            nick, data = data.split(b'!', 1)
            nick = nick.decode()
            if data.find(b'@') != -1:
                user, host = data.split(b'@')
            else:
                user = data
            user = user.decode()
        else:
            host = data
        self._nick = nick
        self._user = user
        self._host = host.decode()


class Message(object):
    @property
    def prefix(self) -> Optional[Prefix]:
        return self._prefix

    @property
    def command(self) -> str:
        return self._command

    @property
    def args(self) -> List[str]:
        return self._args

    def __init__(self, data: bytes):
        try:
            prefix = b''
            # Message has prefix
            if data[0] == b':'[0]:
                prefix, data = data[1:].split(b' ', 1)
            # Message has multi-word argument
            if data.find(b' :') != -1:
                data, long_arg = data.split(b' :', 1)
                args = data.split(b' ')
                args.append(long_arg)
            else:
                args = data.split(b' ')
            if len(prefix) > 0:
                self._prefix = Prefix(prefix)
            self._command = args.pop(0).decode()
            self._args = [arg.decode() for arg in args]
        except Exception:
            raise MessageError('Message could not be decoded: ' + data.decode())
