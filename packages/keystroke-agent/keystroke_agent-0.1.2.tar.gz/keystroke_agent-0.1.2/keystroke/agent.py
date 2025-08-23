from rich.console import Console
from rich.prompt import Prompt
import litellm
import json
import asyncio
import warnings
from dotenv import load_dotenv
from tools import TOOLS, TOOLS_MAP
from keystroke.settings import (
    AGENT_NAME,
    DEFAULT_LLM_MODEL,
    DEFAULT_SYSTEM_MESSAGE,
    MAX_TOKENS,
    HISTORY_LIMIT,
    ENABLE_TOOLS,
)

load_dotenv()
# Ignore warnings
warnings.filterwarnings("ignore")

async def llm_response(messages: list[dict], llm_model=None, tools=None):
    response = await litellm.acompletion(
        model=llm_model,
        messages=messages,
        max_tokens=MAX_TOKENS,
        tools=tools if tools else None
    )
    return response["choices"][0]["message"]

async def tool_response(messages: list[dict]):
    tool_call_text = ""
    tool_return_text = ""
    for tool_call in messages["tool_calls"]:
        tool_name = tool_call["function"]["name"]
        tool_args = tool_call["function"]["arguments"]
        tool_args_dict = json.loads(tool_args)
        tool_call_text = f"[Calling tool {tool_name} with args {tool_args_dict}]"
        print(tool_call_text)
        try:
            result = TOOLS_MAP[tool_name](**tool_args_dict)
            tool_return_text = f"[Tool {tool_name} returned: {result}]"
        except Exception as e:
            tool_return_text = f"[Tool {tool_name} failed: {str(e)}]"
        print(tool_return_text)
    msg_content = tool_call_text + "\n" + tool_return_text
    return {"role": "user", "content": msg_content}

class Agent:
    def __init__(self, name=AGENT_NAME):
        self.name = name
        self.console = Console()
        self.history = []
        self.sys_msg = {
            "role": "system",
            "content": DEFAULT_SYSTEM_MESSAGE
        }
        self.llm_model = DEFAULT_LLM_MODEL
        self.tools_schema = TOOLS if ENABLE_TOOLS else None

    async def greet(self):
        return f"Hello, my name is {self.name}."
    
    async def _handle_dot_commands(self, input_text):
        parts = input_text.lower().split()
        base_cmd = parts[0]
        if base_cmd == ".help":
            self.console.print("[bold blue]Available commands:[/bold blue]")
            self.console.print("  .help - Show this help message")
            self.console.print("  .clear - Clear the conversation history")
            self.console.print("  .model <model_name> - Change the LLM model")
            self.console.print("  .view - View current settings")
            self.console.print("  .system <message> - Change the system message")
            self.console.print("  .name <new_name> - Change the assistant's name")
        elif base_cmd == ".clear":
            self.history = []
            self.console.print("[italic]Conversation history cleared.[/italic]")
        elif base_cmd == ".model" and len(parts) > 1:
            new_model = " ".join(parts[1:])
            self.llm_model = new_model
            self.console.print(f"[italic]Model changed to: {new_model}[/italic]")
        elif base_cmd == ".view":
            self.console.print(f"[bold blue]Current settings:[/bold blue]")
            self.console.print(f"  Model: {self.llm_model}")
            self.console.print(f"  System message: {self.sys_msg['content']}")
            self.console.print(f"  History length: {len(self.history)} messages (limit: {HISTORY_LIMIT})")
            self.console.print(f"  Assistant name: {self.name}")
        elif base_cmd == ".system" and len(parts) > 1:
            new_system = " ".join(parts[1:])
            self.sys_msg = {"role": "system", "content": new_system}
            self.console.print(f"[italic]System message updated.[/italic]")
        elif base_cmd == ".name" and len(parts) > 1:
            new_name = " ".join(parts[1:])
            self.name = new_name.capitalize()
            self.console.print(f"[italic]Assistant name changed to: {self.name}[/italic]")

        return await self.user_input()
    
    async def user_input(self):
        input_text = Prompt.ask(f"You:")
        if input_text.lower() in ["exit", "quit", "q"]:
            self.console.print("Exiting...")
            return
        if input_text.startswith("."):
            return await self._handle_dot_commands(input_text)
        msg = {"role": "user", "content": input_text}
        self.history.append(msg)
        # Enforce history limit
        if len(self.history) > HISTORY_LIMIT:
            self.history = self.history[-HISTORY_LIMIT:]
        return await self.call_llm()
    
    async def call_llm(self):
        msg = await llm_response(self.history, llm_model=self.llm_model, tools=self.tools_schema)
        self.console.print(f"[bold green]{self.name}:[/bold green] {msg['content']}")
        if msg["content"]:
            self.history.append({"role": "assistant", "content": msg["content"]})
        return await self.call_controller(msg)
    
    async def call_tool(self, msg):
        result = await tool_response(msg)
        self.history.append(result)
        return await self.call_llm()

    async def call_controller(self, msg):
        if msg.get("tool_calls"):
            return await self.call_tool(msg)
        return await self.user_input()
    
def main():
    """Entry point for CLI."""
    agent = Agent()
    asyncio.run(agent.user_input())

if __name__ == "__main__":
    main()


