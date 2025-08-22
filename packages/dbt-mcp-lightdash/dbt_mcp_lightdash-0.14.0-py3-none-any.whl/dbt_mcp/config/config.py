import os
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from dbt_mcp.tools.tool_names import ToolName


class TrackingConfig(BaseModel):
    host: str | None = None
    multicell_account_prefix: str | None = None
    prod_environment_id: int | None = None
    dev_environment_id: int | None = None
    dbt_cloud_user_id: int | None = None
    local_user_id: str | None = None


class SemanticLayerConfig(BaseModel):
    url: str
    host: str
    prod_environment_id: int
    service_token: str
    headers: dict[str, str]


class DiscoveryConfig(BaseModel):
    url: str
    headers: dict[str, str]
    environment_id: int


class DbtCliConfig(BaseModel):
    project_dir: str
    dbt_path: str
    dbt_cli_timeout: int


class RemoteConfig(BaseModel):
    multicell_account_prefix: str | None = None
    host: str
    user_id: int
    dev_environment_id: int
    prod_environment_id: int
    token: str


class LightdashConfig(BaseModel):
    api_url: str
    api_key: str
    project_id: str
    default_space_id: str | None = None
    default_chart_type: str = "table"


class DbtMcpSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment variables with proper field configuration
    dbt_host: str | None = Field(None, alias="DBT_HOST")
    dbt_mcp_host: str | None = Field(None, alias="DBT_MCP_HOST")
    dbt_prod_env_id: int | None = Field(None, alias="DBT_PROD_ENV_ID")
    dbt_env_id: int | None = Field(None, alias="DBT_ENV_ID")  # legacy support
    dbt_dev_env_id: int | None = Field(None, alias="DBT_DEV_ENV_ID")
    dbt_user_id: int | None = Field(None, alias="DBT_USER_ID")
    dbt_token: str | None = Field(None, alias="DBT_TOKEN")
    dbt_project_dir: str | None = Field(None, alias="DBT_PROJECT_DIR")
    dbt_path: str = Field("dbt", alias="DBT_PATH")
    dbt_cli_timeout: int = Field(10, alias="DBT_CLI_TIMEOUT")
    dbt_warn_error_options: str | None = Field(None, alias="DBT_WARN_ERROR_OPTIONS")

    disable_dbt_cli: bool = Field(False, alias="DISABLE_DBT_CLI")
    disable_semantic_layer: bool = Field(False, alias="DISABLE_SEMANTIC_LAYER")
    disable_discovery: bool = Field(False, alias="DISABLE_DISCOVERY")
    disable_remote: bool = Field(True, alias="DISABLE_REMOTE")
    disable_tools: Annotated[list[ToolName] | None, NoDecode] = Field(
        None, alias="DISABLE_TOOLS"
    )

    multicell_account_prefix: str | None = Field(None, alias="MULTICELL_ACCOUNT_PREFIX")
    
    # Lightdash configuration
    lightdash_api_url: str | None = Field(None, alias="LIGHTDASH_API_URL")
    lightdash_api_key: str | None = Field(None, alias="LIGHTDASH_API_KEY")
    lightdash_project_id: str | None = Field(None, alias="LIGHTDASH_PROJECT_ID")
    lightdash_default_space_id: str | None = Field(None, alias="LIGHTDASH_DEFAULT_SPACE_ID")
    lightdash_default_chart_type: str = Field("table", alias="LIGHTDASH_DEFAULT_CHART_TYPE")
    disable_lightdash: bool = Field(False, alias="DISABLE_LIGHTDASH")

    @property
    def actual_host(self) -> str | None:
        return self.dbt_host or self.dbt_mcp_host

    @property
    def actual_prod_environment_id(self) -> int | None:
        return self.dbt_prod_env_id or self.dbt_env_id

    @field_validator("disable_tools", mode="before")
    @classmethod
    def parse_disable_tools(cls, env_var: str | None) -> list[ToolName]:
        if not env_var:
            return []
        errors: list[str] = []
        tool_names: list[ToolName] = []
        for tool_name in env_var.split(","):
            tool_name_stripped = tool_name.strip()
            if tool_name_stripped == "":
                continue
            try:
                tool_names.append(ToolName(tool_name_stripped))
            except ValueError:
                errors.append(
                    f"Invalid tool name in DISABLE_TOOLS: {tool_name_stripped}."
                    + " Must be a valid tool name."
                )
        if errors:
            raise ValueError("\n".join(errors))
        return tool_names


class Config(BaseModel):
    tracking_config: TrackingConfig
    remote_config: RemoteConfig | None = None
    dbt_cli_config: DbtCliConfig | None = None
    discovery_config: DiscoveryConfig | None = None
    semantic_layer_config: SemanticLayerConfig | None = None
    lightdash_config: LightdashConfig | None = None
    disable_tools: list[ToolName]


