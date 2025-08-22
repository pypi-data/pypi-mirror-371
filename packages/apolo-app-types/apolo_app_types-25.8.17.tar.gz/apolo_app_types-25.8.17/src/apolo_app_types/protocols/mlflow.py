from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from apolo_app_types.protocols.common import (
    AbstractAppFieldType,
    ApoloFilesPath,
    AppInputs,
    AppOutputs,
    IngressHttp,
    Preset,
    RestAPI,
    SchemaExtraMetadata,
)
from apolo_app_types.protocols.common.networking import HttpApi, ServiceAPI
from apolo_app_types.protocols.common.schema_extra import SchemaMetaType
from apolo_app_types.protocols.postgres import PostgresURI


class MLFlowMetadataPostgres(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Postgres",  # pyright: ignore
            description="Use PostgreSQL server as metadata storage for MLFlow.",  # pyright: ignore
        ).as_json_schema_extra(),
    )
    storage_type: Literal["postgres"] = Field(
        default="postgres",
        json_schema_extra=SchemaExtraMetadata(
            title="Storage Type",
            description="Storage type for MLFlow metadata.",
        ).as_json_schema_extra(),
    )
    postgres_uri: PostgresURI


class MLFlowMetadataSQLite(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="SQLite",  # pyright: ignore
            description=(  # pyright: ignore
                "Use SQLite on a dedicated block device as metadata store for MLFlow."
            ),
        ).as_json_schema_extra(),
    )
    storage_type: Literal["sqlite"] = Field(
        default="sqlite",
        json_schema_extra=SchemaExtraMetadata(
            title="Storage Type",
            description="Storage type for MLFlow metadata.",
        ).as_json_schema_extra(),
    )


MLFlowMetaStorage = MLFlowMetadataSQLite | MLFlowMetadataPostgres


class MLFlowAppInputs(AppInputs):
    """
    The overall MLFlow app config, referencing:
      - 'preset' for CPU/GPU resources
      - 'ingress' for external URL
      - 'mlflow_specific' for MLFlow settings
    """

    preset: Preset
    ingress_http: IngressHttp
    metadata_storage: MLFlowMetaStorage
    artifact_store: ApoloFilesPath = Field(
        default=ApoloFilesPath(path="storage:mlflow-artifacts"),
        json_schema_extra=SchemaExtraMetadata(
            description=(
                "Use Apolo Files to store your MLFlow artifacts "
                "(model binaries, dependency files, etc). "
                "E.g. 'storage://cluster/myorg/proj/mlflow-artifacts'"
                "or relative path E.g. 'storage:mlflow-artifacts'"
            ),
            title="Artifact Store",
        ).as_json_schema_extra(),
    )


class MLFlowTrackingServerURL(ServiceAPI[RestAPI]):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="MLFlow Server URL",
            description="The URL to access the MLFlow server.",
        ).as_json_schema_extra(),
    )


class ModelVersionStatus(StrEnum):
    PENDING_REGISTRATION = "PENDING_REGISTRATION"
    FAILED_REGISTRATION = "FAILED_REGISTRATION"
    READY = "READY"


class ModelVersionTag(BaseModel):
    """Tag metadata for model versions"""

    key: str
    value: str


