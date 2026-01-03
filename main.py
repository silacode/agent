# Entry point
import asyncio
from src.agent import run_agent


async def main():
    print("=" * 50)
    print("ReAct Agent - Prompt-based Tool Calling Demo")
    print("=" * 50)
    print("Available tools: get_weather, web_search")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            response = await run_agent(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
