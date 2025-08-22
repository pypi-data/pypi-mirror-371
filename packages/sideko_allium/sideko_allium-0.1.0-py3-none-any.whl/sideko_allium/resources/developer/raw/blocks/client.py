import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    QueryParams,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    encode_query_param,
    to_encodable,
    type_utils,
)
from sideko_allium.types import models


class BlocksClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
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
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/{chain}/raw/blocks

        Args:
            page: Page number
            size: Page size
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.raw.blocks.list(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(page, type_utils.NotGiven):
            encode_query_param(
                _query,
                "page",
                to_encodable(item=page, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(size, type_utils.NotGiven):
            encode_query_param(
                _query,
                "size",
                to_encodable(item=size, dump_with=int),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        block_number: str,
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/{chain}/raw/blocks/{block_number}

        Args:
            block_number: str
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.raw.blocks.get(block_number="string", chain="abstract")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/blocks/{block_number}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock,
            request_options=request_options or default_request_options(),
        )


class AsyncBlocksClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
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
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/{chain}/raw/blocks

        Args:
            page: Page number
            size: Page size
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.raw.blocks.list(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(page, type_utils.NotGiven):
            encode_query_param(
                _query,
                "page",
                to_encodable(item=page, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(size, type_utils.NotGiven):
            encode_query_param(
                _query,
                "size",
                to_encodable(item=size, dump_with=int),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        block_number: str,
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/{chain}/raw/blocks/{block_number}

        Args:
            block_number: str
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.raw.blocks.get(block_number="string", chain="abstract")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/blocks/{block_number}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock,
            request_options=request_options or default_request_options(),
        )
