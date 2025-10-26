"""
MCP Server for Notion and Jira Integration
This server provides tools to fetch content from Notion pages and Jira issues
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from mcp import Server, types
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("notion-jira-mcp")

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

class NotionClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Fetch content from a Notion page."""
        async with httpx.AsyncClient() as client:
            try:
                # Get page properties
                page_response = await client.get(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers
                )
                page_response.raise_for_status()
                page_data = page_response.json()
                
                # Get page blocks/content
                blocks_response = await client.get(
                    f"{self.base_url}/blocks/{page_id}/children",
                    headers=self.headers
                )
                blocks_response.raise_for_status()
                blocks_data = blocks_response.json()
                
                return {
                    "page": page_data,
                    "blocks": blocks_data.get("results", [])
                }
            except httpx.HTTPError as e:
                logger.error(f"Notion API error: {e}")
                raise
    
    def extract_text_from_blocks(self, blocks: List[Dict]) -> str:
        """Extract plain text from Notion blocks."""
        text_parts = []
        
        for block in blocks:
            block_type = block.get("type")
            
            if block_type == "paragraph":
                paragraph = block.get("paragraph", {})
                rich_text = paragraph.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(text)
            
            elif block_type == "heading_1":
                heading = block.get("heading_1", {})
                rich_text = heading.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(f"# {text}")
            
            elif block_type == "heading_2":
                heading = block.get("heading_2", {})
                rich_text = heading.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(f"## {text}")
            
            elif block_type == "heading_3":
                heading = block.get("heading_3", {})
                rich_text = heading.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(f"### {text}")
            
            elif block_type == "bulleted_list_item":
                item = block.get("bulleted_list_item", {})
                rich_text = item.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(f"• {text}")
            
            elif block_type == "numbered_list_item":
                item = block.get("numbered_list_item", {})
                rich_text = item.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    text_parts.append(f"1. {text}")
            
            elif block_type == "code":
                code = block.get("code", {})
                rich_text = code.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    language = code.get("language", "")
                    text_parts.append(f"```{language}\n{text}\n```")
            
            # Handle child blocks recursively
            if block.get("has_children"):
                children = block.get("children", [])
                child_text = self.extract_text_from_blocks(children)
                if child_text.strip():
                    text_parts.append(child_text)
        
        return "\n\n".join(text_parts)

