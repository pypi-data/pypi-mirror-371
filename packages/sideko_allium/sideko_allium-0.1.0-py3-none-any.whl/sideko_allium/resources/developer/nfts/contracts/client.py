import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
)
from sideko_allium.resources.developer.nfts.contracts.tokens import (
    AsyncTokensClient,
    TokensClient,
)
from sideko_allium.types import models


class ContractsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.tokens = TokensClient(base_client=self._base_client)

    def get_metadata(
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftContract_:
        """
        NFT Contract

        This API returns the NFT contract metadata associated with the contract address.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}

        Args:
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.contracts.get_metadata(
            chain="abstract", contract_address="string"
        )
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.ResponseEnvelopeSingleItemNftContract_,
            request_options=request_options or default_request_options(),
        )

    def get_by_contract_and_token_id(
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
            "solana",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        token_id: typing.Optional[str],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftToken_:
        """
        NFT Token by Contract and Token ID

        This API returns NFT token metadata by contract and token ID. For Solana, pass in a token ID of 0.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/{token_id}

        Args:
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "solana", "soneium", "xai", "zero", "zora"]
            contract_address: str
            token_id: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.nfts.contracts.get_by_contract_and_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.ResponseEnvelopeSingleItemNftToken_,
            request_options=request_options or default_request_options(),
        )


class AsyncContractsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.tokens = AsyncTokensClient(base_client=self._base_client)

    async def get_metadata(
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
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftContract_:
        """
        NFT Contract

        This API returns the NFT contract metadata associated with the contract address.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}

        Args:
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "soneium", "xai", "zero", "zora"]
            contract_address: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.contracts.get_metadata(
            chain="abstract", contract_address="string"
        )
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.ResponseEnvelopeSingleItemNftContract_,
            request_options=request_options or default_request_options(),
        )

    async def get_by_contract_and_token_id(
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
            "solana",
            "soneium",
            "xai",
            "zero",
            "zora",
        ],
        contract_address: str,
        token_id: typing.Optional[str],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeSingleItemNftToken_:
        """
        NFT Token by Contract and Token ID

        This API returns NFT token metadata by contract and token ID. For Solana, pass in a token ID of 0.

        GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/{token_id}

        Args:
            chain: typing_extensions.Literal["abstract", "apechain", "arbitrum", "arbitrum-nova", "avalanche", "base", "ethereum", "optimism", "polygon", "shape", "solana", "soneium", "xai", "zero", "zora"]
            contract_address: str
            token_id: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.nfts.contracts.get_by_contract_and_token_id(
            chain="abstract", contract_address="string", token_id="string"
        )
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/nfts/contracts/{chain}/{contract_address}/{token_id}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.ResponseEnvelopeSingleItemNftToken_,
            request_options=request_options or default_request_options(),
        )
