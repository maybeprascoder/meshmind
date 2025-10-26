"""
Integration script to connect MCP server with the document chat system
This allows fetching content from Notion/Jira and processing it through your RAG pipeline
"""

import asyncio
import json
import requests
from typing import Dict, List, Optional
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
USER_ID = "mcp_user"

class MCPIntegration:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.user_id = USER_ID
    
    def upload_content_as_file(self, content: str, filename: str, source_type: str = "mcp") -> Optional[str]:
        """Upload content as a virtual file to the document processing system."""
        try:
            # Create a temporary file-like object
            import io
            file_content = io.BytesIO(content.encode('utf-8'))
            
            files = {"file": (filename, file_content, "text/plain")}
            headers = {"user-id": self.user_id}
            
            response = requests.post(
                f"{self.api_base_url}/upload",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                file_id = result["file_id"]
                
                # Add metadata about the source
                self._add_source_metadata(file_id, source_type, filename)
                
                return file_id
            else:
                print(f"Upload failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error uploading content: {e}")
            return None
    
    def _add_source_metadata(self, file_id: str, source_type: str, original_name: str):
        """Add metadata about the content source."""
        # This would typically update the file record in the database
        # For now, we'll just log it
        print(f"Added metadata: {file_id} from {source_type} ({original_name})")
    
    def wait_for_processing(self, file_id: str, timeout: int = 60) -> bool:
        """Wait for file processing to complete."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                response = requests.get(
                    f"{self.api_base_url}/file/{file_id}/status",
                    headers={"user-id": self.user_id}
                )
                
                if response.status_code == 200:
                    status = response.json().get("status")
                    
                    if status == "processed":
                        print(f"✅ File {file_id} processed successfully!")
                        return True
                    elif status == "failed":
                        print(f"❌ File {file_id} processing failed!")
                        return False
                    else:
                        print(f"⏳ File {file_id} status: {status}")
                
                asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error checking status: {e}")
                return False
        
        print(f"⏰ Timeout waiting for file {file_id} to process")
        return False
    
    def query_content(self, file_id: str, query: str, use_kg: bool = True) -> Optional[Dict]:
        """Query the processed content."""
        try:
            response = requests.post(
                f"{self.api_base_url}/query",
                headers={"user-id": self.user_id},
                json={
                    "query": query,
                    "file_id": file_id,
                    "session_id": "mcp_session",
                    "use_kg": use_kg
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Query failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error querying content: {e}")
            return None

class NotionIntegration(MCPIntegration):
    """Integration with Notion pages."""
    
    def __init__(self, notion_api_key: str):
        super().__init__()
        self.notion_api_key = notion_api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def fetch_and_process_page(self, page_id: str, query: str = None) -> Optional[Dict]:
        """Fetch a Notion page and process it through the RAG system."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Get page content
                page_response = await client.get(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers
                )
                page_response.raise_for_status()
                page_data = page_response.json()
                
                # Get page blocks
                blocks_response = await client.get(
                    f"{self.base_url}/blocks/{page_id}/children",
                    headers=self.headers
                )
                blocks_response.raise_for_status()
                blocks_data = blocks_response.json()
                
                # Extract text content
                text_content = self._extract_text_from_blocks(blocks_data.get("results", []))
                
                # Get page title
                page_title = self._get_page_title(page_data)
                
                # Upload to document system
                filename = f"notion_{page_title}_{page_id[:8]}.txt"
                file_id = self.upload_content_as_file(text_content, filename, "notion")
                
                if not file_id:
                    return None
                
                # Wait for processing
                if not self.wait_for_processing(file_id):
                    return None
                
                # Query if provided
                if query:
                    result = self.query_content(file_id, query)
                    return {
                        "file_id": file_id,
                        "page_title": page_title,
                        "content_preview": text_content[:200] + "...",
                        "query_result": result
                    }
                else:
                    return {
                        "file_id": file_id,
                        "page_title": page_title,
                        "content_preview": text_content[:200] + "...",
                        "status": "processed"
                    }
                
        except Exception as e:
            print(f"Error fetching Notion page: {e}")
            return None
    
    def _get_page_title(self, page_data: Dict) -> str:
        """Extract page title from Notion page data."""
        properties = page_data.get("properties", {})
        
        # Look for title property
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_content = prop_data.get("title", [])
                if title_content:
                    return "".join([item.get("plain_text", "") for item in title_content])
        
        return "Untitled Page"
    
    def _extract_text_from_blocks(self, blocks: List[Dict]) -> str:
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
            
            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                heading = block.get(block_type, {})
                rich_text = heading.get("rich_text", [])
                text = "".join([rt.get("plain_text", "") for rt in rich_text])
                if text.strip():
                    level = int(block_type.split("_")[1])
                    text_parts.append(f"{'#' * level} {text}")
            
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
        
        return "\n\n".join(text_parts)

class JiraIntegration(MCPIntegration):
    """Integration with Jira issues."""
    
    def __init__(self, jira_url: str, email: str, api_token: str):
        super().__init__()
        self.jira_url = jira_url.rstrip('/')
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
    
    async def fetch_and_process_issue(self, issue_key: str, query: str = None) -> Optional[Dict]:
        """Fetch a Jira issue and process it through the RAG system."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Get issue
                response = await client.get(
                    f"{self.jira_url}/rest/api/3/issue/{issue_key}",
                    headers=self.headers
                )
                response.raise_for_status()
                issue_data = response.json()
                
                # Extract text content
                text_content = self._extract_text_from_issue(issue_data)
                
                # Upload to document system
                filename = f"jira_{issue_key}.txt"
                file_id = self.upload_content_as_file(text_content, filename, "jira")
                
                if not file_id:
                    return None
                
                # Wait for processing
                if not self.wait_for_processing(file_id):
                    return None
                
                # Query if provided
                if query:
                    result = self.query_content(file_id, query)
                    return {
                        "file_id": file_id,
                        "issue_key": issue_key,
                        "content_preview": text_content[:200] + "...",
                        "query_result": result
                    }
                else:
                    return {
                        "file_id": file_id,
                        "issue_key": issue_key,
                        "content_preview": text_content[:200] + "...",
                        "status": "processed"
                    }
                
        except Exception as e:
            print(f"Error fetching Jira issue: {e}")
            return None
    
    def _extract_text_from_issue(self, issue: Dict) -> str:
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
        
        return "\n\n".join(text_parts)
    
    def _extract_text_from_atlassian_doc(self, doc: Dict) -> str:
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
        
        return "\n\n".join(text_parts)
    
    def _extract_text_from_content(self, content: List[Dict]) -> str:
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

# Example usage
async def main():
    """Example usage of the MCP integration."""
    
    # Notion integration example
    if os.getenv("NOTION_API_KEY"):
        print("🔗 Testing Notion integration...")
        notion = NotionIntegration(os.getenv("NOTION_API_KEY"))
        
        # Replace with your actual Notion page ID
        page_id = "your-notion-page-id"
        result = await notion.fetch_and_process_page(
            page_id, 
            "What is this page about?"
        )
        
        if result:
            print(f"✅ Notion page processed: {result['page_title']}")
            if result.get("query_result"):
                print(f"Answer: {result['query_result']['answer'][:200]}...")
    
    # Jira integration example
    if all([os.getenv("JIRA_URL"), os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")]):
        print("🔗 Testing Jira integration...")
        jira = JiraIntegration(
            os.getenv("JIRA_URL"),
            os.getenv("JIRA_EMAIL"),
            os.getenv("JIRA_API_TOKEN")
        )
        
        # Replace with your actual Jira issue key
        issue_key = "PROJ-123"
        result = await jira.fetch_and_process_issue(
            issue_key,
            "What is the status of this issue?"
        )
        
        if result:
            print(f"✅ Jira issue processed: {result['issue_key']}")
            if result.get("query_result"):
                print(f"Answer: {result['query_result']['answer'][:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
