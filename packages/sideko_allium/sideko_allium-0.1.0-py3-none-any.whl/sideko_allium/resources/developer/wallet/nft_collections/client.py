import typing

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
from sideko_allium.types import models, params


class NftCollectionsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        address: str,
        chain: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.NftCollection]:
        """
        NFT Collections owned by wallet

        Get all NFT collections owned by a wallet

        POST /api/v1/developer/wallet/nft-collections

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            address: str
            chain: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.nft_collections.get(address="string", chain="string")
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
        _json = to_encodable(
            item={"address": address, "chain": chain},
            dump_with=params._SerializerPayloadAddress,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/nft-collections",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.NftCollection],
            request_options=request_options or default_request_options(),
        )


class AsyncNftCollectionsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        address: str,
        chain: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.NftCollection]:
        """
        NFT Collections owned by wallet

        Get all NFT collections owned by a wallet

        POST /api/v1/developer/wallet/nft-collections

        Args:
            cursor: typing.Optional[str]
            limit: Number of items to return in a response.
            address: str
            chain: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.nft_collections.get(
            address="string", chain="string"
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
        _json = to_encodable(
            item={"address": address, "chain": chain},
            dump_with=params._SerializerPayloadAddress,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/nft-collections",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.NftCollection],
            request_options=request_options or default_request_options(),
        )
