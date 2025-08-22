import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import params


class SqlClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def query(
        self,
        *,
        chain: typing_extensions.Literal[
            "abstract",
            "aleph_zero",
            "alienx",
            "apechain",
            "aptos",
            "arbitrum",
            "arbitrum_nova",
            "arbitrum_sepolia",
            "astar",
            "avalanche",
            "b3",
            "babylon",
            "base",
            "base_sepolia",
            "beacon",
            "beacon_validators",
            "berachain",
            "binance",
            "bitcoin",
            "bitcoin_cash",
            "blast",
            "botanix",
            "bsc",
            "cardano",
            "celestia",
            "celo",
            "codex",
            "core",
            "cosmos",
            "cosmoshub",
            "dogecoin",
            "dydx",
            "dymension",
            "educhain",
            "ethereum",
            "ethereum_goerli",
            "ethereum_hoodi",
            "ethereum_sepolia",
            "everclear",
            "fantom",
            "fraxtal",
            "gnosis",
            "gravity",
            "harmony",
            "hedera",
            "holesky",
            "hyperevm",
            "hyperliquid",
            "imx_zkevm",
            "injective",
            "ink",
            "katana",
            "kava",
            "kinto",
            "linea",
            "litecoin",
            "logx",
            "manta_pacific",
            "mantle",
            "mantra",
            "metis",
            "mode",
            "monad_devnet1",
            "monad_testnet",
            "near",
            "oasys",
            "optimism",
            "osmosis",
            "plume",
            "polygon",
            "polygon_zkevm",
            "proof_of_play_apex",
            "proof_of_play_boss",
            "provenance",
            "real",
            "reya",
            "ronin",
            "rootstock",
            "sanko",
            "scroll",
            "scroll_sepolia",
            "sei",
            "solana",
            "soneium",
            "sonic",
            "stable_testnet",
            "stacks",
            "starknet",
            "stellar",
            "sui",
            "superposition",
            "sx",
            "ton",
            "tron",
            "unichain",
            "vana",
            "winr",
            "worldchain",
            "x_layer",
            "xrp_ledger",
            "zksync",
            "zora",
        ],
        query: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Raw Sql Query

        POST /api/v1/developer/{chain}/sql/

        Args:
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            query: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.sql.query(chain="abstract", query="string")
        ```
        """
        _json = to_encodable(
            item={"query": query}, dump_with=params._SerializerRawQueryPayload
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/developer/{chain}/sql/",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncSqlClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def query(
        self,
        *,
        chain: typing_extensions.Literal[
            "abstract",
            "aleph_zero",
            "alienx",
            "apechain",
            "aptos",
            "arbitrum",
            "arbitrum_nova",
            "arbitrum_sepolia",
            "astar",
            "avalanche",
            "b3",
            "babylon",
            "base",
            "base_sepolia",
            "beacon",
            "beacon_validators",
            "berachain",
            "binance",
            "bitcoin",
            "bitcoin_cash",
            "blast",
            "botanix",
            "bsc",
            "cardano",
            "celestia",
            "celo",
            "codex",
            "core",
            "cosmos",
            "cosmoshub",
            "dogecoin",
            "dydx",
            "dymension",
            "educhain",
            "ethereum",
            "ethereum_goerli",
            "ethereum_hoodi",
            "ethereum_sepolia",
            "everclear",
            "fantom",
            "fraxtal",
            "gnosis",
            "gravity",
            "harmony",
            "hedera",
            "holesky",
            "hyperevm",
            "hyperliquid",
            "imx_zkevm",
            "injective",
            "ink",
            "katana",
            "kava",
            "kinto",
            "linea",
            "litecoin",
            "logx",
            "manta_pacific",
            "mantle",
            "mantra",
            "metis",
            "mode",
            "monad_devnet1",
            "monad_testnet",
            "near",
            "oasys",
            "optimism",
            "osmosis",
            "plume",
            "polygon",
            "polygon_zkevm",
            "proof_of_play_apex",
            "proof_of_play_boss",
            "provenance",
            "real",
            "reya",
            "ronin",
            "rootstock",
            "sanko",
            "scroll",
            "scroll_sepolia",
            "sei",
            "solana",
            "soneium",
            "sonic",
            "stable_testnet",
            "stacks",
            "starknet",
            "stellar",
            "sui",
            "superposition",
            "sx",
            "ton",
            "tron",
            "unichain",
            "vana",
            "winr",
            "worldchain",
            "x_layer",
            "xrp_ledger",
            "zksync",
            "zora",
        ],
        query: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Raw Sql Query

        POST /api/v1/developer/{chain}/sql/

        Args:
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            query: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.sql.query(chain="abstract", query="string")
        ```
        """
        _json = to_encodable(
            item={"query": query}, dump_with=params._SerializerRawQueryPayload
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/developer/{chain}/sql/",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
