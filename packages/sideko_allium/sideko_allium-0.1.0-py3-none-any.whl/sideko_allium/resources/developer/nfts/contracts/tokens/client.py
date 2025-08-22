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


class TokensClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
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
    ) -> models.ResponseEnvelopeMultiItemsNftToken_:
        """
        NFT Tokens by Contract

        This API returns all NFT tokens that belong to a given contract.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/tokens

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "linea", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.contracts.tokens.list(
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
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}/tokens",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftToken_,
            request_options=request_options or default_request_options(),
        )


class AsyncTokensClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
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
    ) -> models.ResponseEnvelopeMultiItemsNftToken_:
        """
        NFT Tokens by Contract

        This API returns all NFT tokens that belong to a given contract.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/tokens

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "linea", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.contracts.tokens.list(
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
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}/tokens",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftToken_,
            request_options=request_options or default_request_options(),
        )
