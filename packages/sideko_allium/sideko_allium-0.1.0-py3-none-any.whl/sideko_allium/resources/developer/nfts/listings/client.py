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


class ListingsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list_by_contact_address(
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
            "optimism",
            "polygon",
            "shape",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftListing_:
        """
        NFT Listings by Contract Address

        Get a list of NFT listings by contract address.

        GET /api/v1/developer/nfts/listings/{chain}/{contract_address}

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: Address of the NFT Contract.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.listings.list_by_contact_address(
            chain="abstract", contract_address="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/listings/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftListing_,
            request_options=request_options or default_request_options(),
        )

    def list_by_token_id(
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
            "optimism",
            "polygon",
            "shape",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        token_id: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftListing_:
        """
        NFT Listings by Token ID

        Get a list of NFT listings by token ID.

        GET /api/v1/developer/nfts/listings/{chain}/{contract_address}/{token_id}

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: Address of the NFT Contract.
            token_id: Token ID of the NFT.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.listings.list_by_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/listings/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeSingleItemNftListing_,
            request_options=request_options or default_request_options(),
        )


class AsyncListingsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list_by_contact_address(
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
            "optimism",
            "polygon",
            "shape",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftListing_:
        """
        NFT Listings by Contract Address

        Get a list of NFT listings by contract address.

        GET /api/v1/developer/nfts/listings/{chain}/{contract_address}

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: Address of the NFT Contract.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.listings.list_by_contact_address(
            chain="abstract", contract_address="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/listings/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftListing_,
            request_options=request_options or default_request_options(),
        )

    async def list_by_token_id(
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
            "optimism",
            "polygon",
            "shape",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        token_id: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftListing_:
        """
        NFT Listings by Token ID

        Get a list of NFT listings by token ID.

        GET /api/v1/developer/nfts/listings/{chain}/{contract_address}/{token_id}

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: Address of the NFT Contract.
            token_id: Token ID of the NFT.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.listings.list_by_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/listings/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeSingleItemNftListing_,
            request_options=request_options or default_request_options(),
        )
