from typing import Annotated, Dict

from mcp import ServerSession, SamplingMessage
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from pydantic import Field, BaseModel
from mcp_demo.views import dialogue


def create_server() -> FastMCP:
    mcp_server = FastMCP(name="hw-mcp-demo")

    @mcp_server.tool(
        title="Ask Human",
        description="Ask human for certain information. Especially when you don't know what you are going to do next"
    )
    def ask_human(
            query: Annotated[str, Field(description="The question to ask the human user")],
    ) -> str:
        return dialogue(query)

    @mcp_server.tool(
        title="Ask Expert",
        description="Ask expert for specific knowledge. Especially when you don't know how to achieve the target"
    )
    async def ask_expert(
            query: Annotated[str, Field(description="The question to ask the expert")],
            ctx: Context[ServerSession, None]
    ) -> str:
        result = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=query),
                )
            ],
            max_tokens=1024,
        )
        if result.content.type == "text":
            return result.content.text
        return str(result.content)

    @mcp_server.tool(
        title="Run Task",
        description="Run a task"
    )
    async def run_task(
            task_name: Annotated[str, Field(description="The name of the task to run")],
            ctx: Context[ServerSession, None]
    ) -> str:
        await ctx.info(f"Starting: {task_name}")
        for i in range(3):
            await ctx.info(f"Completed step {i + 1}")
        return f"Task '{task_name}' completed"

    return mcp_server


def main():
    print("Starting MCP server...")
    mcp = create_server()
    mcp.run()
