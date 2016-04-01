from asyncio import AbstractEventLoop, StreamReader, StreamWriter
from typing import Optional, Dict, Tuple
from email.utils import formatdate
from urllib.parse import urlsplit
from abc import ABC
import asyncio
import json

from lobot.plugins import Plugin


__all__ = [
    'HTTPResponse',
    'HTTPSession',
    'HTTPPlugin'
]


class HTTPResponse(object):
    @property
    def status(self) -> int:
        return self._status

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def json(self) -> dict:
        return json.loads(self._data.decode())

    def __init__(self, status: int, headers: Dict[str, str], data: bytes):
        self._status = status
        self._headers = headers
        self._data = data


class HTTPSession(ABC):
    async def __aenter__(self) -> 'HTTPSession':
        raise NotImplementedError

    async def __aexit__(self, *args):
        raise NotImplementedError

    async def get(self, resource: str, data: Optional[bytes]=None,
                  headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        raise NotImplementedError

    async def post(self, resource: str, data: Optional[bytes]=None,
                   headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        raise NotImplementedError

    async def put(self, resource: str, data: Optional[bytes]=None,
                  headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        raise NotImplementedError

    async def delete(self, resource: str, data: Optional[bytes]=None,
                     headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        raise NotImplementedError


class _HTTPClient(HTTPSession):
    def __init__(self, loop: AbstractEventLoop, hostname: str, port: Optional[int]=80, ssl: Optional[bool]=False):
        self._loop = loop
        self._hostname = hostname
        self._port = port
        self._ssl = ssl

    async def __aenter__(self) -> HTTPSession:
        self._reader, self._writer = await self._connect()
        return self

    async def __aexit__(self, *args):
        self._writer.close()

    async def _connect(self) -> Tuple[StreamReader, StreamWriter]:
        return await asyncio.open_connection(host=self._hostname, port=self._port, loop=self._loop)

    async def _send(self, request: str, data: Optional[bytes]=None,
                    headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        host = 'Host: ' + self._hostname + ':' + str(self._port)
        message = [
            request,
            host
        ]
        send_headers = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            # 'Accept-Encoding: gzip',
            'Date': formatdate(timeval=None, localtime=False, usegmt=True)
        }
        if headers is not None:
            send_headers.update(headers)
        if data:
            headers['Content-Length'] = str(len(data))
        for key, value in send_headers.items():
            message.append(key + ': ' + value)
        full_request = '\r\n'.join(message) + '\r\n\r\n'
        self._writer.write(full_request.encode('latin-1'))
        if data:
            self._writer.write(data)
        # Parse Status Code
        status = int((await self._reader.readline()).decode('latin-1').split(' ')[1])
        response_headers = dict()
        # Parse Headers
        while True:
            line = await self._reader.readline()
            if line is None or line == b'\r\n':
                break
            header_name, header_value = line.decode('latin-1').rstrip().split(' ', 1)
            # Remove : from header name
            response_headers[header_name[:-1]] = header_value
        response_length = int(response_headers['Content-Length'])
        response_data = await self._reader.read(response_length)
        return HTTPResponse(status, response_headers, response_data)

    async def _method(self, method: str, resource: str, data: Optional[bytes]=None,
                      headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        return await self._send(method + ' ' + resource + ' HTTP/1.1', data, headers)

    async def get(self, resource: str, data: Optional[bytes]=None,
                  headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        return await self._method('GET', resource, data, headers)

    async def post(self, resource: str, data: Optional[bytes]=None,
                   headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        return await self._method('POST', resource, data, headers)

    async def put(self, resource: str, data: Optional[bytes]=None,
                  headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        return await self._method('PUT', resource, data, headers)

    async def delete(self, resource: str, data: Optional[bytes]=None,
                     headers: Optional[Dict[str, str]]=None) -> HTTPResponse:
        return await self._method('DELETE', resource, data, headers)


class HTTPPlugin(Plugin):
    def _decompose(self, url: str) -> Tuple[str, str, int, bool]:
        url_components = urlsplit(url)
        resource = url_components.path or '/'
        if url_components.query:
            resource += '?' + url_components.query
        if url_components.scheme == 'https':
            port = url_components.port or 443
            ssl = True
        else:
            port = url_components.port or 80
            ssl = False
        return url_components.hostname, resource, port, ssl

    def http_session(self, hostname: str, port: Optional[int]=80, ssl: Optional[bool]=False) -> HTTPSession:
        return _HTTPClient(self._bridge.loop, hostname, port, ssl)

    async def http_get(self, url: str, data: Optional[bytes]=None) -> HTTPResponse:
        hostname, resource, port, ssl = self._decompose(url)
        async with self.http_session(hostname, port, ssl) as session:
            return await session.get(resource, data)

    async def http_post(self, url: str, data: Optional[bytes]=None) -> HTTPResponse:
        hostname, resource, port, ssl = self._decompose(url)
        async with self.http_session(hostname, port, ssl) as session:
            return await session.post(resource, data)

    async def http_put(self, url: str, data: Optional[bytes]=None) -> HTTPResponse:
        hostname, resource, port, ssl = self._decompose(url)
        async with self.http_session(hostname, port, ssl) as session:
            return await session.put(resource, data)

    async def http_delete(self, url: str, data: Optional[bytes]=None) -> HTTPResponse:
        hostname, resource, port, ssl = self._decompose(url)
        async with self.http_session(hostname, port, ssl) as session:
            return await session.delete(resource, data)