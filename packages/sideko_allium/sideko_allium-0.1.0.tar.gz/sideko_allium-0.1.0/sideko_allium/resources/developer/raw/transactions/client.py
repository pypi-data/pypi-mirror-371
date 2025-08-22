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


class TransactionsClient:
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
        block_number: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        from_address: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        include_label: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        order_by: typing.Union[
            typing.Optional[typing_extensions.Literal["asc", "desc"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        order_by_col: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        to_address: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AlliumPageEnrichedTransaction_:
        """
        Get Transactions

        GET /api/v1/developer/{chain}/raw/transactions

        Args:
            block_number: typing.Optional[int]
            from_address: typing.Optional[str]
            include_label: bool
            order_by: typing_extensions.Literal["asc", "desc"]
            order_by_col: str
            page: Page number
            size: Page size
            to_address: typing.Optional[str]
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.raw.transactions.list(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(block_number, type_utils.NotGiven):
            encode_query_param(
                _query,
                "block_number",
                to_encodable(item=block_number, dump_with=typing.Optional[int]),
                style="form",
                explode=True,
            )
        if not isinstance(from_address, type_utils.NotGiven):
            encode_query_param(
                _query,
                "from_address",
                to_encodable(item=from_address, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(include_label, type_utils.NotGiven):
            encode_query_param(
                _query,
                "include_label",
                to_encodable(item=include_label, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(order_by, type_utils.NotGiven):
            encode_query_param(
                _query,
                "order_by",
                to_encodable(
                    item=order_by, dump_with=typing_extensions.Literal["asc", "desc"]
                ),
                style="form",
                explode=True,
            )
        if not isinstance(order_by_col, type_utils.NotGiven):
            encode_query_param(
                _query,
                "order_by_col",
                to_encodable(item=order_by_col, dump_with=str),
                style="form",
                explode=True,
            )
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
        if not isinstance(to_address, type_utils.NotGiven):
            encode_query_param(
                _query,
                "to_address",
                to_encodable(item=to_address, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.AlliumPageEnrichedTransaction_,
            request_options=request_options or default_request_options(),
        )

    def get(
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
        transaction_hash: str,
        include_label: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnrichedTransaction:
        """
        Get Transaction

        GET /api/v1/developer/{chain}/raw/transactions/{transaction_hash}

        Args:
            include_label: bool
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            transaction_hash: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.raw.transactions.get(
            chain="abstract", transaction_hash="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(include_label, type_utils.NotGiven):
            encode_query_param(
                _query,
                "include_label",
                to_encodable(item=include_label, dump_with=bool),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/transactions/{transaction_hash}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.EnrichedTransaction,
            request_options=request_options or default_request_options(),
        )


class AsyncTransactionsClient:
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
        block_number: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        from_address: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        include_label: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        order_by: typing.Union[
            typing.Optional[typing_extensions.Literal["asc", "desc"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        order_by_col: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        to_address: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AlliumPageEnrichedTransaction_:
        """
        Get Transactions

        GET /api/v1/developer/{chain}/raw/transactions

        Args:
            block_number: typing.Optional[int]
            from_address: typing.Optional[str]
            include_label: bool
            order_by: typing_extensions.Literal["asc", "desc"]
            order_by_col: str
            page: Page number
            size: Page size
            to_address: typing.Optional[str]
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.raw.transactions.list(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(block_number, type_utils.NotGiven):
            encode_query_param(
                _query,
                "block_number",
                to_encodable(item=block_number, dump_with=typing.Optional[int]),
                style="form",
                explode=True,
            )
        if not isinstance(from_address, type_utils.NotGiven):
            encode_query_param(
                _query,
                "from_address",
                to_encodable(item=from_address, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(include_label, type_utils.NotGiven):
            encode_query_param(
                _query,
                "include_label",
                to_encodable(item=include_label, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(order_by, type_utils.NotGiven):
            encode_query_param(
                _query,
                "order_by",
                to_encodable(
                    item=order_by, dump_with=typing_extensions.Literal["asc", "desc"]
                ),
                style="form",
                explode=True,
            )
        if not isinstance(order_by_col, type_utils.NotGiven):
            encode_query_param(
                _query,
                "order_by_col",
                to_encodable(item=order_by_col, dump_with=str),
                style="form",
                explode=True,
            )
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
        if not isinstance(to_address, type_utils.NotGiven):
            encode_query_param(
                _query,
                "to_address",
                to_encodable(item=to_address, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.AlliumPageEnrichedTransaction_,
            request_options=request_options or default_request_options(),
        )

    async def get(
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
        transaction_hash: str,
        include_label: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnrichedTransaction:
        """
        Get Transaction

        GET /api/v1/developer/{chain}/raw/transactions/{transaction_hash}

        Args:
            include_label: bool
            chain: typing_extensions.Literal["abstract", "aleph_zero", "alienx", "apechain", "aptos", "arbitrum", "arbitrum_nova", "arbitrum_sepolia", "astar", "avalanche", "b3", "babylon", "base", "base_sepolia", "beacon", "beacon_validators", "berachain", "binance", "bitcoin", "bitcoin_cash", "blast", "botanix", "bsc", "cardano", "celestia", "celo", "codex", "core", "cosmos", "cosmoshub", "dogecoin", "dydx", "dymension", "educhain", "ethereum", "ethereum_goerli", "ethereum_hoodi", "ethereum_sepolia", "everclear", "fantom", "fraxtal", "gnosis", "gravity", "harmony", "hedera", "holesky", "hyperevm", "hyperliquid", "imx_zkevm", "injective", "ink", "katana", "kava", "kinto", "linea", "litecoin", "logx", "manta_pacific", "mantle", "mantra", "metis", "mode", "monad_devnet1", "monad_testnet", "near", "oasys", "optimism", "osmosis", "plume", "polygon", "polygon_zkevm", "proof_of_play_apex", "proof_of_play_boss", "provenance", "real", "reya", "ronin", "rootstock", "sanko", "scroll", "scroll_sepolia", "sei", "solana", "soneium", "sonic", "stable_testnet", "stacks", "starknet", "stellar", "sui", "superposition", "sx", "ton", "tron", "unichain", "vana", "winr", "worldchain", "x_layer", "xrp_ledger", "zksync", "zora"]
            transaction_hash: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.raw.transactions.get(
            chain="abstract", transaction_hash="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(include_label, type_utils.NotGiven):
            encode_query_param(
                _query,
                "include_label",
                to_encodable(item=include_label, dump_with=bool),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/{chain}/raw/transactions/{transaction_hash}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.EnrichedTransaction,
            request_options=request_options or default_request_options(),
        )
