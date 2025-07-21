from collections import defaultdict

from authlib.deprecate import deprecate

from .errors import InsecureTransportError


class AsyncOAuth2Payload:
    @property
    async def data(self):
        raise NotImplementedError()

    @property
    async def datalist(self) -> defaultdict[str, list]:
        raise NotImplementedError()

    @property
    async def client_id(self) -> str:
        """The authorization server issues the registered client a client
        identifier -- a unique string representing the registration
        information provided by the client. The value is extracted from
        request.

        :return: string
        """
        data = await self.data
        return data.get("client_id")

    @property
    async def response_type(self) -> str:
        data = await self.data
        rt = data.get("response_type")
        if rt and " " in rt:
            # sort multiple response types
            return " ".join(sorted(rt.split()))
        return rt

    @property
    async def grant_type(self) -> str:
        data = await self.data
        return data.get("grant_type")

    @property
    async def redirect_uri(self):
        data = await self.data
        return data.get("redirect_uri")

    @property
    async def scope(self) -> str:
        data = await self.data
        return data.get("scope")

    @property
    async def state(self):
        data = await self.data
        return data.get("state")


class AsyncBasicOAuth2Payload(AsyncOAuth2Payload):
    def __init__(self, payload):
        self._data = payload
        self._datalist = {key: [value] for key, value in payload.items()}

    @property
    def data(self):
        return self._data

    @property
    def datalist(self) -> defaultdict[str, list]:
        return self._datalist


class AsyncOAuth2Request(AsyncOAuth2Payload):
    def __init__(self, method: str, uri: str, headers=None):
        InsecureTransportError.check(uri)
        #: HTTP method
        self.method = method
        self.uri = uri
        #: HTTP headers
        self.headers = headers or {}

        self.payload = None

        self.client = None
        self.auth_method = None
        self.user = None
        self.authorization_code = None
        self.refresh_token = None
        self.credential = None

    @property
    def args(self):
        raise NotImplementedError()

    @property
    def form(self):
        raise NotImplementedError()

    @property
    def data(self):
        deprecate(
            "'request.data' is deprecated in favor of 'request.payload.data'",
            version="1.8",
        )
        return self.payload.data

    @property
    def datalist(self) -> defaultdict[str, list]:
        deprecate(
            "'request.datalist' is deprecated in favor of 'request.payload.datalist'",
            version="1.8",
        )
        return self.payload.datalist

    @property
    def client_id(self) -> str:
        deprecate(
            "'request.client_id' is deprecated in favor of 'request.payload.client_id'",
            version="1.8",
        )
        return self.payload.client_id

    @property
    def response_type(self) -> str:
        deprecate(
            "'request.response_type' is deprecated in favor of 'request.payload.response_type'",
            version="1.8",
        )
        return self.payload.response_type

    @property
    def grant_type(self) -> str:
        deprecate(
            "'request.grant_type' is deprecated in favor of 'request.payload.grant_type'",
            version="1.8",
        )
        return self.payload.grant_type

    @property
    def redirect_uri(self):
        deprecate(
            "'request.redirect_uri' is deprecated in favor of 'request.payload.redirect_uri'",
            version="1.8",
        )
        return self.payload.redirect_uri

    @property
    def scope(self) -> str:
        deprecate(
            "'request.scope' is deprecated in favor of 'request.payload.scope'",
            version="1.8",
        )
        return self.payload.scope

    @property
    def state(self):
        deprecate(
            "'request.state' is deprecated in favor of 'request.payload.state'",
            version="1.8",
        )
        return self.payload.state


class AsyncJsonPayload:
    @property
    def data(self):
        raise NotImplementedError()


class AsyncJsonRequest:
    def __init__(self, method, uri, headers=None):
        self.method = method
        self.uri = uri
        self.headers = headers or {}
        self.payload = None

    @property
    def data(self):
        deprecate(
            "'request.data' is deprecated in favor of 'request.payload.data'",
            version="1.8",
        )
        return self.payload.data
