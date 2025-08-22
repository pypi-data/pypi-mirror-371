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


class TokensClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_price_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_supply_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_volume: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.Token]:
        """
        Get Tokens

        POST /api/v1/developer/tokens

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            with_price_info: If true, returns price data.
            with_supply_info: If true, returns total supply.
            with_volume: If true, returns 1h and 24h volume data.
            data: typing.List[PayloadTokenAddress]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.tokens.list(
            data=[{"chain": "string", "token_address": "string"}]
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(with_liquidity_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_liquidity_info",
                to_encodable(item=with_liquidity_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_price_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_price_info",
                to_encodable(item=with_price_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_supply_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_supply_info",
                to_encodable(item=with_supply_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_volume, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_volume",
                to_encodable(item=with_volume, dump_with=bool),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/tokens",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.Token],
            request_options=request_options or default_request_options(),
        )


class AsyncTokensClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_price_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_supply_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        with_volume: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.Token]:
        """
        Get Tokens

        POST /api/v1/developer/tokens

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            with_price_info: If true, returns price data.
            with_supply_info: If true, returns total supply.
            with_volume: If true, returns 1h and 24h volume data.
            data: typing.List[PayloadTokenAddress]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.tokens.list(
            data=[{"chain": "string", "token_address": "string"}]
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(with_liquidity_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_liquidity_info",
                to_encodable(item=with_liquidity_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_price_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_price_info",
                to_encodable(item=with_price_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_supply_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_supply_info",
                to_encodable(item=with_supply_info, dump_with=bool),
                style="form",
                explode=True,
            )
        if not isinstance(with_volume, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_volume",
                to_encodable(item=with_volume, dump_with=bool),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/tokens",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=typing.List[models.Token],
            request_options=request_options or default_request_options(),
        )
