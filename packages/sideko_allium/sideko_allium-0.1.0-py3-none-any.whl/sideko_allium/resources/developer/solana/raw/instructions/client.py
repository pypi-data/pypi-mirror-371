import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import models, params


class InstructionsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        data: typing.List[params.TransactionBasedRequest],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.Instruction]:
        """
        Get Instructions

        POST /api/v1/developer/solana/raw/instructions

        Args:
            data: typing.List[TransactionBasedRequest]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.solana.raw.instructions.get(
            data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerTransactionBasedRequest]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/solana/raw/instructions",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=typing.List[models.Instruction],
            request_options=request_options or default_request_options(),
        )


class AsyncInstructionsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        data: typing.List[params.TransactionBasedRequest],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.Instruction]:
        """
        Get Instructions

        POST /api/v1/developer/solana/raw/instructions

        Args:
            data: typing.List[TransactionBasedRequest]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.solana.raw.instructions.get(
            data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerTransactionBasedRequest]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/solana/raw/instructions",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=typing.List[models.Instruction],
            request_options=request_options or default_request_options(),
        )
