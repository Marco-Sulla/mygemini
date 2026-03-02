import asyncio
from pathlib import Path

from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    ThinkingConfig,
    ThinkingLevel, Tool, ToolCodeExecution, GoogleSearch,
)


async def main():
    curr_path = Path(__file__)
    curr_dir = curr_path.parent

    with open(curr_dir / "api_key.txt") as f:
        api_key = f.read().strip()

    tools = [
        Tool(code_execution=ToolCodeExecution()),
        Tool(google_search=GoogleSearch()),
    ]

    thinking_conf = ThinkingConfig(
        thinking_level=ThinkingLevel.LOW,
        include_thoughts=True,
    )

    config = GenerateContentConfig(
        system_instruction="""
            My name is Marco. Write in simple text, not in markdown.
        """,
        thinking_config=thinking_conf,
        tools=tools,
    )

    async with Client(api_key=api_key).aio as client:
        chat = client.chats.create(
            model="gemini-3.1-pro-preview",
            config=config
        )

        print()
        print("Gemini e' pronto e al vostro servizio")
        print()
        while True:
            msg = input(">>> ")
            print()

            async for chunk in await chat.send_message_stream(msg):
                for part in chunk.parts:
                    text = part.text

                    if not text:
                        continue

                    if part.thought:
                        print("[THOUGHT - START]")
                        print(text)
                        print("[THOUGHT - END]")
                    elif part.executable_code:
                        print("[EXECUTING CODE - START]")
                        print(text)
                        print("[EXECUTING CODE - END]")
                    elif part.code_execution_result:
                        print("[CODE RESULT - START]")
                        print(text)
                        print("[CODE RESULT - END]")
                    else:
                        print(text)

            print()

asyncio.run(main())
