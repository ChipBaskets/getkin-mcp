# GetKin MCP Server

Agent infrastructure that runs itself. One MCP server, six tools.

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `recommend_model` | Get the optimal LLM for any task across 17 models and 6 providers | Free |
| `check_availability` | Real-time availability and latency for LLM provider APIs | $0.005 USDC |
| `route_llm_call` | Route chat completions through GetKin's proxy (OpenAI-compatible) | 3% margin |
| `compress_memory` | Compress session dumps into structured 3-tier memory | First 5 free, then $0.03 USDC |
| `list_models` | List all available models with current pricing | Free |
| `check_memory_usage` | Check free tier compression usage for an agent | Free |

## Installation

Connect to the GetKin MCP server using any MCP-compatible client:
```json
{
  "mcpServers": {
    "getkin": {
      "url": "https://getkin-mcp.fly.dev/mcp"
    }
  }
}
```

## Usage

Once connected, your agent has access to all six tools. The `recommend_model` tool is free and requires no payment — use it to find the cheapest or fastest model for any task.

Paid tools use x402 payments via Solana USDC. The `compress_memory` tool includes 5 free compressions per agent.

## Providers Monitored

Anthropic, OpenAI, Google, Mistral, DeepSeek, Meta (via Together AI)

## Links

- **Portal:** https://getkin.io
- **MCP Endpoint:** https://getkin-mcp.fly.dev/mcp
- **Smithery:** https://smithery.ai/server/getkin/agent-infrastructure

## License

MIT
