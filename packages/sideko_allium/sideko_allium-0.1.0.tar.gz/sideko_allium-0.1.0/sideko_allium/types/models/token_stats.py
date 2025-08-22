import pydantic


class TokenStats(pydantic.BaseModel):
    """
    TokenStats
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    decimals: int = pydantic.Field(
        alias="decimals",
    )
    high_1h: float = pydantic.Field(
        alias="high_1h",
    )
    high_24h: float = pydantic.Field(
        alias="high_24h",
    )
    high_all_time: float = pydantic.Field(
        alias="high_all_time",
    )
    latest_price: float = pydantic.Field(
        alias="latest_price",
    )
    low_1h: float = pydantic.Field(
        alias="low_1h",
    )
    low_24h: float = pydantic.Field(
        alias="low_24h",
    )
    low_all_time: float = pydantic.Field(
        alias="low_all_time",
    )
    mint: str = pydantic.Field(
        alias="mint",
    )
    percent_change_1h: float = pydantic.Field(
        alias="percent_change_1h",
    )
    percent_change_24h: float = pydantic.Field(
        alias="percent_change_24h",
    )
    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
    volume_1h: float = pydantic.Field(
        alias="volume_1h",
    )
    volume_24h: float = pydantic.Field(
        alias="volume_24h",
    )
