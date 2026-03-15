"""
GetKin MCP Gateway
====================
A proper MCP server exposing all GetKin services as tools.
One entry point for agents, one listing on directories, four services behind it.
"""

import os
import json
from typing import Annotated, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

# ---------------------------------------------------------------------------
# Service URLs
# ---------------------------------------------------------------------------
ORACLE_URL = os.getenv("ORACLE_URL", "https://getkin-api.fly.dev")
MONITOR_URL = os.getenv("MONITOR_URL", "https://getkin-monitor.fly.dev")
PROXY_URL = os.getenv("PROXY_URL", "https://getkin-proxy.fly.dev")
MEMORY_URL = os.getenv("MEMORY_URL", "https://getkin-memory.fly.dev")

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="GetKin",
    instructions=(
        "GetKin provides agent infrastructure services: model recommendations, "
        "availability monitoring, LLM routing, and memory compression. "
        "All services are agent-native and built for autonomous operation. "
        "The recommend_model and list_models tools are FREE. Other tools "
        "accept x402 payments via Solana USDC."
    ),
    description=(
        "Agent infrastructure that runs itself. Six tools for autonomous agents: "
        "free LLM model recommendations across 17 models and 6 providers, "
        "real-time provider availability monitoring, LLM routing proxy, "
        "and stateless memory compression. Paid services via x402 on Solana USDC. "
        "Homepage: https://getkin.io"
    ),
)


# ---------------------------------------------------------------------------
# Tool 1: Model Recommendation (FREE)
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Get the optimal LLM for any task based on cost, speed, and quality data. "
        "Compares 17 models across 6 providers: Anthropic, OpenAI, Google, Mistral, "
        "DeepSeek, and Meta. Returns the top recommendation plus 3 alternatives with "
        "estimated cost, latency, and quality scores. FREE — no payment required."
    ),
)
async def recommend_model(
    task: Annotated[str, "Task type to optimize for. Options: code-generation, summarization, translation, creative-writing, data-analysis, classification, conversation, reasoning, extraction, general"],
    priority: Annotated[str, "What to optimize the recommendation for. Options: cost, speed, quality"] = "cost",
    max_tokens: Annotated[int, "Expected output length in tokens. Used to estimate cost."] = 1000,
) -> dict:
    """Get the optimal LLM for any task. Compares 17 models across 6 providers. FREE."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{ORACLE_URL}/models/recommend",
            params={"task": task, "priority": priority, "max_tokens": max_tokens},
        )
    return response.json()


# ---------------------------------------------------------------------------
# Tool 2: Check Availability
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Check real-time availability and latency of LLM provider API endpoints. "
        "Monitors Anthropic, OpenAI, Google, Mistral, DeepSeek, and Meta. "
        "Returns up/down status, response time in ms, and reliability percentage. "
        "Use this before making an API call to avoid wasting tokens on a down service. "
        "Costs $0.005 USDC via x402 on Solana."
    ),
)
async def check_availability(
    provider: Annotated[str, "Provider to check. Options: anthropic, openai, google, mistral, deepseek, meta, all. Use 'all' to get status for every monitored provider."] = "all",
) -> dict:
    """Check real-time availability and latency of LLM provider APIs. $0.005 USDC."""
    url = f"{MONITOR_URL}/status"
    if provider != "all":
        url = f"{MONITOR_URL}/status/{provider}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
    return response.json()


# ---------------------------------------------------------------------------
# Tool 3: Route LLM Call (Proxy)
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Route an LLM chat completion through GetKin's proxy. Uses OpenAI-compatible "
        "message format. We forward your request to the provider, return the full "
        "response including token usage, and charge a 3% margin on the provider cost. "
        "Currently supports Google Gemini models: gemini-2.5-flash, gemini-2.5-flash-lite, "
        "gemini-3-flash-preview, gemini-3.1-pro-preview. "
        "Costs provider rate + 3% margin via x402 on Solana USDC."
    ),
)
async def route_llm_call(
    model: Annotated[str, "Model ID to route to. Available: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-3-flash-preview, gemini-3.1-pro-preview"],
    messages: Annotated[list[dict], "Chat messages in OpenAI format. Each message is an object with 'role' (system/user/assistant) and 'content' (string)."],
    max_tokens: Annotated[int, "Maximum number of output tokens to generate."] = 1000,
    temperature: Annotated[float, "Controls randomness. 0.0 for deterministic, up to 2.0 for maximum creativity."] = 0.7,
) -> dict:
    """Route an LLM chat completion through GetKin's proxy. 3% margin on provider cost."""
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{PROXY_URL}/v1/chat/completions",
            json=body,
        )
    return response.json()


