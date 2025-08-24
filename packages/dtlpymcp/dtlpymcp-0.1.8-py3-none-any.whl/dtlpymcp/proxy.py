
from mcp.server.fastmcp import FastMCP, Context
from typing import Any, Optional
import traceback
import os

from dtlpymcp.utils.dtlpy_context import DataloopContext
from dtlpymcp.utils.server_utils import safe_initialize_dataloop_context
from dtlpymcp.utils.logging_config import setup_logging, get_logger

# Get the main logger
logger = get_logger()


def create_dataloop_mcp_server(sources_file: Optional[str] = None, init_timeout: float = 30.0) -> FastMCP:
    """Create a FastMCP server for Dataloop with Bearer token authentication."""
    app = FastMCP(
        name="Dataloop MCP Server",
        instructions="A multi-tenant MCP server for Dataloop with authentication",
        stateless_http=True,
        debug=True,
    )
    
    # Create Dataloop context
    dl_context = DataloopContext(token=os.environ.get('DATALOOP_API_KEY'), 
                                 env=os.environ.get('DATALOOP_ENV', 'prod'),
                                 sources_file=sources_file)
    
    @app.tool(description="Test tool for health checks")
    async def test(ctx: Context, ping: Any = None) -> dict[str, Any]:
        """Health check tool. Returns status ok and echoes ping if provided."""
        result = {"status": "ok"}
        if ping is not None:
            result["ping"] = ping
        return result

    # Initialize context using the safe utility function
    initialization_success = safe_initialize_dataloop_context(dl_context, app, init_timeout)
    
    if not initialization_success:
        logger.info("Server will start without Dataloop tools - they will be available on next restart")
        # Continue without initialization - the server will still work with the test tool
    
    return app


def main(sources_file: Optional[str] = None, init_timeout: float = 30.0, log_level: str = "DEBUG") -> int:
    # Setup logging with the specified level
    setup_logging(log_level)
    
    logger.info("Starting Dataloop MCP server in stdio mode")
    
    # Validate environment variables
    if not os.environ.get('DATALOOP_API_KEY'):
        logger.error("DATALOOP_API_KEY environment variable is required")
        return 1
    
    try:
        mcp_server = create_dataloop_mcp_server(sources_file=sources_file, init_timeout=init_timeout)
        logger.info("Dataloop MCP server created successfully")
        logger.info("Starting server in stdio mode...")
        mcp_server.run(transport="stdio")
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    main()
