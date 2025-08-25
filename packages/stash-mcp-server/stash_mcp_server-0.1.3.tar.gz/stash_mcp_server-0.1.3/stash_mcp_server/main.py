import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    stash_api_base: str = Field(
        description="Base URL for the Stash API"
    )
    mcp_token: str = Field(
        default="",
        description="MCP authentication token"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()

def get_auth_headers(token: str) -> dict[str, str]:
    """Get authentication headers for Stash API requests."""
    if not token:
        raise ValueError("MCP token is not provided")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

async def make_stash_request(url: str, token: str) -> dict[str, Any] | None:
    """Make authenticated request to Stash API."""
    try:
        headers = get_auth_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error making Stash API request: {str(e)}")
        return None

def format_similar_issues(similar_issues: list) -> str:
    """Format similar issues into a readable string."""
    if not similar_issues:
        return "No similar issues found."
    
    output = []
    for item in similar_issues:
        issue = item["issue"]
        similarity = item["similarity"]
        output.append(f"""
• {issue.get('key', '<No key>')}: {issue.get('summary', '<No title>')}
  Description: {issue.get('description', '<No description>')}
  Similarity: {similarity:.2%}
  URL: {issue.get('url', '<No URL>')}""")
    
    return "\n".join(output)

def format_similar_documents(similar_documents: list) -> str:
    """Format similar documents into a readable string."""
    if not similar_documents:
        return "No similar documents found."
    
    output = []
    for item in similar_documents:
        doc = item["document"]
        chunks = item["chunks"]
        scores = item["similarity_scores"]
        context = f"""
{doc.get('title', '<No title>')}
{doc.get('url', '<No URL>')}
"""
        for i, chunk in enumerate(chunks):
            context += f"""
Chunk {i+1} with similarity {scores[i]:.2%}:
{chunk}
"""
        output.append(context)
    return "\n".join(output)

def format_similar_files(similar_files: list) -> str:
    """Format similar files into a readable string."""
    if not similar_files:
        return "No similar code files found."
    
    output = []
    for item in similar_files:
        file = item["file"]
        chunks = item["chunks"]
        output.append(f"\n• {file.get('path', '<No path>')}")
        
        for chunk in chunks:
            start, end = chunk["start_end_lines"]
            score = chunk["similarity_score"]
            url = chunk.get("url", "<No URL>")
            output.append(f"""
  Lines {start}-{end}
  Similarity: {score:.2%}
  URL: {url}""")
    
    return "\n".join(output)

def format_experts(experts: list) -> str:
    """Format experts into a readable string."""
    if not experts:
        return "No experts identified."
    
    output = []
    for expert in experts:
        user = expert["user"]
        score = expert["score"]
        availability = expert.get("availability", "Unknown")
        output.append(f"""
• {user.get('name', user.get('email', '<No name>'))}
  Availability: {availability}
  Expertise Score: {score:.2%}""")
    
    return "\n".join(output)

# Initialize the MCP server
app = Server("stash-mcp-server")

# Store token globally when server starts
_mcp_token: str = ""

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_my_tasks",
            description="List all tasks assigned to the authenticated user, grouped by categories",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_issue_analysis",
            description="Get detailed analysis for a specific issue including similar content and experts",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_slug": {
                        "type": "string",
                        "description": "The project's slug identifier"
                    },
                    "issue_id": {
                        "type": "string",
                        "description": "UUID of the issue"
                    }
                },
                "required": ["project_slug", "issue_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    # Get token from arguments or global storage
    token = arguments.get("token", _mcp_token)
    
    if name == "list_my_tasks":
        return await list_my_tasks(token)
    elif name == "get_issue_analysis":
        project_slug = arguments.get("project_slug")
        issue_id = arguments.get("issue_id")
        if not project_slug or not issue_id:
            return [TextContent(
                type="text",
                text="Error: Both project_slug and issue_id are required"
            )]
        return await get_issue_analysis(project_slug, issue_id, token)
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def list_my_tasks(token: str) -> list[TextContent]:
    """List all tasks assigned to the authenticated user, grouped by categories."""
    url = f"{settings.stash_api_base}/users/dashboard/"
    data = await make_stash_request(url, token)
    
    if not data:
        return [TextContent(
            type="text",
            text="Unable to fetch your assigned tasks. Please make sure your MCP token is set correctly."
        )]
    
    if not data.get("issues"):
        return [TextContent(
            type="text",
            text="You have no assigned tasks."
        )]
        
    output = []
    for group in data["issues"]:
        group_str = f"\n=== {group['title']} ===\n"
        
        if not group["issues"]:
            group_str += "No issues in this category\n"
        else:
            for issue in group["issues"]:
                issue_str = f"""
{issue.get('key', '<No key>')}: {issue.get('title', '<No title>')}
Issue ID: {issue.get('id', '<No ID>')}
Project Name: {issue.get('project', {}).get('name', '<Unknown>')}
Project Slug: {issue.get('project', {}).get('slug', '<Unknown>')}
"""
                group_str += issue_str
        
        output.append(group_str)
    
    return [TextContent(
        type="text",
        text="\n".join(output)
    )]

async def get_issue_analysis(project_slug: str, issue_id: str, token: str) -> list[TextContent]:
    """Get detailed analysis for a specific issue including similar content and experts."""
    url = f"{settings.stash_api_base}/projects/{project_slug}/issues/{issue_id}/analysis/"
    data = await make_stash_request(url, token)
    
    if not data:
        return [TextContent(
            type="text",
            text="Unable to fetch issue analysis. Please check your MCP token and the issue ID."
        )]
    
    sections = [
        ("Similar Issues", format_similar_issues(data.get("similar_issues", []))),
        ("Similar Documents", format_similar_documents(data.get("similar_documents", []))),
        ("Similar Code Files", format_similar_files(data.get("similar_files", []))),
        ("Knowledgeable Team Members", format_experts(data.get("experts", [])))
    ]
    
    output = []
    for title, content in sections:
        output.extend([f"\n=== {title} ===", content])
    
    return [TextContent(
        type="text",
        text="\n".join(output)
    )]

def main():
    """Main entry point for the MCP server."""
    import asyncio
    import sys
    
    async def run_server():
        global _mcp_token
        
        # Get token from environment variable (like Nia MCP)
        _mcp_token = os.getenv("STASH_MCP_TOKEN")
        
        # Fallback to command line argument if env var not set
        if not _mcp_token and len(sys.argv) > 1:
            _mcp_token = sys.argv[1]
        
        # For stdio server
        import mcp.server.stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
