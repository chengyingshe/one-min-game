"""PyGame Game Studio MCP Server.

Provides 22 tools for AI-powered game development:
check_environment, create_project, list_templates, scaffold_template,
apply_game_spec, create_game, write_game_file, read_game_file,
build_game, run_game, validate_gameplay, capture_frame,
capture_screenshot, tune_balance, list_sdk_api, generate_readme,
upload_to_playground, list_playground_games, get_playground_game,
download_from_playground, delete_playground_game, add_llm_to_game.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# -- Tool handlers -----------------------------------------------------------
from pygame_studio_mcp.tools.check_environment import check_environment
from pygame_studio_mcp.tools.create_project import create_project
from pygame_studio_mcp.tools.list_templates import list_templates
from pygame_studio_mcp.tools.scaffold_template import scaffold_template
from pygame_studio_mcp.tools.apply_game_spec import apply_game_spec
from pygame_studio_mcp.tools.create_game import create_game
from pygame_studio_mcp.tools.write_game_file import write_game_file
from pygame_studio_mcp.tools.read_game_file import read_game_file
from pygame_studio_mcp.tools.build_game import build_game
from pygame_studio_mcp.tools.run_game import run_game
from pygame_studio_mcp.tools.validate_gameplay import validate_gameplay
from pygame_studio_mcp.tools.capture_frame import capture_frame
from pygame_studio_mcp.tools.capture_screenshot import capture_screenshot
from pygame_studio_mcp.tools.tune_balance import tune_balance_tool
from pygame_studio_mcp.tools.list_sdk_api import list_sdk_api
from pygame_studio_mcp.tools.generate_readme import generate_readme
from pygame_studio_mcp.tools.upload_to_playground import upload_to_playground
from pygame_studio_mcp.tools.list_playground_games import list_playground_games
from pygame_studio_mcp.tools.get_playground_game import get_playground_game
from pygame_studio_mcp.tools.download_from_playground import download_from_playground
from pygame_studio_mcp.tools.delete_playground_game import delete_playground_game
from pygame_studio_mcp.tools.add_llm_to_game import add_llm_to_game

app = Server("pygame-game-studio")


def _json_result(data: Any) -> list[TextContent]:
    """Wrap structured data as MCP TextContent."""
    return [TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]


# -- Tool definitions --------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="check_environment",
            description="Check if the development environment meets all requirements (Python 3.11+, PyGame, PyYAML, MCP). Optionally auto-fix issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Automatically fix issues when possible (default: false)",
                    },
                },
            },
        ),
        Tool(
            name="create_project",
            description="Create a new game project directory under generated-games/",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="list_templates",
            description="List available game templates",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="scaffold_template",
            description="Copy template files into a project directory",
            inputSchema={
                "type": "object",
                "required": ["template", "project"],
                "properties": {
                    "template": {"type": "string", "description": "Template name"},
                    "project": {"type": "string", "description": "Target project name"},
                },
            },
        ),
        Tool(
            name="apply_game_spec",
            description="Merge a game spec into a project's config.yaml",
            inputSchema={
                "type": "object",
                "required": ["project", "spec"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "spec": {
                        "type": "object",
                        "description": "Game spec object with name, genre, screen, player, enemy, etc.",
                    },
                },
            },
        ),
        Tool(
            name="create_game",
            description="Create a blank PyGame game project with standard file structure and compilable skeleton code",
            inputSchema={
                "type": "object",
                "required": ["name", "description"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Game name, lowercase hyphenated",
                    },
                    "description": {
                        "type": "string",
                        "description": "One-line game description",
                    },
                },
            },
        ),
        Tool(
            name="write_game_file",
            description="Write or overwrite a file in a game project. Use this to generate game source code.",
            inputSchema={
                "type": "object",
                "required": ["project", "filename", "content"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "filename": {
                        "type": "string",
                        "description": "File name (e.g., main.py, model.py, config.yaml)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete file content to write",
                    },
                },
            },
        ),
        Tool(
            name="read_game_file",
            description="Read a file from a game project. Use this to debug compilation errors.",
            inputSchema={
                "type": "object",
                "required": ["project", "filename"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "filename": {"type": "string", "description": "File name to read"},
                },
            },
        ),
        Tool(
            name="build_game",
            description="Build a Python game project (syntax-check all .py files + install requirements)",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="run_game",
            description="Run a Python game with SDL_VIDEODRIVER=dummy for headless testing",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "duration": {
                        "type": "number",
                        "description": "Max run duration in seconds (default 60)",
                    },
                },
            },
        ),
        Tool(
            name="validate_gameplay",
            description="Validate a game runs without crashing (3-second headless test)",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="capture_frame",
            description="Capture a frame of game output (short run stdout)",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="capture_screenshot",
            description="Capture a PNG screenshot from a PyGame project (headless surface save)",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="tune_balance",
            description="Adjust game difficulty parameters based on natural-language feedback",
            inputSchema={
                "type": "object",
                "required": ["project", "feedback"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "feedback": {
                        "type": "string",
                        "description": "Natural language feedback about difficulty (e.g., 'too hard', 'too easy')",
                    },
                },
            },
        ),
        Tool(
            name="list_sdk_api",
            description="Get the full PyGame SDK API surface: all types, functions, constants available for game development",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_readme",
            description="Generate a detailed README.md documentation for a game project",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                },
            },
        ),
        Tool(
            name="upload_to_playground",
            description="Package a local game project as ZIP and upload it to the Playground web platform for sharing",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Local project name to upload"},
                    "display_name": {"type": "string", "description": "Display name on Playground (defaults to project name)"},
                    "description": {"type": "string", "description": "Game description for Playground listing"},
                    "author_name": {"type": "string", "description": "Author name to credit"},
                },
            },
        ),
        Tool(
            name="list_playground_games",
            description="List games available on the Playground web platform with optional filtering and sorting",
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {"type": "string", "description": "Filter by genre (flappy, shooter, rogue, fps, topdown, platformer)"},
                    "search": {"type": "string", "description": "Search in game names and descriptions"},
                    "sort": {"type": "string", "description": "Sort field: play_count, avg_rating, created_at, or name"},
                    "order": {"type": "string", "description": "Sort order: asc or desc"},
                    "limit": {"type": "integer", "description": "Max results (1-200, default 50)"},
                    "offset": {"type": "integer", "description": "Pagination offset"},
                },
            },
        ),
        Tool(
            name="get_playground_game",
            description="Get detailed information about a specific game on the Playground web platform",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Game name on Playground"},
                },
            },
        ),
        Tool(
            name="download_from_playground",
            description="Download a game from the Playground web platform and extract it as a local project",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Game name on Playground to download"},
                    "project": {"type": "string", "description": "Local project name (defaults to the Playground game name)"},
                },
            },
        ),
        Tool(
            name="delete_playground_game",
            description="Delete a game from the Playground web platform",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Game name to delete from Playground"},
                },
            },
        ),
        Tool(
            name="add_llm_to_game",
            description="Test the LLM API endpoint and return integration instructions for adding AI features (NPC dialogue, procedural content, dynamic storytelling) to a game project. Call this when the game needs AI capabilities.",
            inputSchema={
                "type": "object",
                "required": ["project"],
                "properties": {
                    "project": {"type": "string", "description": "Game project name"},
                    "test_prompt": {"type": "string", "description": "Test prompt to verify LLM API (default: 'Say hello in one sentence.')"},
                    "system_prompt": {"type": "string", "description": "Optional system prompt to test with"},
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls to their handlers."""
    try:
        if name == "check_environment":
            result = await check_environment(auto_fix=arguments.get("auto_fix", False))
        elif name == "create_project":
            result = await create_project(name=arguments["name"])
        elif name == "list_templates":
            result = await list_templates()
        elif name == "scaffold_template":
            result = await scaffold_template(
                template=arguments["template"],
                project=arguments["project"],
            )
        elif name == "apply_game_spec":
            result = await apply_game_spec(
                project=arguments["project"],
                spec=arguments["spec"],
            )
        elif name == "create_game":
            result = await create_game(
                name=arguments["name"],
                description=arguments["description"],
            )
        elif name == "write_game_file":
            result = await write_game_file(
                project=arguments["project"],
                filename=arguments["filename"],
                content=arguments["content"],
            )
        elif name == "read_game_file":
            result = await read_game_file(
                project=arguments["project"],
                filename=arguments["filename"],
            )
        elif name == "build_game":
            result = await build_game(project=arguments["project"])
        elif name == "run_game":
            result = await run_game(
                project=arguments["project"],
                duration=arguments.get("duration"),
            )
        elif name == "validate_gameplay":
            result = await validate_gameplay(project=arguments["project"])
        elif name == "capture_frame":
            result = await capture_frame(project=arguments["project"])
        elif name == "capture_screenshot":
            result = await capture_screenshot(project=arguments["project"])
        elif name == "tune_balance":
            result = await tune_balance_tool(
                project=arguments["project"],
                feedback=arguments["feedback"],
            )
        elif name == "list_sdk_api":
            result = await list_sdk_api()
        elif name == "generate_readme":
            result = await generate_readme(project=arguments["project"])
        elif name == "upload_to_playground":
            result = await upload_to_playground(
                project=arguments["project"],
                display_name=arguments.get("display_name"),
                description=arguments.get("description"),
                author_name=arguments.get("author_name"),
            )
        elif name == "list_playground_games":
            result = await list_playground_games(
                genre=arguments.get("genre"),
                search=arguments.get("search"),
                sort=arguments.get("sort"),
                order=arguments.get("order"),
                limit=arguments.get("limit"),
                offset=arguments.get("offset"),
            )
        elif name == "get_playground_game":
            result = await get_playground_game(name=arguments["name"])
        elif name == "download_from_playground":
            result = await download_from_playground(
                name=arguments["name"],
                project=arguments.get("project"),
            )
        elif name == "delete_playground_game":
            result = await delete_playground_game(name=arguments["name"])
        elif name == "add_llm_to_game":
            result = await add_llm_to_game(
                project=arguments["project"],
                test_prompt=arguments.get("test_prompt"),
                system_prompt=arguments.get("system_prompt"),
            )
        else:
            return _json_result({"error": f"Unknown tool: {name}"})

        return _json_result(result)

    except Exception as exc:
        return _json_result({"error": f"Tool '{name}' failed: {exc}"})


async def main() -> None:
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
