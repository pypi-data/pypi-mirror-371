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


class LatestSolanaNftBalancesClient:
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.WalletNftLatestBalance]:
        """
        Latest Solana NFT Balances

        Get the latest NFT balances for a single Solana wallet.

        POST /api/v1/developer/wallet/latest-solana-nft-balances

        Args:
            cursor: typing.Optional[str]
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
        client.developer.wallet.latest_solana_nft_balances.get(
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
        _json = to_encodable(
            item={"address": address, "chain": chain},
            dump_with=params._SerializerPayloadAddress,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/latest-solana-nft-balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.WalletNftLatestBalance],
            request_options=request_options or default_request_options(),
        )


class AsyncLatestSolanaNftBalancesClient:
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.WalletNftLatestBalance]:
        """
        Latest Solana NFT Balances

        Get the latest NFT balances for a single Solana wallet.

        POST /api/v1/developer/wallet/latest-solana-nft-balances

        Args:
            cursor: typing.Optional[str]
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
        await client.developer.wallet.latest_solana_nft_balances.get(
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
        _json = to_encodable(
            item={"address": address, "chain": chain},
            dump_with=params._SerializerPayloadAddress,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/latest-solana-nft-balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.WalletNftLatestBalance],
            request_options=request_options or default_request_options(),
        )
