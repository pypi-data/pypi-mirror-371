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
from sideko_allium.resources.developer.prices.history import (
    AsyncHistoryClient,
    HistoryClient,
)
from sideko_allium.resources.developer.prices.stats import AsyncStatsClient, StatsClient
from sideko_allium.types import models, params


class PricesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.history = HistoryClient(base_client=self._base_client)
        self.stats = StatsClient(base_client=self._base_client)

    def list(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenPriceV2_:
        """
        Get Latest Prices

        Get the latest prices for the given token addresses.
        Returns price information including timestamp, price, open, high, close, low, and volume.
        Args:
            payloads: List of PayloadTokenAddress objects containing token addresses and chains
        Returns:
            Dictionary mapping chain types to lists of PayloadTokenAddress objects
        Example:
            ```
            [
                {
                    "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
                    "chain": "solana",
                }
            ]
            ```

        POST /api/v1/developer/prices

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            data: typing.List[PayloadTokenAddress]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.prices.list(
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
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.EnvelopeTokenPriceV2_,
            request_options=request_options or default_request_options(),
        )

    def list_at_timestamp(
        self,
        *,
        addresses: typing.List[params.PayloadTokenAddress],
        time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"],
        timestamp: str,
        staleness_tolerance: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenPriceAtTimestamp_:
        """
        Get Prices At Timestamp

        Get the price for a list of token addresses at a given timestamp.
        If a token doesn't have a price at the given timestamp (because there weren't any trades at that time),
        the price will be the price at the closest timestamp before the given timestamp.
        Use 'stalesness_tolerance' to specify the max lookback time (in minutes) for a price.
        Args:
            payloads: PayloadTokenAddressAtTimestamp objects containing timestamp, granularity, stalesness_tolerance and a list of token address + chain pairs.
        Returns:
            Dictionary mapping chain types to lists of PayloadTokenAddressAtTimestamp objects
        Example:
            ```
            [
                {
                    "addresses": [
                        {
                            "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
                            "chain": "solana",
                        }
                    ],
                    "timestamp": "2025-07-11T00:00:00Z",
                    "time_granularity": "5m",
                    "staleness_tolerance": 120,
                }
            ]
            ```

        POST /api/v1/developer/prices/at-timestamp

        Args:
            staleness_tolerance: typing.Optional[str]
            addresses: typing.List[PayloadTokenAddress]
            time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
            timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.prices.list_at_timestamp(
            addresses=[
                {"chain": "string", "token_address": "string"},
                {"chain": "string", "token_address": "string"},
            ],
            time_granularity="5m",
            timestamp="2025-03-07T00:00:00Z",
            staleness_tolerance="1h",
        )
        ```
        """
        _json = to_encodable(
            item={
                "staleness_tolerance": staleness_tolerance,
                "addresses": addresses,
                "time_granularity": time_granularity,
                "timestamp": timestamp,
            },
            dump_with=params._SerializerPayloadTokenAddressAtTimestamp,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/at-timestamp",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=models.EnvelopeTokenPriceAtTimestamp_,
            request_options=request_options or default_request_options(),
        )


class AsyncPricesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.history = AsyncHistoryClient(base_client=self._base_client)
        self.stats = AsyncStatsClient(base_client=self._base_client)

    async def list(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenPriceV2_:
        """
        Get Latest Prices

        Get the latest prices for the given token addresses.
        Returns price information including timestamp, price, open, high, close, low, and volume.
        Args:
            payloads: List of PayloadTokenAddress objects containing token addresses and chains
        Returns:
            Dictionary mapping chain types to lists of PayloadTokenAddress objects
        Example:
            ```
            [
                {
                    "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
                    "chain": "solana",
                }
            ]
            ```

        POST /api/v1/developer/prices

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            data: typing.List[PayloadTokenAddress]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.prices.list(
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
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.EnvelopeTokenPriceV2_,
            request_options=request_options or default_request_options(),
        )

    async def list_at_timestamp(
        self,
        *,
        addresses: typing.List[params.PayloadTokenAddress],
        time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"],
        timestamp: str,
        staleness_tolerance: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenPriceAtTimestamp_:
        """
        Get Prices At Timestamp

        Get the price for a list of token addresses at a given timestamp.
        If a token doesn't have a price at the given timestamp (because there weren't any trades at that time),
        the price will be the price at the closest timestamp before the given timestamp.
        Use 'stalesness_tolerance' to specify the max lookback time (in minutes) for a price.
        Args:
            payloads: PayloadTokenAddressAtTimestamp objects containing timestamp, granularity, stalesness_tolerance and a list of token address + chain pairs.
        Returns:
            Dictionary mapping chain types to lists of PayloadTokenAddressAtTimestamp objects
        Example:
            ```
            [
                {
                    "addresses": [
                        {
                            "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
                            "chain": "solana",
                        }
                    ],
                    "timestamp": "2025-07-11T00:00:00Z",
                    "time_granularity": "5m",
                    "staleness_tolerance": 120,
                }
            ]
            ```

        POST /api/v1/developer/prices/at-timestamp

        Args:
            staleness_tolerance: typing.Optional[str]
            addresses: typing.List[PayloadTokenAddress]
            time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
            timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.prices.list_at_timestamp(
            addresses=[
                {"chain": "string", "token_address": "string"},
                {"chain": "string", "token_address": "string"},
            ],
            time_granularity="5m",
            timestamp="2025-03-07T00:00:00Z",
            staleness_tolerance="1h",
        )
        ```
        """
        _json = to_encodable(
            item={
                "staleness_tolerance": staleness_tolerance,
                "addresses": addresses,
                "time_granularity": time_granularity,
                "timestamp": timestamp,
            },
            dump_with=params._SerializerPayloadTokenAddressAtTimestamp,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/at-timestamp",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=models.EnvelopeTokenPriceAtTimestamp_,
            request_options=request_options or default_request_options(),
        )
