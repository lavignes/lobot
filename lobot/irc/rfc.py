from enum import Enum, IntEnum, unique


__all__ = [
    'Command',
    'ReplyCode',
    'ErrorCode'
]


@unique
class Command(Enum):
    JOIN = 'JOIN'
    KICK = 'KICK'
    NICK = 'NICK'
    NOTICE = 'NOTICE'
    PART = 'PART'
    PASS = 'PASS'
    PING = 'PING'
    PONG = 'PONG'
    PRIVMSG = 'PRIVMSG'
    TOPIC = 'TOPIC'
    USER = 'USER'


@unique
class ReplyCode(IntEnum):
    pass


@unique
class ErrorCode(IntEnum):
    pass