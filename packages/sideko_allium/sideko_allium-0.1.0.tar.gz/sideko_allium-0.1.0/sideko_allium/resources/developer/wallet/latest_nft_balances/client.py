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


class LatestNftBalancesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        exclude_spam: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.WalletNftLatestBalance]:
        """
        Latest NFT Balances

        Get the latest NFT balances for a list of wallets.

        POST /api/v1/developer/wallet/latest-nft-balances

        Args:
            cursor: typing.Optional[str]
            exclude_spam: Exclude spam NFTs
            limit: Number of items to return in a response.
            data: List of wallet chain+address pairs to get balances for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.latest_nft_balances.get(
            data=[{"address": "string", "chain": "string"}]
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
        if not isinstance(exclude_spam, type_utils.NotGiven):
            encode_query_param(
                _query,
                "exclude_spam",
                to_encodable(item=exclude_spam, dump_with=bool),
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
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/latest-nft-balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.WalletNftLatestBalance],
            request_options=request_options or default_request_options(),
        )


class AsyncLatestNftBalancesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        exclude_spam: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.WalletNftLatestBalance]:
        """
        Latest NFT Balances

        Get the latest NFT balances for a list of wallets.

        POST /api/v1/developer/wallet/latest-nft-balances

        Args:
            cursor: typing.Optional[str]
            exclude_spam: Exclude spam NFTs
            limit: Number of items to return in a response.
            data: List of wallet chain+address pairs to get balances for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.latest_nft_balances.get(
            data=[{"address": "string", "chain": "string"}]
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
        if not isinstance(exclude_spam, type_utils.NotGiven):
            encode_query_param(
                _query,
                "exclude_spam",
                to_encodable(item=exclude_spam, dump_with=bool),
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
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/latest-nft-balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.WalletNftLatestBalance],
            request_options=request_options or default_request_options(),
        )
