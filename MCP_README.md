# MCP Server Integration for Notion & Jira

This MCP (Model Context Protocol) server allows you to fetch content from Notion pages and Jira issues and process them through your document chat system.

## 🚀 What This Enables

- **Notion Integration**: Fetch any Notion page and chat with its content
- **Jira Integration**: Fetch Jira issues and ask questions about them
- **Seamless Processing**: Content automatically goes through your RAG pipeline
- **Knowledge Graph**: Notion/Jira content gets the same entity extraction and knowledge graph treatment
- **Unified Chat**: Chat with external content using the same interface as uploaded documents

## 📋 Prerequisites

1. **Notion API Key** (for Notion integration)
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the API key
   - Share your pages with the integration

2. **Jira API Token** (for Jira integration)
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create a new API token
   - Note your Jira URL and email

3. **Running Document Chat System**
   - Your `simple_app.py` should be running on `http://localhost:8000`

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r mcp_requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example file
cp mcp.env.example .env

# Edit .env with your actual values
# NOTION_API_KEY=your_actual_notion_api_key
# JIRA_URL=https://your-domain.atlassian.net
# JIRA_EMAIL=your-email@example.com
# JIRA_API_TOKEN=your_actual_jira_token
```

### 3. Run the MCP Server
```bash
python mcp_server.py
```

## 🎯 Usage Examples

### Notion Integration

```python
from mcp_integration import NotionIntegration
import asyncio

async def fetch_notion_page():
    notion = NotionIntegration("your_notion_api_key")
    
    # Fetch and process a Notion page
    result = await notion.fetch_and_process_page(
        page_id="your-page-id",
        query="What is this page about?"
    )
    
    if result:
        print(f"Page: {result['page_title']}")
        print(f"Answer: {result['query_result']['answer']}")

asyncio.run(fetch_notion_page())
```

### Jira Integration

```python
from mcp_integration import JiraIntegration
import asyncio

async def fetch_jira_issue():
    jira = JiraIntegration(
        jira_url="https://your-domain.atlassian.net",
        email="your-email@example.com",
        api_token="your_api_token"
    )
    
    # Fetch and process a Jira issue
    result = await jira.fetch_and_process_issue(
        issue_key="PROJ-123",
        query="What is the current status of this issue?"
    )
    
    if result:
        print(f"Issue: {result['issue_key']}")
        print(f"Answer: {result['query_result']['answer']}")

asyncio.run(fetch_jira_issue())
```

## 🔧 MCP Tools Available

### Notion Tools
- `fetch_notion_page`: Get content from a specific Notion page
- `search_notion_pages`: Search for Notion pages (implementation needed)

### Jira Tools
- `fetch_jira_issue`: Get a specific Jira issue
- `search_jira_issues`: Search Jira issues using JQL

## 🔄 Integration Flow

1. **Fetch Content**: MCP server fetches content from Notion/Jira
2. **Extract Text**: Content is converted to plain text
3. **Upload to System**: Text is uploaded as a virtual file to your document chat system
4. **Process**: Content goes through chunking, embedding, and knowledge graph creation
5. **Query**: You can now chat with the external content using your existing interface

## 📁 File Structure

```
├── mcp_server.py          # Main MCP server implementation
├── mcp_integration.py     # Integration helpers for your system
├── mcp_requirements.txt  # MCP server dependencies
├── mcp.env.example       # Environment configuration template
└── README.md             # This file
```

## 🎨 Streamlit UI Integration

You can extend your Streamlit UI to include MCP integration:

```python
# Add to streamlit_app.py
if st.button("Fetch from Notion"):
    page_id = st.text_input("Notion Page ID")
    if page_id:
        # Use MCP integration to fetch and process
        result = await notion.fetch_and_process_page(page_id)
        if result:
            st.success(f"✅ Notion page processed: {result['page_title']}")
            st.session_state.current_file_id = result['file_id']
            st.rerun()

if st.button("Fetch from Jira"):
    issue_key = st.text_input("Jira Issue Key (e.g., PROJ-123)")
    if issue_key:
        # Use MCP integration to fetch and process
        result = await jira.fetch_and_process_issue(issue_key)
        if result:
            st.success(f"✅ Jira issue processed: {result['issue_key']}")
            st.session_state.current_file_id = result['file_id']
            st.rerun()
```

## 🔒 Security Notes

- **API Keys**: Keep your Notion API keys and Jira tokens secure
- **Permissions**: Only share necessary Notion pages with your integration
- **Rate Limits**: Be mindful of API rate limits for both Notion and Jira
- **Data Privacy**: Content is processed through your local system

## 🚀 Advanced Features

### Custom MCP Tools
You can extend the MCP server with additional tools:

```python
@server.list_tools()
async def list_tools() -> List[types.Tool]:
    tools = [
        # ... existing tools ...
        types.Tool(
            name="fetch_confluence_page",
            description="Fetch content from Confluence",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"}
                },
                "required": ["page_id"]
            }
        )
    ]
    return tools
```

### Batch Processing
Process multiple Notion pages or Jira issues at once:

```python
async def process_multiple_notion_pages(page_ids: List[str]):
    notion = NotionIntegration(api_key)
    results = []
    
    for page_id in page_ids:
        result = await notion.fetch_and_process_page(page_id)
        if result:
            results.append(result)
    
    return results
```

## 🐛 Troubleshooting

### Common Issues

1. **Notion API Errors**
   - Check if the page is shared with your integration
   - Verify your API key is correct
   - Check Notion API rate limits

2. **Jira API Errors**
   - Verify your Jira URL format
   - Check if your API token is valid
   - Ensure you have access to the issue

3. **Processing Failures**
   - Make sure your document chat system is running
   - Check if the content extraction worked properly
   - Verify the uploaded content isn't empty

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 Benefits

- **Unified Interface**: Chat with external content using your existing UI
- **Knowledge Graph**: External content gets the same intelligent processing
- **Source Citations**: See exactly which parts of Notion/Jira content were used
- **Scalable**: Easy to add more external services (Confluence, GitHub, etc.)
- **Flexible**: Works with any MCP-compatible AI system

This MCP integration transforms your document chat system into a powerful tool for working with external knowledge sources! 🚀
