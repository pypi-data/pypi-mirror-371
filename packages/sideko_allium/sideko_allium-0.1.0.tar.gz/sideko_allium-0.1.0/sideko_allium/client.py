import httpx
import typing

from sideko_allium.core import AsyncBaseClient, AuthBearer, AuthKey, SyncBaseClient
from sideko_allium.environment import Environment, _get_base_url
from sideko_allium.resources.admin import AdminClient, AsyncAdminClient
from sideko_allium.resources.developer import AsyncDeveloperClient, DeveloperClient
from sideko_allium.resources.explorer import AsyncExplorerClient, ExplorerClient
from sideko_allium.resources.streams import AsyncStreamsClient, StreamsClient
from sideko_allium.resources.supported_chains import (
    AsyncSupportedChainsClient,
    SupportedChainsClient,
)


class Client:
    def __init__(
        self,
        *,
        timeout: typing.Optional[float] = 60,
        httpx_client: typing.Optional[httpx.Client] = None,
        base_url: typing.Optional[str] = None,
        environment: Environment = Environment.PRODUCTION,
        key: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
    ):
        """Initialize root client"""
        self._base_client = SyncBaseClient(
            base_url=_get_base_url(base_url=base_url, environment=environment),
            httpx_client=httpx.Client(timeout=timeout)
            if httpx_client is None
            else httpx_client,
            auths={
                "APIKeyBearer": AuthKey(name="X-API-KEY", location="header", val=key),
                "FirebaseAuthBearer": AuthBearer(token=token),
            },
        )
        self.streams = StreamsClient(base_client=self._base_client)
        self.developer = DeveloperClient(base_client=self._base_client)
        self.explorer = ExplorerClient(base_client=self._base_client)
        self.supported_chains = SupportedChainsClient(base_client=self._base_client)
        self.admin = AdminClient(base_client=self._base_client)


class AsyncClient:
    def __init__(
        self,
        *,
        timeout: typing.Optional[float] = 60,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
        base_url: typing.Optional[str] = None,
        environment: Environment = Environment.PRODUCTION,
        key: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
    ):
        """Initialize root client"""
        self._base_client = AsyncBaseClient(
            base_url=_get_base_url(base_url=base_url, environment=environment),
            httpx_client=httpx.AsyncClient(timeout=timeout)
            if httpx_client is None
            else httpx_client,
            auths={
                "APIKeyBearer": AuthKey(name="X-API-KEY", location="header", val=key),
                "FirebaseAuthBearer": AuthBearer(token=token),
            },
        )
        self.streams = AsyncStreamsClient(base_client=self._base_client)
        self.developer = AsyncDeveloperClient(base_client=self._base_client)
        self.explorer = AsyncExplorerClient(base_client=self._base_client)
        self.supported_chains = AsyncSupportedChainsClient(
            base_client=self._base_client
        )
        self.admin = AsyncAdminClient(base_client=self._base_client)