# ---------------------------------------------------------------------------
# Tool 4: Compress Memory
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Compress a raw session dump into structured short-term, medium-term, and "
        "long-term memory files. Stateless — we never store your data. Send your "
        "existing memory files (if any) plus the new session dump, and receive back "
        "updated structured memory. An LLM intelligently sorts information into the "
        "appropriate time tier. First 5 compressions per agent are free, then $0.03 "
        "USDC via x402 on Solana."
    ),
)
async def compress_memory(
    agent_id: Annotated[str, "Your unique agent identifier. Used only for free tier tracking — we hash it and never store the original."],
    session_dump: Annotated[str, "Raw session content to compress. Can include conversation logs, decisions made, observations, task results — anything from the work session. Max 50,000 characters."],
    existing_memory: Annotated[Optional[dict], "Your current memory files from a previous compression. Should contain short_term, medium_term, and long_term string fields. Omit on first use."] = None,
    session_metadata: Annotated[Optional[dict], "Optional metadata about the session. Can include task_type (string), duration_minutes (int), and tools_used (list of strings)."] = None,
) -> dict:
    """Compress a session dump into structured 3-tier memory. First 5 free, then $0.03 USDC."""
    body = {
        "agent_id": agent_id,
        "session_dump": session_dump,
    }
    if existing_memory:
        body["existing_memory"] = existing_memory
    if session_metadata:
        body["session_metadata"] = session_metadata

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{MEMORY_URL}/memory/compress",
            json=body,
        )
    return response.json()


# ---------------------------------------------------------------------------
# Tool 5: List Available Models (FREE)
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "List all LLM models available through GetKin's routing proxy with current "
        "per-token pricing. Returns model IDs, provider names, input cost per 1K tokens, "
        "output cost per 1K tokens, and the proxy margin percentage. "
        "FREE — no payment required."
    ),
)
async def list_models() -> dict:
    """List all models available through GetKin with current pricing. FREE."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{PROXY_URL}/v1/models")
    return response.json()


# ---------------------------------------------------------------------------
# Tool 6: Check Memory Usage (FREE)
# ---------------------------------------------------------------------------
@mcp.tool(
    description=(
        "Check how many free memory compressions remain for a specific agent. "
        "Returns the number of compressions used, free compressions remaining, "
        "whether the agent is still on the free tier, and the price after the "
        "free tier is exhausted. FREE — no payment required."
    ),
)
async def check_memory_usage(
    agent_id: Annotated[str, "The unique agent identifier to check free tier usage for."],
) -> dict:
    """Check how many free memory compressions remain for an agent. FREE."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{MEMORY_URL}/memory/usage/{agent_id}")
    return response.json()


# ---------------------------------------------------------------------------
# Resource: GetKin Service Status
# ---------------------------------------------------------------------------
@mcp.resource("getkin://status")
async def getkin_status() -> str:
    """Current operational status of all four GetKin services — oracle, monitor, proxy, and memory."""
    status = {}
    services = {
        "oracle": ORACLE_URL,
        "monitor": MONITOR_URL,
        "proxy": PROXY_URL,
        "memory": MEMORY_URL,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, url in services.items():
            try:
                r = await client.get(f"{url}/health")
                data = r.json()
                status[name] = {"status": data.get("status", "unknown"), "url": url}
            except Exception:
                status[name] = {"status": "unreachable", "url": url}

    return json.dumps(status, indent=2)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http", stateless_http=True, host="0.0.0.0", port=8080)
