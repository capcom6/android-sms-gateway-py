import abc
import base64
import logging
import sys
import typing as t

from . import ahttp, domain, http
from .constants import DEFAULT_URL, VERSION

logger = logging.getLogger(__name__)


class BaseClient(abc.ABC):
    def __init__(
        self, login: str, password: str, *, base_url: str = DEFAULT_URL
    ) -> None:
        credentials = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode(
            "utf-8"
        )
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "User-Agent": f"android-sms-gateway/{VERSION} (client; python {sys.version_info.major}.{sys.version_info.minor})",
        }
        self.base_url = base_url.rstrip("/")


class APIClient(BaseClient):
    def __init__(
        self,
        login: str,
        password: str,
        *,
        base_url: str = DEFAULT_URL,
        http_client: t.Optional[http.HttpClient] = None,
    ) -> None:
        super().__init__(login, password, base_url=base_url)
        self.http = http_client

    def __enter__(self):
        if self.http is not None:
            raise ValueError("HTTP client already initialized")

        self.http = http.get_client().__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.http.__exit__(exc_type, exc_val, exc_tb)
        self.http = None

    def send(self, message: domain.Message) -> domain.MessageState:
        return domain.MessageState.from_dict(
            self.http.post(
                f"{self.base_url}/message",
                payload=message.asdict(),
                headers=self.headers,
            )
        )

    def get_state(self, _id: str) -> domain.MessageState:
        return domain.MessageState.from_dict(
            self.http.get(f"{self.base_url}/message/{_id}", headers=self.headers)
        )


class AsyncAPIClient(BaseClient):
    def __init__(
        self,
        login: str,
        password: str,
        *,
        base_url: str = DEFAULT_URL,
        http_client: t.Optional[ahttp.AsyncHttpClient] = None,
    ) -> None:
        super().__init__(login, password, base_url=base_url)
        self.http = http_client

    async def __aenter__(self):
        if self.http is not None:
            raise ValueError("HTTP client already initialized")

        self.http = await ahttp.get_client().__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http.__aexit__(exc_type, exc_val, exc_tb)
        self.http = None

    async def send(self, message: domain.Message) -> domain.MessageState:
        return domain.MessageState.from_dict(
            await self.http.post(
                f"{self.base_url}/message",
                payload=message.asdict(),
                headers=self.headers,
            )
        )

    async def get_state(self, _id: str) -> domain.MessageState:
        return domain.MessageState.from_dict(
            await self.http.get(f"{self.base_url}/message/{_id}", headers=self.headers)
        )
