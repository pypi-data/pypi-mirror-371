import logging
import time
from collections.abc import AsyncIterator, Sequence
from contextlib import (
    asynccontextmanager,
)
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    ContentBlock,
    TextContent,
)

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.tools import register_lightdash_tools
from dbt_mcp.lightdash.prompts import register_lightdash_prompts
from dbt_mcp.lightdash.resources import register_lightdash_resources
from dbt_mcp.tracking.tracking import UsageTracker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    logger.info("Starting MCP server")
    try:
        yield
    except Exception as e:
        logger.error(f"Error in MCP server: {e}")
        raise e
    finally:
        logger.info("Shutting down MCP server")
        # Only shutdown vortex if it was imported (when dbt features are enabled)
        try:
            from dbtlabs_vortex.producer import shutdown
            shutdown()
        except ImportError:
            pass


class DbtMCP(FastMCP):
    def __init__(
        self,
        config: Config,
        usage_tracker: UsageTracker,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.usage_tracker = usage_tracker
        self.config = config

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any]:
        logger.info(f"Calling tool: {name}")
        result = None
        start_time = int(time.time() * 1000)
        try:
            result = await super().call_tool(
                name,
                arguments,
            )
        except Exception as e:
            end_time = int(time.time() * 1000)
            logger.error(
                f"Error calling tool: {name} with arguments: {arguments} "
                + f"in {end_time - start_time}ms: {e}"
            )
            self.usage_tracker.emit_tool_called_event(
                config=self.config.tracking_config,
                tool_name=name,
                arguments=arguments,
                start_time_ms=start_time,
                end_time_ms=end_time,
                error_message=str(e),
            )
            return [
                TextContent(
                    type="text",
                    text=str(e),
                )
            ]
        end_time = int(time.time() * 1000)
        logger.info(f"Tool {name} called successfully in {end_time - start_time}ms")
        self.usage_tracker.emit_tool_called_event(
            config=self.config.tracking_config,
            tool_name=name,
            arguments=arguments,
            start_time_ms=start_time,
            end_time_ms=end_time,
            error_message=None,
        )
        return result


async def create_dbt_mcp(config: Config):
    dbt_mcp = DbtMCP(
        config=config,
        usage_tracker=UsageTracker(),
        name="dbt",
        lifespan=app_lifespan,
    )

    if config.semantic_layer_config:
        logger.info("Registering semantic layer tools")
        from dbt_mcp.semantic_layer.tools import register_sl_tools
        register_sl_tools(dbt_mcp, config.semantic_layer_config, config.disable_tools)

    if config.discovery_config:
        logger.info("Registering discovery tools")
        from dbt_mcp.discovery.tools import register_discovery_tools
        register_discovery_tools(dbt_mcp, config.discovery_config, config.disable_tools)

    if config.dbt_cli_config:
        logger.info("Registering dbt cli tools")
        # TODO: allow for disabling CLI tools
        from dbt_mcp.dbt_cli.tools import register_dbt_cli_tools
        register_dbt_cli_tools(dbt_mcp, config.dbt_cli_config, [])

    if config.remote_config:
        logger.info("Registering remote tools")
        from dbt_mcp.remote.tools import register_remote_tools
        await register_remote_tools(dbt_mcp, config.remote_config, config.disable_tools)

    if config.lightdash_config:
        logger.info("Registering Lightdash tools")
        register_lightdash_tools(dbt_mcp, config.lightdash_config, config.disable_tools)
        logger.info("Registering Lightdash prompts")
        register_lightdash_prompts(dbt_mcp, config.lightdash_config)
        logger.info("Registering Lightdash resources")
        register_lightdash_resources(dbt_mcp, config.lightdash_config)

    return dbt_mcp
