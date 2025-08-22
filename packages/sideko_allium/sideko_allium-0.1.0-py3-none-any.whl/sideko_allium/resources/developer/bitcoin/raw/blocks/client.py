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
from sideko_allium.types import models


class BlocksClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/bitcoin/raw/blocks

        Args:
            page: Page number
            size: Page size
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.bitcoin.raw.blocks.list()
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
            path="/api/v1/developer/bitcoin/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        block_number: int,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/bitcoin/raw/blocks/{block_number}

        Args:
            block_number: int
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.bitcoin.raw.blocks.get(block_number=123)
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/bitcoin/raw/blocks/{block_number}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock,
            request_options=request_options or default_request_options(),
        )


class AsyncBlocksClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/bitcoin/raw/blocks

        Args:
            page: Page number
            size: Page size
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.bitcoin.raw.blocks.list()
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
            path="/api/v1/developer/bitcoin/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        block_number: int,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/bitcoin/raw/blocks/{block_number}

        Args:
            block_number: int
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.bitcoin.raw.blocks.get(block_number=123)
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/bitcoin/raw/blocks/{block_number}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock,
            request_options=request_options or default_request_options(),
        )
