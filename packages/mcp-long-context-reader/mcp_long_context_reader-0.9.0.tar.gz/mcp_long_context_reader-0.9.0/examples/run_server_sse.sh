export MCP_WORKSPACE_DIRECTORY="${HOME}/path/to/workspace"
export MCP_CACHE_DIRECTORY="${HOME}/path/to/cache"
export MCP_API_PROVIDER="dashscope"
export MCP_EMBEDDING_MODEL="text-embedding-v1"
export MCP_LLM_MODEL="qwen-max"
export DASHSCOPE_API_KEY="sk-your-api-key"

# This will run the server on "http://localhost:8000/sse"
uv run fastmcp run src/mcp_long_context_reader/server.py --transport sse --port 8000
