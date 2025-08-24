"""
Utility functions for Dataloop MCP server initialization and management.
"""

import asyncio
from mcp.server.fastmcp import FastMCP
from dtlpymcp.utils.dtlpy_context import DataloopContext
from dtlpymcp.utils.logging_config import get_logger

logger = get_logger("server_utils")


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running
        return asyncio.run(coro)
    else:
        # Already running event loop
        return loop.create_task(coro)


async def initialize_dataloop_context(dl_context: DataloopContext, app: FastMCP, init_timeout: float = 30.0) -> bool:
    """
    Initialize Dataloop context with timeout protection.

    Args:
        dl_context: The DataloopContext instance to initialize
        app: The FastMCP app instance to register tools with
        init_timeout: Timeout in seconds for initialization

    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    try:
        logger.info("Initializing Dataloop context...")
        # Use asyncio.wait_for for timeout protection
        await asyncio.wait_for(dl_context.initialize(), timeout=init_timeout)
        logger.info("Dataloop context initialized successfully")

        # Register tools after initialization
        logger.info(f"Adding tools from {len(dl_context.mcp_sources)} sources")
        for source in dl_context.mcp_sources:
            logger.info(f"Adding tools from source: {source.dpk_name}")
            for tool in source.tools:
                app._tool_manager._tools[tool.name] = tool
                logger.info(f"Registered tool: {tool.name}")

        return True

    except asyncio.TimeoutError:
        logger.error("Timeout during Dataloop context initialization")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Dataloop context: {e}")
        return False


def safe_initialize_dataloop_context(dl_context: DataloopContext, app: FastMCP, init_timeout: float = 30.0) -> bool:
    """
    Safely initialize Dataloop context using run_async utility.

    Args:
        dl_context: The DataloopContext instance to initialize
        app: The FastMCP app instance to register tools with
        init_timeout: Timeout in seconds for initialization

    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    try:
        # Use the run_async utility to handle async execution properly
        result = run_async(initialize_dataloop_context(dl_context, app, init_timeout))

        # Handle different return types from run_async
        if hasattr(result, 'done'):
            # It's a task, wait for it to complete
            while not result.done():
                pass
            return result.result()
        elif asyncio.iscoroutine(result):
            # It's a coroutine, run it
            return asyncio.run(result)
        else:
            # It's already the result (bool)
            return result

    except Exception as e:
        logger.error(f"Failed to initialize during server creation: {e}")
        return False
