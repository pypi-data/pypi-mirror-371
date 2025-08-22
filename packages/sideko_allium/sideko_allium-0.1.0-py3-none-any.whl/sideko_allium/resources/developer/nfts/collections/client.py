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


class CollectionsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        chain: typing_extensions.Literal[
            "abstract",
            "apechain",
            "arbitrum",
            "arbitrum-nova",
            "avalanche",
            "base",
            "ethereum",
            "linea",
            "optimism",
            "polygon",
            "shape",
            "solana",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        collection_symbols: typing.Union[
            typing.Optional[typing.List[str]], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        contract_addresses: typing.Union[
            typing.Optional[typing.List[str]], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftFullCollectionBase_:
        """
        NFT Collections

        Fetch multiple collections that match the given contract addresses.

        GET /api/v1/developer/nfts/collections/{chain}

        Args:
            collection_symbols: Collection Symbols of the Solana NFT Collections to fetch. This is only used for Solana.
            contract_addresses: Addresses of the NFT Contracts to fetch Collections for. This is used for EVM chains.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "linea", "optimism", "polygon", "shape", "solana", "soneium", "xai", "zero", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.collections.get(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(collection_symbols, type_utils.NotGiven):
            encode_query_param(
                _query,
                "collection_symbols",
                to_encodable(item=collection_symbols, dump_with=typing.List[str]),
                style="form",
                explode=True,
            )
        if not isinstance(contract_addresses, type_utils.NotGiven):
            encode_query_param(
                _query,
                "contract_addresses",
                to_encodable(item=contract_addresses, dump_with=typing.List[str]),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/collections/{chain}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftFullCollectionBase_,
            request_options=request_options or default_request_options(),
        )


class AsyncCollectionsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        chain: typing_extensions.Literal[
            "abstract",
            "apechain",
            "arbitrum",
            "arbitrum-nova",
            "avalanche",
            "base",
            "ethereum",
            "linea",
            "optimism",
            "polygon",
            "shape",
            "solana",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        collection_symbols: typing.Union[
            typing.Optional[typing.List[str]], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        contract_addresses: typing.Union[
            typing.Optional[typing.List[str]], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftFullCollectionBase_:
        """
        NFT Collections

        Fetch multiple collections that match the given contract addresses.

        GET /api/v1/developer/nfts/collections/{chain}

        Args:
            collection_symbols: Collection Symbols of the Solana NFT Collections to fetch. This is only used for Solana.
            contract_addresses: Addresses of the NFT Contracts to fetch Collections for. This is used for EVM chains.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "linea", "optimism", "polygon", "shape", "solana", "soneium", "xai", "zero", "zora"]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.collections.get(chain="abstract")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(collection_symbols, type_utils.NotGiven):
            encode_query_param(
                _query,
                "collection_symbols",
                to_encodable(item=collection_symbols, dump_with=typing.List[str]),
                style="form",
                explode=True,
            )
        if not isinstance(contract_addresses, type_utils.NotGiven):
            encode_query_param(
                _query,
                "contract_addresses",
                to_encodable(item=contract_addresses, dump_with=typing.List[str]),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/collections/{chain}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftFullCollectionBase_,
            request_options=request_options or default_request_options(),
        )