class ModelVersion(BaseModel):
    """Model version information"""

    name: str = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Name", description="Unique name of the model"
        ).as_json_schema_extra(),
    )

    version: str = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Version", description="Model's version number"
        ).as_json_schema_extra(),
    )

    creation_timestamp: int = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Creation Timestamp",
            description="Timestamp recorded when this model_version was created",
        ).as_json_schema_extra(),
    )

    last_updated_timestamp: int = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Last Updated Timestamp",
            description="Timestamp recorded when metadata for this"
            " model_version was last updated",
        ).as_json_schema_extra(),
    )

    user_id: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="User ID", description="User that created this model_version"
        ).as_json_schema_extra(),
    )

    current_stage: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Current Stage", description="Current stage for this model_version"
        ).as_json_schema_extra(),
    )

    description: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Description", description="Description of this model_version"
        ).as_json_schema_extra(),
    )

    source: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Source",
            description="URI indicating the location of the source model artifacts,"
            " used when creating model_version",
        ).as_json_schema_extra(),
    )

    run_id: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Run ID",
            description="MLflow run ID used when creating model_version, if source"
            " was generated by an experiment run stored in MLflow tracking server",
        ).as_json_schema_extra(),
    )

    status: ModelVersionStatus | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Status", description="Current status of model_version"
        ).as_json_schema_extra(),
    )

    status_message: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Status Message",
            description="Details on current status, if it is pending or failed",
        ).as_json_schema_extra(),
    )

    tags: list[ModelVersionTag] = Field(
        default_factory=list,
        json_schema_extra=SchemaExtraMetadata(
            title="Tags",
            description="Tags: Additional metadata key-value pairs for"
            " this model_version",
        ).as_json_schema_extra(),
    )

    run_link: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Run Link",
            description="Run Link: Direct link to the run that generated this version."
            " This field is set at model version creation time only for model versions"
            " whose source run is from a tracking server that is different from the"
            " registry server",
        ).as_json_schema_extra(),
    )

    aliases: list[str] = Field(
        default_factory=list,
        json_schema_extra=SchemaExtraMetadata(
            title="Aliases", description="Aliases pointing to this model_version"
        ).as_json_schema_extra(),
    )


class RegisteredModelTag(BaseModel):
    """Tag metadata for registered models"""

    key: str
    value: str


class RegisteredModelAlias(BaseModel):
    """Alias pointing to model versions"""

    alias: str
    version: str


class RegisteredModel(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Registered Model",
            description="Registered models in MLFlow.",
            meta_type=SchemaMetaType.DYNAMIC,
        ).as_json_schema_extra(),
    )
    name: str = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Name", description="Unique name for the model"
        ).as_json_schema_extra(),
    )

    creation_timestamp: int = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Creation Timestamp",
            description="Timestamp recorded when this registered_model was created",
        ).as_json_schema_extra(),
    )

    last_updated_timestamp: int = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="Last Updated Timestamp",
            description="Timestamp recorded when metadata for"
            " this registered_model was last updated",
        ).as_json_schema_extra(),
    )

    user_id: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="User ID",
            description="User that created this registered_model."
            " NOTE: this field is not currently returned",
        ).as_json_schema_extra(),
    )

    description: str | None = Field(
        None,
        json_schema_extra=SchemaExtraMetadata(
            title="Description", description="Description of this registered_model"
        ).as_json_schema_extra(),
    )

    latest_versions: list[ModelVersion] = Field(
        default_factory=list,
        json_schema_extra=SchemaExtraMetadata(
            title="Latest Versions",
            description="Collection of latest model versions for each stage."
            " Only contains models with current READY status",
        ).as_json_schema_extra(),
    )

    tags: list[RegisteredModelTag] = Field(
        default_factory=list,
        json_schema_extra=SchemaExtraMetadata(
            title="Tags",
            description="Tags: Additional metadata key-value pairs for this"
            " registered_model",
        ).as_json_schema_extra(),
    )

    aliases: list[RegisteredModelAlias] = Field(
        default_factory=list,
        json_schema_extra=SchemaExtraMetadata(
            title="Aliases",
            description="Aliases pointing to model versions associated with"
            " this registered_model",
        ).as_json_schema_extra(),
    )


class MLFlowAppOutputs(AppOutputs):
    web_app_url: ServiceAPI[HttpApi] = Field(
        default=ServiceAPI[HttpApi](),
        json_schema_extra=SchemaExtraMetadata(
            title="MLFlow Web App URL",
            description=("URL to access the MLFlow web application. "),
        ).as_json_schema_extra(),
    )

    server_url: MLFlowTrackingServerURL | None = Field(
        default=None,
        json_schema_extra=SchemaExtraMetadata(
            title="MLFlow Tracking Server URL",
            description=("URL to access the MLFlow tracking server. "),
        ).as_json_schema_extra(),
    )
    registered_models: list[RegisteredModel] | None = Field(
        default=None,
        json_schema_extra=SchemaExtraMetadata(
            title="Registered Models",
            description="List of registered models in MLFlow.",
            meta_type=SchemaMetaType.DYNAMIC,
        ).as_json_schema_extra(),
    )
