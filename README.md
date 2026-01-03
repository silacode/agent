# ReAct Agent - Prompt-based Tool Calling
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

A minimal implementation of an AI agent using the **ReAct (Reasoning + Acting)** pattern with prompt-based tool calling. Built for educational purposes to understand the fundamentals before using higher-level SDKs.

## What This Project Demonstrates

1. **Prompt-based tool calling** - Tool definitions embedded in the system prompt (no SDK `tools` parameter) - prompt engineering
2. **ReAct pattern** - Thought → Action → Observation → Answer loop
3. **Multi-tool handling** - Sequential tool execution with result tracking
4. **Async execution** - Using `httpx` and `AsyncOpenAI`
5. **Stateless messages** - No context between messages; each query is independent
6. **Intelligent tool reasoning** - Model decides whether to use tools for independent queries (weather + stock) or dependent queries (search → then use result for next action)

## Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│           Agent Loop                │
│  ┌─────────────────────────────┐   │
│  │ LLM (with ReAct prompt)     │   │
│  │ Thought: I need weather...  │   │
│  │ Action: {"tool_name": ...}  │   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │ Parse Response              │   │
│  │ - Extract Thought           │   │
│  │ - Extract Action or Answer  │   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │ Execute Tool                │   │
│  │ - get_weather (OpenWeather) │   │
│  │ - web_search (Tavily)       │   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  Observation added to context       │
│  Loop until Answer is provided      │
└─────────────────────────────────────┘
    ↓
Final Response
```

## File Structure

```
agent/
├── main.py              # Entry point with chat loop
├── pyproject.toml       # Dependencies
└── src/
    ├── agent.py         # Agent loop and response parsing
    ├── client.py        # OpenAI client initialization
    ├── config.py        # Environment config (API keys)
    ├── prompts/
    │   └── system.py    # ReAct system prompt with tool definitions
    └── tools/
        ├── definitions.py   # Tool schemas (OpenAI format) - NOT USED in prompt-based approach
        └── handlers.py      # Tool execution logic
```

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables** (create `.env`):
   ```
   OPENAI_API_KEY=your_openai_key
   WEATHER_API_KEY=your_openweathermap_key
   TAVILY-API-KEY=your_tavily_key
   ```

3. **Run the agent:**
   ```bash
   uv run python main.py
   ```

## Example

```
==================================================
ReAct Agent - Prompt-based Tool Calling Demo
==================================================
Available tools: get_weather, web_search
Type 'exit' or 'quit' to end the session.

You: What's the weather in Kingston Ontario and nvidia stock price?
Assistant: - Kingston, Ontario weather: broken clouds. Temperature about -6°C. Humidity 63%. Wind 4.1 m/s from the west.
- NVIDIA (NVDA) stock price: approximately $189.89 USD per share.

You: exit
Goodbye!
```

## Key Concepts Learned

| Concept | Implementation |
|---------|----------------|
| Tool definitions | Embedded in system prompt as structured text |
| Response parsing | Regex extraction of Thought/Action/Answer |
| Tool execution loop | Async loop until Answer is provided |
| Context tracking | `[DATA COLLECTED: ...]` markers |
| ReAct pattern | Thought → Action → Observation → Answer |
| Stateless design | No conversation memory; each message is independent |
| Tool reasoning | Model decides tool order for independent vs dependent queries |

## Next Steps

After understanding this bare-minimum implementation, explore:

1. **LLM SDK `tools` parameter** - Structured tool definitions, no prompt parsing needed
2. **OpenAI Agents SDK** - Auto tool execution loop, handoffs between agents
3. **LangGraph** - Graph-based workflows for complex agent patterns
4. **Multi-agent frameworks** - CrewAI, AutoGen for agent collaboration

## License

MIT

