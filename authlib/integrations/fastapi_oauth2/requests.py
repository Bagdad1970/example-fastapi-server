from collections import defaultdict
from functools import cached_property

from fastapi import Request
from authlib.oauth2.rfc6749 import AsyncJsonPayload, AsyncJsonRequest, AsyncOAuth2Payload, AsyncOAuth2Request


class FastAPIOAuth2Payload(AsyncOAuth2Payload):
    def __init__(self, request: Request):
        self._request = request

    @property
    async def data(self) -> dict:
        form_data = await self._request.form()
        query_params = self._request.query_params
        return {**form_data, **query_params}

    @cached_property
    async def datalist(self):
        form_data = await self._request.form()
        values = defaultdict(list)
        for k, v in form_data.multi_items():
            values[k].append(v)
        return values


class FastAPIOAuth2Request(AsyncOAuth2Request):
    def __init__(self, request: Request):
        super().__init__(request.method, str(request.url), request.headers)
        self._request = request
        self.payload = FastAPIOAuth2Payload(request)

    @property
    def args(self):
        return dict(self._request.query_params)

    @property
    async def form(self):
        form_data = await self._request.form()
        return form_data


class FastAPIJsonPayload(AsyncJsonPayload):
    def __init__(self, request: Request):
        self._request = request

    @property
    def data(self):
        return self._request.json()


class FastAPIJsonRequest(AsyncJsonRequest):
    def __init__(self, request: Request):
        super().__init__(request.method, str(request.url), request.headers)
        self.payload = FastAPIJsonPayload(request)