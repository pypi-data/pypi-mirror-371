import pydantic
import typing
import typing_extensions


class IngestJob(pydantic.BaseModel):
    """
    IngestJob
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    created_at: str = pydantic.Field(
        alias="created_at",
    )
    creator_organization_id: str = pydantic.Field(
        alias="creator_organization_id",
    )
    job_id: str = pydantic.Field(
        alias="job_id",
    )
    overwrite: bool = pydantic.Field(
        alias="overwrite",
    )
    status: typing.Optional[
        typing_extensions.Literal[
            "completed", "failed", "queued", "running", "up_for_retry"
        ]
    ] = pydantic.Field(alias="status", default=None)
    table_name: str = pydantic.Field(
        alias="table_name",
    )
    updated_at: str = pydantic.Field(
        alias="updated_at",
    )
