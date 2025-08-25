"""MCP command module - handles Model Context Protocol server operations."""

import argparse
import os
import sys
from pathlib import Path


async def mcp_command(args: argparse.Namespace, config) -> None:
    """Execute the MCP server command.

    Args:
        args: Parsed command-line arguments containing database path
        config: Pre-validated configuration instance
    """
    # Set MCP mode environment early
    os.environ["CHUNKHOUND_MCP_MODE"] = "1"

    # CRITICAL: Import numpy modules early for DuckDB threading safety in MCP mode
    # Must happen before any DuckDB operations in async/threading context
    # See: https://duckdb.org/docs/stable/clients/python/known_issues.html
    try:
        import numpy  # noqa: F401
    except ImportError:
        pass


    # Handle transport selection
    if hasattr(args, "http") and args.http:
        # Use HTTP transport via subprocess to avoid event loop conflicts
        import subprocess

        # Use config values instead of hardcoded fallbacks
        # CLI args override config values
        host = getattr(args, "host", None) or config.mcp.host
        port = getattr(args, "port", None) or config.mcp.port

        # Run HTTP server in subprocess
        cmd = [
            sys.executable,
            "-m",
            "chunkhound.mcp.http_server",
            "--host",
            str(host),
            "--port",
            str(port),
        ]

        if hasattr(args, "db") and args.db:
            cmd.extend(["--db", str(args.db)])

        process = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=os.environ.copy(),
        )
        sys.exit(process.returncode)
    else:
        # Use stdio transport (default)
        from chunkhound.mcp.stdio import main

        await main(args=args)


__all__: list[str] = ["mcp_command"]
