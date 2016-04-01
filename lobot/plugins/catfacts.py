from lobot.plugins import HTTPPlugin, command


class CatFacts(HTTPPlugin):
    @command('cat ?facts?', 'i')
    async def cat_facts(self, nick: str, target: str, message: str, match):
        r = await self.http_get('http://catfacts-api.appspot.com/api/facts')
        json = r.json
        if r.status != 200 or json['success'] == False:
            self.reply(nick, target, 'I could not load any cat facts. Try again later.')
            return
        self.reply(nick, target, json['facts'][0])