def load_config() -> Config:
    # Load settings from environment variables using pydantic_settings
    settings = DbtMcpSettings()  # type: ignore[call-arg]

    # Set default warn error options if not provided
    if settings.dbt_warn_error_options is None:
        warn_error_options = '{"error": ["NoNodesForSelectionCriteria"]}'
        os.environ["DBT_WARN_ERROR_OPTIONS"] = warn_error_options

    # Validation
    errors: list[str] = []
    if (
        not settings.disable_semantic_layer
        or not settings.disable_discovery
        or not settings.disable_remote
    ):
        if not settings.actual_host:
            errors.append(
                "DBT_HOST environment variable is required when semantic layer, discovery, or remote tools are enabled."
            )
        if not settings.actual_prod_environment_id:
            errors.append(
                "DBT_PROD_ENV_ID environment variable is required when semantic layer, discovery, or remote tools are enabled."
            )
        if not settings.dbt_token:
            errors.append(
                "DBT_TOKEN environment variable is required when semantic layer, discovery, or remote tools are enabled."
            )
        if settings.actual_host and (
            settings.actual_host.startswith("metadata")
            or settings.actual_host.startswith("semantic-layer")
        ):
            errors.append(
                "DBT_HOST must not start with 'metadata' or 'semantic-layer'."
            )
    if not settings.disable_remote:
        if not settings.dbt_dev_env_id:
            errors.append(
                "DBT_DEV_ENV_ID environment variable is required when remote tools are enabled."
            )
        if not settings.dbt_user_id:
            errors.append(
                "DBT_USER_ID environment variable is required when remote tools are enabled."
            )
    if not settings.disable_dbt_cli:
        if not settings.dbt_project_dir:
            errors.append(
                "DBT_PROJECT_DIR environment variable is required when dbt CLI tools are enabled."
            )
        if not settings.dbt_path:
            errors.append(
                "DBT_PATH environment variable is required when dbt CLI tools are enabled."
            )
    
    if not settings.disable_lightdash:
        if not settings.lightdash_api_url:
            errors.append(
                "LIGHTDASH_API_URL environment variable is required when Lightdash tools are enabled."
            )
        if not settings.lightdash_api_key:
            errors.append(
                "LIGHTDASH_API_KEY environment variable is required when Lightdash tools are enabled."
            )
        if not settings.lightdash_project_id:
            errors.append(
                "LIGHTDASH_PROJECT_ID environment variable is required when Lightdash tools are enabled."
            )

    if errors:
        raise ValueError("Errors found in configuration:\n\n" + "\n".join(errors))

    # Build configurations
    remote_config = None
    if (
        not settings.disable_remote
        and settings.dbt_user_id
        and settings.dbt_token
        and settings.dbt_dev_env_id
        and settings.actual_prod_environment_id
        and settings.actual_host
    ):
        remote_config = RemoteConfig(
            multicell_account_prefix=settings.multicell_account_prefix,
            user_id=settings.dbt_user_id,
            token=settings.dbt_token,
            dev_environment_id=settings.dbt_dev_env_id,
            prod_environment_id=settings.actual_prod_environment_id,
            host=settings.actual_host,
        )

    dbt_cli_config = None
    if not settings.disable_dbt_cli and settings.dbt_project_dir and settings.dbt_path:
        dbt_cli_config = DbtCliConfig(
            project_dir=settings.dbt_project_dir,
            dbt_path=settings.dbt_path,
            dbt_cli_timeout=settings.dbt_cli_timeout,
        )

    discovery_config = None
    if (
        not settings.disable_discovery
        and settings.actual_host
        and settings.actual_prod_environment_id
        and settings.dbt_token
    ):
        if settings.multicell_account_prefix:
            url = f"https://{settings.multicell_account_prefix}.metadata.{settings.actual_host}/graphql"
        else:
            url = f"https://metadata.{settings.actual_host}/graphql"
        discovery_config = DiscoveryConfig(
            url=url,
            headers={
                "Authorization": f"Bearer {settings.dbt_token}",
                "Content-Type": "application/json",
            },
            environment_id=settings.actual_prod_environment_id,
        )

    semantic_layer_config = None
    if (
        not settings.disable_semantic_layer
        and settings.actual_host
        and settings.actual_prod_environment_id
        and settings.dbt_token
    ):
        is_local = settings.actual_host and settings.actual_host.startswith("localhost")
        if is_local:
            host = settings.actual_host
        elif settings.multicell_account_prefix:
            host = f"{settings.multicell_account_prefix}.semantic-layer.{settings.actual_host}"
        else:
            host = f"semantic-layer.{settings.actual_host}"
        assert host is not None

        semantic_layer_config = SemanticLayerConfig(
            url=f"http://{host}" if is_local else f"https://{host}" + "/api/graphql",
            host=host,
            prod_environment_id=settings.actual_prod_environment_id,
            service_token=settings.dbt_token,
            headers={
                "Authorization": f"Bearer {settings.dbt_token}",
                "x-dbt-partner-source": "dbt-mcp",
            },
        )

    # Build Lightdash configuration
    lightdash_config = None
    if (
        not settings.disable_lightdash
        and settings.lightdash_api_url
        and settings.lightdash_api_key
        and settings.lightdash_project_id
    ):
        lightdash_config = LightdashConfig(
            api_url=settings.lightdash_api_url,
            api_key=settings.lightdash_api_key,
            project_id=settings.lightdash_project_id,
            default_space_id=settings.lightdash_default_space_id,
            default_chart_type=settings.lightdash_default_chart_type,
        )

    # Load local user ID from dbt profile
    local_user_id = None
    try:
        home = os.environ.get("HOME")
        user_path = Path(f"{home}/.dbt/.user.yml")
        if home and user_path.exists():
            with open(user_path) as f:
                local_user_id = yaml.safe_load(f).get("id")
    except Exception:
        pass

    return Config(
        tracking_config=TrackingConfig(
            host=settings.actual_host,
            multicell_account_prefix=settings.multicell_account_prefix,
            prod_environment_id=settings.actual_prod_environment_id,
            dev_environment_id=settings.dbt_dev_env_id,
            dbt_cloud_user_id=settings.dbt_user_id,
            local_user_id=local_user_id,
        ),
        remote_config=remote_config,
        dbt_cli_config=dbt_cli_config,
        discovery_config=discovery_config,
        semantic_layer_config=semantic_layer_config,
        lightdash_config=lightdash_config,
        disable_tools=settings.disable_tools or [],
    )
