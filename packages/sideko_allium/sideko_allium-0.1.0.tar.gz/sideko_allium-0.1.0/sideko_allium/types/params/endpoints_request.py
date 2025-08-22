import pydantic
import typing
import typing_extensions


class EndpointsRequest(typing_extensions.TypedDict):
    """
    EndpointsRequest
    """

    endpoints: typing_extensions.Required[
        typing.List[
            typing_extensions.Literal[
                "custom_sql",
                "historical_fungible_token_balances",
                "latest_fungible_token_balances",
                "latest_nft_balances",
                "nft_apis",
                "pnl",
                "token_latest_price",
                "token_price_historical",
                "token_price_stats",
                "wallet_transactions",
            ]
        ]
    ]


class _SerializerEndpointsRequest(pydantic.BaseModel):
    """
    Serializer for EndpointsRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    endpoints: typing.List[
        typing_extensions.Literal[
            "custom_sql",
            "historical_fungible_token_balances",
            "latest_fungible_token_balances",
            "latest_nft_balances",
            "nft_apis",
            "pnl",
            "token_latest_price",
            "token_price_historical",
            "token_price_stats",
            "wallet_transactions",
        ]
    ] = pydantic.Field(
        alias="endpoints",
    )