class JiraClient:
    def __init__(self, url: str, email: str, api_token: str):
        self.url = url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Basic {self._encode_auth()}",
            "Content-Type": "application/json"
        }
    
    def _encode_auth(self) -> str:
        """Encode email and API token for basic auth."""
        import base64
        auth_string = f"{self.email}:{self.api_token}"
        return base64.b64encode(auth_string.encode()).decode()
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Fetch a Jira issue."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.url}/rest/api/3/issue/{issue_key}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Jira API error: {e}")
                raise
    
    async def search_issues(self, jql: str, max_results: int = 50) -> Dict[str, Any]:
        """Search Jira issues using JQL."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "jql": jql,
                    "maxResults": max_results,
                    "fields": ["summary", "description", "status", "assignee", "created", "updated"]
                }
                response = await client.post(
                    f"{self.url}/rest/api/3/search",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Jira API error: {e}")
                raise
    
    def extract_text_from_issue(self, issue: Dict[str, Any]) -> str:
        """Extract plain text from a Jira issue."""
        fields = issue.get("fields", {})
        
        text_parts = []
        
        # Issue key and summary
        key = issue.get("key", "")
        summary = fields.get("summary", "")
        if summary:
            text_parts.append(f"**{key}: {summary}**")
        
        # Description
        description = fields.get("description", {})
        if description:
            desc_text = self._extract_text_from_atlassian_doc(description)
            if desc_text.strip():
                text_parts.append(f"Description:\n{desc_text}")
        
        # Status and assignee
        status = fields.get("status", {}).get("name", "")
        assignee = fields.get("assignee", {})
        assignee_name = assignee.get("displayName", "") if assignee else "Unassigned"
        
        if status or assignee_name:
            text_parts.append(f"Status: {status} | Assignee: {assignee_name}")
        
        # Dates
        created = fields.get("created", "")
        updated = fields.get("updated", "")
        if created:
            text_parts.append(f"Created: {created}")
        if updated:
            text_parts.append(f"Updated: {updated}")
        
        return "\n\n".join(text_parts)
    
    def _extract_text_from_atlassian_doc(self, doc: Dict[str, Any]) -> str:
        """Extract text from Atlassian Document Format (ADF)."""
        if not isinstance(doc, dict):
            return str(doc)
        
        content = doc.get("content", [])
        if not content:
            return ""
        
        text_parts = []
        
        for item in content:
            item_type = item.get("type", "")
            
            if item_type == "paragraph":
                paragraph_text = self._extract_text_from_content(item.get("content", []))
                if paragraph_text.strip():
                    text_parts.append(paragraph_text)
            
            elif item_type == "heading":
                level = item.get("attrs", {}).get("level", 1)
                heading_text = self._extract_text_from_content(item.get("content", []))
                if heading_text.strip():
                    text_parts.append(f"{'#' * level} {heading_text}")
            
            elif item_type == "bulletList":
                list_items = item.get("content", [])
                for list_item in list_items:
                    item_content = list_item.get("content", [])
                    for para in item_content:
                        if para.get("type") == "paragraph":
                            para_text = self._extract_text_from_content(para.get("content", []))
                            if para_text.strip():
                                text_parts.append(f"• {para_text}")
            
            elif item_type == "orderedList":
                list_items = item.get("content", [])
                for i, list_item in enumerate(list_items, 1):
                    item_content = list_item.get("content", [])
                    for para in item_content:
                        if para.get("type") == "paragraph":
                            para_text = self._extract_text_from_content(para.get("content", []))
                            if para_text.strip():
                                text_parts.append(f"{i}. {para_text}")
        
        return "\n\n".join(text_parts)
    
    def _extract_text_from_content(self, content: List[Dict[str, Any]]) -> str:
        """Extract text from ADF content array."""
        text_parts = []
        
        for item in content:
            item_type = item.get("type", "")
            
            if item_type == "text":
                text_parts.append(item.get("text", ""))
            elif item_type == "hardBreak":
                text_parts.append("\n")
            elif item_type == "code":
                text_parts.append(f"`{item.get('text', '')}`")
            elif item_type == "strong":
                strong_text = self._extract_text_from_content(item.get("content", []))
                text_parts.append(f"**{strong_text}**")
            elif item_type == "em":
                em_text = self._extract_text_from_content(item.get("content", []))
                text_parts.append(f"*{em_text}*")
        
        return "".join(text_parts)

# Initialize clients
notion_client = None
jira_client = None

if NOTION_API_KEY:
    notion_client = NotionClient(NOTION_API_KEY)
    logger.info("Notion client initialized")

if JIRA_URL and JIRA_EMAIL and JIRA_API_TOKEN:
    jira_client = JiraClient(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    logger.info("Jira client initialized")

# MCP Tools
@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MCP tools."""
    tools = []
    
    if notion_client:
        tools.extend([
            types.Tool(
                name="fetch_notion_page",
                description="Fetch content from a Notion page by page ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The Notion page ID to fetch"
                        }
                    },
                    "required": ["page_id"]
                }
            ),
            types.Tool(
                name="search_notion_pages",
                description="Search for Notion pages by query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Notion pages"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            )
        ])
    
    if jira_client:
        tools.extend([
            types.Tool(
                name="fetch_jira_issue",
                description="Fetch a Jira issue by issue key",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The Jira issue key (e.g., PROJ-123)"
                        }
                    },
                    "required": ["issue_key"]
                }
            ),
            types.Tool(
                name="search_jira_issues",
                description="Search Jira issues using JQL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "jql": {
                            "type": "string",
                            "description": "JQL query to search for issues"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    },
                    "required": ["jql"]
                }
            )
        ])
    
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    
    if name == "fetch_notion_page" and notion_client:
        page_id = arguments.get("page_id")
        try:
            content = await notion_client.get_page_content(page_id)
            text_content = notion_client.extract_text_from_blocks(content["blocks"])
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Notion Page Content:\n\n{text_content}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error fetching Notion page: {str(e)}"
                )
            ]
    
    elif name == "search_notion_pages" and notion_client:
        query = arguments.get("query")
        max_results = arguments.get("max_results", 10)
        
        # Note: Notion doesn't have a direct search API in the same way
        # This would need to be implemented based on your specific use case
        return [
            types.TextContent(
                type="text",
                text=f"Notion search for '{query}' (max {max_results} results) - Implementation needed"
            )
        ]
    
    elif name == "fetch_jira_issue" and jira_client:
        issue_key = arguments.get("issue_key")
        try:
            issue = await jira_client.get_issue(issue_key)
            text_content = jira_client.extract_text_from_issue(issue)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Jira Issue Content:\n\n{text_content}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error fetching Jira issue: {str(e)}"
                )
            ]
    
    elif name == "search_jira_issues" and jira_client:
        jql = arguments.get("jql")
        max_results = arguments.get("max_results", 50)
        
        try:
            results = await jira_client.search_issues(jql, max_results)
            issues = results.get("issues", [])
            
            text_parts = [f"Found {len(issues)} Jira issues:"]
            
            for issue in issues:
                issue_text = jira_client.extract_text_from_issue(issue)
                text_parts.append(f"\n---\n{issue_text}")
            
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(text_parts)
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error searching Jira issues: {str(e)}"
                )
            ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )
        ]

# Server initialization
@server.list_resources()
async def list_resources() -> List[types.Resource]:
    """List available resources."""
    return []

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    return f"Resource not found: {uri}"

async def main():
    """Run the MCP server."""
    # Import here to avoid issues if mcp is not installed
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="notion-jira-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
