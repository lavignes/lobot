from lobot.plugins import Plugin, command


class Echo(Plugin):
    async def on_load(self):
        self._state = self.config.get('state', False)

    async def on_msg(self, nick: str, channel: str, message: str):
        if self._state:
            self.say(channel, message)

    async def on_private_msg(self, nick: str, message: str):
        if self._state:
            self.say(nick, message)

    @command('^echo (on|off|status)', 'i')
    async def echo_control(self, nick: str, target: str, message: str, match):
        text = match.group(1).lower()
        if text == 'status':
            self.say(target, 'Echo status: ' + ['OFF', 'ON'][self._state])
            return
        self._state = (text == 'on')
