from lobot.plugins import Plugin, command


class Tell(Plugin):
    @command('^tell ([^ ]*) (.*)', 'i')
    async def tell(self, nick: str, target: str, message: str, match):
        self.say(match.group(1), match.group(2))
