import json
from typing import Callable
import inspect
from google import generativeai as genai
from openai import OpenAI
from .models import FinalAnswer, ParseResult, ToolCall



# --- The Tool Class and Decorator ---


class Tool:
    """A simpler wrapper that just holds the function and its signature."""
    def __init__(self, function: Callable):
        self.name = function.__name__
        self.description = inspect.getdoc(function)
        self.signature = inspect.signature(function)
        self.function = function

def tool(func: Callable) -> Tool:
    """The decorator now just wraps the function in the Tool class."""
    if not func.__doc__:
        raise ValueError("Tool function must have a docstring for its description.")
    return Tool(function=func)

# --- The Main Toolchain Class ---


class Toolchain:
    """
    The main orchestrator that manages tools and executes LLM-driven workflows.
    """

    def __init__(self, tools: list[Tool]):
        """
        Initializes the Toolchain with a list of tools.

        Args:
            tools: A list of Tool objects, typically created with the @tool decorator.
        """
        # The internal tool registry, mapping tool names to Tool objects
        self.tools = {t.name: t for t in tools}

    def _get_adapter(self, llm_client):
        from .adapters import OpenAIAdapter
        if isinstance(llm_client, OpenAI):
            return OpenAIAdapter()
        if isinstance(llm_client, genai.GenerativeModel):
            from .adapters import GeminiAdapter
            return GeminiAdapter()



    # --- High-Level "Simple" Method ---


    def run(self, prompt: str, llm, adapter=None, **kwargs) -> str:
        """
        The main high-level method. Handles the entire ReAct loop automatically.
        This version is fully generic and relies on the adapter for all parsing.
        """
        adapter = adapter or self._get_adapter(llm)
        messages = [{"role": "user", "content": prompt}]

        while True:
            tools_as_schema = [adapter.generate_schema(t) for t in self.tools.values()]
            
            # Use the adapter to call the LLM
            response = adapter.chat(
                llm_client=llm,
                messages=messages,
                tools=tools_as_schema,
                **kwargs
            )
            print(f"LLM raw response: {response}")  # Debugging line
            # The adapter does all the hard work of parsing
            parsed_result = adapter.parse(response)

            if isinstance(parsed_result, FinalAnswer):

                # The conversation is over, return the final content.
                return parsed_result.content

            # If the result is not a FinalAnswer, it must be a tuple
            # containing the tool calls and the raw assistant message.
            tool_calls, assistant_message = parsed_result
            
            tool_outputs = []
            for tool_call in tool_calls:
                output = self.execute_tool(tool_call)
                tool_outputs.append(output)

            # Append the standardized assistant message and the tool outputs to history
            messages.append(assistant_message)
            messages.extend(tool_outputs)

        # --- Low-Level "Tinkering" Building Blocks ---

    def prepare_messages(self, prompt: str, history: list = None) -> list[dict]:
        """Prepares the message list for an API call. (For advanced use)"""
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        return messages

    def parse_response(self, response, adapter) -> ParseResult:
        """Parses the raw LLM response. (For advanced use)"""
        return adapter.parse(response)  # Delegate parsing to the adapter

    def execute_tool(self, tool_call: ToolCall) -> dict:
        """Executes a single tool call and returns the formatted output. (For advanced use)"""
        if tool_call.name not in self.tools:
            return {"error": f"Tool '{tool_call.name}' not found."}

        try:
            tool_obj = self.tools[tool_call.name]
            # Here we assume the adapter has already parsed args into a dict
            output = tool_obj.function(**tool_call.args)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": json.dumps(output),
            }
        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": f"Error executing tool: {e}",
            }
