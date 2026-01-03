# Main agent logic and conversation loop
import json
import re
from openai import AsyncOpenAI

from src.config import config
from src.prompts.system import SYSTEM_PROMPT
from src.tools.handlers import handle_tool_call


def parse_response(response_text: str) -> tuple[str | None, dict | None, str | None]:
    """
    Parse a ReAct-style response from the model.

    Returns:
        Tuple of (thought, action_dict, final_answer)
        - If action_dict is not None, it's a tool call
        - If final_answer is not None, it's the final response
    """
    thought = None
    action = None
    answer = None

    # Extract thought
    thought_match = re.search(
        r"Thought:\s*(.+?)(?=\nAction:|\nAnswer:|$)", response_text, re.DOTALL
    )
    if thought_match:
        thought = thought_match.group(1).strip()

    # Check for final answer
    answer_match = re.search(r"Answer:\s*(.+)", response_text, re.DOTALL)
    if answer_match:
        answer = answer_match.group(1).strip()
        return thought, None, answer

    # Check for action (tool call)
    action_match = re.search(r"Action:\s*(\{.*\})", response_text, re.DOTALL)
    if action_match:
        try:
            action = json.loads(action_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return thought, action, answer


async def run_agent(user_message: str, max_iterations: int = 10) -> str:
    """
    Run the agent loop with ReAct-style tool calling.

    Args:
        user_message: The user's input message
        max_iterations: Maximum number of tool call iterations

    Returns:
        The final response from the agent
    """
    client = AsyncOpenAI(api_key=config.api_key)

    # Build the conversation as a single input string
    conversation = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"

    # Track collected data
    collected_data: list[str] = []

    for _ in range(max_iterations):
        response = await client.responses.create(
            model=config.model,
            input=conversation,
            max_output_tokens=config.max_tokens,
            reasoning={"effort": "medium"},
        )

        assistant_message = response.output_text
        conversation += f"\n\nAssistant: {assistant_message}"

        # Parse the ReAct response
        thought, action, answer = parse_response(assistant_message)

        # If we have a final answer, return it
        if answer is not None:
            return answer

        # If no action and no answer, nudge the model to continue
        if action is None:
            conversation += (
                "\n\n[Continue with the next Action or provide your final Answer.]"
            )
            continue

        # Execute the tool
        tool_name = action.get("tool_name", "")
        arguments = action.get("arguments", {})

        if not tool_name:
            return "Error: No tool name specified in action."
        print(f"Tool name: {tool_name}")
        print(f"Arguments: {arguments}")
        try:
            result = await handle_tool_call(tool_name, arguments)
            tool_result = json.dumps(result, indent=2)

            # Track what data we collected
            if tool_name == "get_weather":
                location = result.get("name", "unknown location")
                collected_data.append(f"weather for {location}")
            elif tool_name == "web_search":
                query = arguments.get("query", "")
                collected_data.append(f"web search results for '{query}'")

        except Exception as e:
            tool_result = f"Error: {str(e)}"

        # Add tool result and reminder of collected data
        conversation += f"\n\nObservation ({tool_name}):\n```json\n{tool_result}\n```"

        if collected_data:
            conversation += f"\n\n[DATA COLLECTED: {', '.join(collected_data)}. If you have all needed info, provide your Answer now.]"

    return "Max iterations reached. Please try again with a simpler query."
