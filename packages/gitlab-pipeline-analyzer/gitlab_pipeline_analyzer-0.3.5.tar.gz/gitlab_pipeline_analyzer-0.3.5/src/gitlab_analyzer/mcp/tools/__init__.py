"""
MCP tools package for GitLab Pipeline Analyzer

Copyright (c) 2025 Siarhei Skuratovich
Licensed under the MIT License - see LICENSE file for details
"""

from fastmcp import FastMCP

from .analysis_tools import register_analysis_tools
from .info_tools import register_info_tools
from .log_tools import register_log_tools
from .pagination_tools import register_pagination_tools
from .pytest_tools import register_pytest_tools
from .search_tools import register_search_tools
from .utils import get_gitlab_analyzer


def register_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the FastMCP instance"""
    register_analysis_tools(mcp)
    register_info_tools(mcp)
    register_log_tools(mcp)
    register_pagination_tools(mcp)
    register_pytest_tools(mcp)
    register_search_tools(mcp)


__all__ = [
    "register_tools",
    "register_analysis_tools",
    "register_info_tools",
    "register_log_tools",
    "register_pagination_tools",
    "register_pytest_tools",
    "register_search_tools",
    "get_gitlab_analyzer",
]
