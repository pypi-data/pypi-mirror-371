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


class ActivitiesClient:
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
        activity_types: typing.Union[
            typing.Optional[
                typing.List[typing_extensions.Literal["mint", "sale", "transfer"]]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftActivity_:
        """
        NFT Activities by Contract Address

        Fetch a list of NFT Activities by contract address.

        GET /api/v1/developer/nfts/activities/{chain}/{contract_address}

        Args:
            activity_types: Types of activities to fetch.
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
        client.developer.nfts.activities.list_by_contact_address(
            chain="abstract", contract_address="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(activity_types, type_utils.NotGiven):
            encode_query_param(
                _query,
                "activity_types",
                to_encodable(
                    item=activity_types,
                    dump_with=typing.List[
                        typing_extensions.Literal["mint", "sale", "transfer"]
                    ],
                ),
                style="form",
                explode=True,
            )
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
            path=f"/api/v1/developer/nfts/activities/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftActivity_,
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
        activity_types: typing.Union[
            typing.Optional[
                typing.List[typing_extensions.Literal["mint", "sale", "transfer"]]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftActivity_:
        """
        NFT Activities by Token ID

        Get a list of NFT Activities by token ID.

        GET /api/v1/developer/nfts/activities/{chain}/{contract_address}/{token_id}

        Args:
            activity_types: Types of activities to fetch.
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
        client.developer.nfts.activities.list_by_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(activity_types, type_utils.NotGiven):
            encode_query_param(
                _query,
                "activity_types",
                to_encodable(
                    item=activity_types,
                    dump_with=typing.List[
                        typing_extensions.Literal["mint", "sale", "transfer"]
                    ],
                ),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/activities/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftActivity_,
            request_options=request_options or default_request_options(),
        )


class AsyncActivitiesClient:
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
        activity_types: typing.Union[
            typing.Optional[
                typing.List[typing_extensions.Literal["mint", "sale", "transfer"]]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftActivity_:
        """
        NFT Activities by Contract Address

        Fetch a list of NFT Activities by contract address.

        GET /api/v1/developer/nfts/activities/{chain}/{contract_address}

        Args:
            activity_types: Types of activities to fetch.
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
        await client.developer.nfts.activities.list_by_contact_address(
            chain="abstract", contract_address="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(activity_types, type_utils.NotGiven):
            encode_query_param(
                _query,
                "activity_types",
                to_encodable(
                    item=activity_types,
                    dump_with=typing.List[
                        typing_extensions.Literal["mint", "sale", "transfer"]
                    ],
                ),
                style="form",
                explode=True,
            )
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
            path=f"/api/v1/developer/nfts/activities/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftActivity_,
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
        activity_types: typing.Union[
            typing.Optional[
                typing.List[typing_extensions.Literal["mint", "sale", "transfer"]]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsNftActivity_:
        """
        NFT Activities by Token ID

        Get a list of NFT Activities by token ID.

        GET /api/v1/developer/nfts/activities/{chain}/{contract_address}/{token_id}

        Args:
            activity_types: Types of activities to fetch.
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
        await client.developer.nfts.activities.list_by_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(activity_types, type_utils.NotGiven):
            encode_query_param(
                _query,
                "activity_types",
                to_encodable(
                    item=activity_types,
                    dump_with=typing.List[
                        typing_extensions.Literal["mint", "sale", "transfer"]
                    ],
                ),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/activities/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ResponseEnvelopeMultiItemsNftActivity_,
            request_options=request_options or default_request_options(),
        )
