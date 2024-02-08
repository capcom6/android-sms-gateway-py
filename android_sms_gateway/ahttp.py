import abc
import typing as t


class AsyncHttpClient(t.Protocol):
    @abc.abstractmethod
    async def get(
        self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    async def post(
        self, url: str, payload: dict, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


DEFAULT_CLIENT: t.Optional[t.Type[AsyncHttpClient]] = None


try:
    import aiohttp

    class AiohttpAsyncHttpClient(AsyncHttpClient):
        def __init__(self, session: t.Optional[aiohttp.ClientSession] = None) -> None:
            self._session = session

        async def __aenter__(self):
            if self._session is not None:
                raise ValueError("Session already initialized")

            self._session = await aiohttp.ClientSession().__aenter__()

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self._session.close()
            self._session = None

        async def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            response = await self._session.get(url, headers=headers)
            response.raise_for_status()

            return await response.json()

        async def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            response = await self._session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            return await response.json()

    DEFAULT_CLIENT = AiohttpAsyncHttpClient
except ImportError:
    pass

try:
    import httpx

    class HttpxAsyncHttpClient(AsyncHttpClient):
        def __init__(self, client: t.Optional[httpx.AsyncClient] = None) -> None:
            self._client = client

        async def __aenter__(self):
            if self._client is not None:
                raise ValueError("Client already initialized")

            self._client = await httpx.AsyncClient().__aenter__()

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self._client.aclose()
            self._client = None

        async def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            response = await self._client.get(url, headers=headers)

            return response.raise_for_status().json()

        async def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            response = await self._client.post(url, headers=headers, json=payload)

            return response.raise_for_status().json()

    DEFAULT_CLIENT = HttpxAsyncHttpClient
except ImportError:
    pass


def get_client() -> AsyncHttpClient:
    if DEFAULT_CLIENT is None:
        raise ImportError("Please install aiohttp or httpx")

    return DEFAULT_CLIENT()
