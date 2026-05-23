"""MCP server implementation for GitHub PR review workflows."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from app.config import get_settings, setup_logging
from app.github_client import GitHubClient
from app.models import DiffResponse, ReviewSuggestions
from app.release_notes_generator import generate_release_notes
from app.risk_analyzer import analyze_file_changes, generate_summary

logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("repo-assistant-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_pull_request",
            description="Fetch complete pull request information including title, description, author, state, labels, changed files count, additions/deletions, reviewers, and PR URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                },
                "required": ["owner", "repo", "pull_number"],
            },
        ),
        Tool(
            name="list_changed_files",
            description="List all files modified in a pull request with their status, additions, deletions, and patch snippets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                },
                "required": ["owner", "repo", "pull_number"],
            },
        ),
        Tool(
            name="get_diff",
            description="Get the complete unified diff for a pull request, grouped by file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                },
                "required": ["owner", "repo", "pull_number"],
            },
        ),
        Tool(
            name="suggest_review_comments",
            description="Analyze PR changes and generate AI review suggestions. Identifies risky files, large changes, missing tests, and code smells.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                },
                "required": ["owner", "repo", "pull_number"],
            },
        ),
        Tool(
            name="post_review_comment",
            description="Post a review comment to a GitHub pull request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                    "body": {
                        "type": "string",
                        "description": "Comment body (markdown supported)",
                    },
                    "commit_id": {
                        "type": "string",
                        "description": "Optional commit SHA for line-specific comments",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional file path for line-specific comments",
                    },
                    "line": {
                        "type": "integer",
                        "description": "Optional line number for line-specific comments",
                    },
                },
                "required": ["owner", "repo", "pull_number", "body"],
            },
        ),
        Tool(
            name="generate_release_notes",
            description="Generate release notes from commits between two branches. Categorizes changes into features, fixes, refactors, documentation, and breaking changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (username or organization)",
                    },
                    "repo": {"type": "string", "description": "Repository name"},
                    "base_branch": {
                        "type": "string",
                        "description": "Base branch (e.g., 'main')",
                    },
                    "head_branch": {
                        "type": "string",
                        "description": "Head branch (e.g., 'develop')",
                    },
                    "version": {
                        "type": "string",
                        "description": "Version number for the release (e.g., '1.0.0')",
                    },
                },
                "required": ["owner", "repo", "base_branch", "head_branch", "version"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        client = GitHubClient()

        if name == "get_pull_request":
            pr_info = client.get_pull_request(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )
            result = json.dumps(pr_info.model_dump(mode="json"), indent=2, default=str)

        elif name == "list_changed_files":
            files = client.list_changed_files(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )
            result = json.dumps(
                [f.model_dump(mode="json") for f in files],
                indent=2,
                default=str,
            )

        elif name == "get_diff":
            diff_text = client.get_diff(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )
            pr_info = client.get_pull_request(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )
            files = client.list_changed_files(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )

            total_additions = sum(f.additions for f in files)
            total_deletions = sum(f.deletions for f in files)

            response = DiffResponse(
                pr_number=arguments["pull_number"],
                total_files=len(files),
                total_additions=total_additions,
                total_deletions=total_deletions,
                diff_text=diff_text,
            )
            result = json.dumps(response.model_dump(mode="json"), indent=2, default=str)

        elif name == "suggest_review_comments":
            pr_info = client.get_pull_request(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )
            files = client.list_changed_files(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
            )

            suggestions, risk_score = analyze_file_changes(files)
            summary = generate_summary(suggestions, risk_score)

            review_suggestions = ReviewSuggestions(
                pr_title=pr_info.title,
                pr_url=pr_info.pr_url,
                risk_score=risk_score,
                suggestions=suggestions,
                summary=summary,
            )
            result = json.dumps(review_suggestions.model_dump(mode="json"), indent=2, default=str)

        elif name == "post_review_comment":
            result_dict = client.post_review_comment(
                arguments["owner"],
                arguments["repo"],
                arguments["pull_number"],
                arguments["body"],
                commit_id=arguments.get("commit_id"),
                path=arguments.get("path"),
                line=arguments.get("line"),
            )
            result = json.dumps(result_dict, indent=2, default=str)

        elif name == "generate_release_notes":
            commits = client.get_commits_since(
                arguments["owner"],
                arguments["repo"],
                arguments["base_branch"],
                arguments["head_branch"],
            )

            # Extract contributors
            contributors = list(set(c["author"] for c in commits))

            release_notes = generate_release_notes(
                arguments["version"],
                commits,
                contributors,
            )
            result = json.dumps(release_notes.model_dump(mode="json"), indent=2, default=str)

        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})

        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        error_result = json.dumps({"error": f"Error: {str(e)}"})
        return [TextContent(type="text", text=error_result)]
    finally:
        client.close()


async def main() -> None:
    """Run the MCP server."""
    import sys
    import os
    import anyio
    from mcp.server.stdio import stdio_server

    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting repo-assistant-mcp server")
    logger.info(f"Environment: {settings.app_env}")

    # Check if running in dev mode (when stdin is not a pipe)
    dev_mode = os.environ.get("DEV_MODE", "").lower() == "true"
    
    if dev_mode or (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        logger.warning("Running in development mode (stdio not piped)")
        logger.info("This server is designed to run as an MCP server via stdio.")
        logger.info("To use it properly, configure it in your MCP client config.")
        logger.info("For testing, use: DEV_MODE=true python main.py")
        
        # Keep the process alive for testing
        try:
            while True:
                await anyio.sleep(1)
        except (KeyboardInterrupt, EOFError):
            logger.info("Server stopped.")
    else:
        try:
            async with stdio_server(server) as (read_stream, write_stream):
                logger.info("Server running. Press Ctrl+C to exit.")
                await server.run(read_stream, write_stream, None)
        except (KeyboardInterrupt, EOFError):
            logger.info("Server stopped.")
        except BaseException as e:
            if "unhandled errors in a TaskGroup" in str(e):
                logger.info("Server stopped.")
            else:
                logger.error(f"Server error: {e}", exc_info=True)
                raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
