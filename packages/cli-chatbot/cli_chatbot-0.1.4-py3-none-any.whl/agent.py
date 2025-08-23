from rich.console import Console
from rich.prompt import Prompt
import litellm
from fastmcp import Client
import json
import asyncio

async def llm_response(messages: list[dict], llm_model=None, tools=None):
    response = await litellm.acompletion(
        model=llm_model,
        messages=messages,
        max_tokens=1000,
        tools=tools if tools else None
    )
    return response["choices"][0]["message"]

async def tool_response(messages: list[dict], mcp_client: Client):
    async with mcp_client:
        for tool_call in messages["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]
            tool_args_dict = json.loads(tool_args)
            tool_call_text = f"[Calling tool {tool_name} with args {tool_args_dict}]"
            print(tool_call_text)
            try:
                result = await mcp_client.call_tool(tool_name, tool_args_dict)
                tool_return_text = f"[Tool {tool_name} returned: {result.content}]"
            except Exception as e:
                tool_return_text = f"[Tool {tool_name} failed: {str(e)}]"
            
    msg_content = tool_call_text + "\n" + tool_return_text
    return {"role": "user", "content": msg_content}

class Agent:
    def __init__(self, name, transport):
        self.name = name
        self.console = Console()
        self.history = []
        self.sys_msg = {
            "role": "system",
            "content": f"You are a helpful assistant named {self.name}."
        }
        self.llm_model = "gemini/gemini-2.0-flash"
        self.mcp_client = Client(transport)
        self.tools_schema = []

    async def greet(self):
        return f"Hello, my name is {self.name}."
    
    async def user_input(self):
        input_text = Prompt.ask(f"You:")
        msg = {"role": "user", "content": input_text}
        self.history.append(msg)
        return await self.call_llm()
    
    async def get_tools(self):
        if self.tools_schema:
            return self.tools_schema
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()
        for tool in tools:
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema or {"type": "object", "properties": {}}
                }
            }
            self.tools_schema.append(tool_schema)
        return self.tools_schema
    
    async def call_llm(self):
        msg = await llm_response(self.history, llm_model=self.llm_model, tools=await self.get_tools())
        self.console.print(f"[bold green]{self.name}:[/bold green] {msg['content']}")
        if msg["content"]:
            self.history.append({"role": "assistant", "content": msg["content"]})
        return await self.call_controller(msg)
    
    async def call_tool(self, msg):
        result = await tool_response(msg, self.mcp_client)
        self.history.append(result)
        return result
        
    async def call_controller(self, msg):
        if msg.get("tool_calls"):
            return await self.call_tool(msg)
        return await self.user_input()
    
if __name__ == "__main__":
    agent = Agent(name="Auto-Form Agent", transport="http://localhost:8931/mcp")
    asyncio.run(agent.user_input())
        
        
