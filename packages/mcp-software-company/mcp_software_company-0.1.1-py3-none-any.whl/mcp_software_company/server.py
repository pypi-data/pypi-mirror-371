import asyncio
import os
import logging
from pathlib import Path
# import agentops
from typing import Annotated
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    TextContent,
    Tool,
    INVALID_PARAMS,
)
from metagpt.config2 import config
from metagpt.const import CONFIG_ROOT
from metagpt.utils.project_repo import ProjectRepo
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecuteMetaGPTParams(BaseModel):
    """Parameters for executing MetaGPT project generation."""
    idea: Annotated[str, Field(description="Your innovative idea, such as 'Create a 2048 game'")]
    investment: Annotated[float, Field(default=3.0, description="Dollar amount to invest in the AI company")]
    n_round: Annotated[int, Field(default=5, description="Number of rounds for the simulation")]
    code_review: Annotated[bool, Field(default=True, description="Whether to use code review")]
    run_tests: Annotated[bool, Field(default=False, description="Whether to enable QA for adding & running tests")]
    implement: Annotated[bool, Field(default=True, description="Enable or disable code implementation")]
    project_name: Annotated[str, Field(default="", description="Unique project name, such as 'game_2048'")]
    inc: Annotated[bool, Field(default=False, description="Incremental mode for existing repo cooperation")]
    project_path: Annotated[str, Field(default="", description="Directory path for incremental project")]
    reqa_file: Annotated[str, Field(default="", description="Source file for rewriting QA code")]
    max_auto_summarize_code: Annotated[int, Field(default=0, description="Max auto summarize iterations (-1 for unlimited)")]
    recover_path: Annotated[str | None, Field(default=None, description="Path to recover project from serialized storage")]


async def generate_project(
    idea: str,
    investment: float = 3.0,
    n_round: int = 5,
    code_review: bool = True,
    run_tests: bool = False,
    implement: bool = True,
    project_name: str = "",
    inc: bool = False,
    project_path: str = "",
    reqa_file: str = "",
    max_auto_summarize_code: int = 0,
    recover_path: str | None = None
) -> str:
    """Generate a software project using MetaGPT with all original parameters"""
    try:
        # Update config if project path exists
        if project_path:
            config.update_via_cli(project_path, project_name, inc, reqa_file, max_auto_summarize_code)

        # Initialize team based on recover path
        if recover_path:
            stg_path = Path(recover_path)
            if not stg_path.exists() or not str(stg_path).endswith("team"):
                raise FileNotFoundError(f"{recover_path} not exists or not endswith `team`")
            company = Team.deserialize(stg_path=stg_path)
        else:
            company = Team()

            # Base team members
            team = [
                ProductManager(),
                Architect(),
                ProjectManager(),
            ]

            # Add Engineer if implementation or code review is needed
            if implement or code_review:
                team.append(Engineer(n_borg=5, use_code_review=code_review))

            # Add QA Engineer if tests are enabled
            if run_tests:
                team.append(QaEngineer())
                if n_round < 8:
                    n_round = 8  # Minimum rounds needed for QA

            company.hire(team)

        company.invest(investment)
        company.run_project(idea)
        await company.run(n_round=n_round)

        return "Project generation completed successfully"
    except Exception as e:
        logger.error(f"Project generation failed: {str(e)}")
        return f"Error: {str(e)}"


async def serve() -> None:
    """Run the metagpt MCP server."""
    server = Server("metagpt_executor")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="execute_metagpt",
                description="Executes MetaGPT project generation with full parameter support",
                inputSchema=ExecuteMetaGPTParams.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name != "execute_metagpt":
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Tool {name} not found"))

        try:
            args = ExecuteMetaGPTParams(**arguments)
        except ValueError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        result = await generate_project(
            idea=args.idea,
            investment=args.investment,
            n_round=args.n_round,
            code_review=args.code_review,
            run_tests=args.run_tests,
            implement=args.implement,
            project_name=args.project_name,
            inc=args.inc,
            project_path=args.project_path,
            reqa_file=args.reqa_file,
            max_auto_summarize_code=args.max_auto_summarize_code,
            recover_path=args.recover_path,
        )
        return [TextContent(type="text", text=result)]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    # Uncomment the following line to run as an MCP server
    asyncio.run(serve())

    # # For direct testing, similar to the FastMCP version
    #asyncio.run(generate_project("Create a simple calculator app", investment=3.0, n_round=5, code_review=True, run_tests=False, implement=True, project_name="calculator_app"))
