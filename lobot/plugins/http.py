from http.cookies import SimpleCookie
import aiohttp

from lobot.plugins import Plugin


class HTTPResponse(object):
    @property
    def status(self) -> int:
        return self._response.status

    @property
    def reason(self) -> str:
        return self._response.reason

    @property
    def cookies(self) -> SimpleCookie:
        return self._response.cookies

    @property
    def raw_headers(self) -> dict:
        return self._response.raw_headers

    @property
    async def text(self) -> str:
        return (await self._response.read()).decode()

    @property
    async def json(self) -> dict:
        return await self._response.json()

    def __init__(self, response: aiohttp.ClientResponse):
        self._response = response


class HTTPPlugin(Plugin):
    async def http_get(self, url: str) -> HTTPResponse:
        with aiohttp.ClientSession() as session:
            return HTTPResponse(await session.get(url))

    async def http_post(self, url: str, data: bytes) -> HTTPResponse:
        with aiohttp.ClientSession() as session:
            return HTTPResponse(await session.post(url, data=data))

    async def http_put(self, url: str, data: bytes) -> HTTPResponse:
        with aiohttp.ClientSession() as session:
            return HTTPResponse(await session.put(url, data=data))

    async def http_delete(self, url: str) -> HTTPResponse:
        with aiohttp.ClientSession() as session:
            return HTTPResponse(await session.delete(url))