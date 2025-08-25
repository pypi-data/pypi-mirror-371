import json
from typing import Any

from google.generativeai import types, GenerativeModel

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

# A clear error message for the user
GEMINI_INSTALL_MESSAGE = (
    "To use the GeminiAdapter, you must install the google-generativeai library. "
    "Please run 'pip install toolchain[gemini]' or 'pip install google-generativeai'."
)

class GeminiAdapter(BaseAdapter):
    """
    An adapter for Google's Gemini models. It lazy-imports the google-generativeai
    library to keep the core toolchain installation lightweight.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We can check for the library at initialization to fail early.
        try:
            from google.generativeai import types, GenerativeModel
        except ImportError:
            raise ImportError(GEMINI_INSTALL_MESSAGE)

    def generate_schema(self, tool: Tool) -> dict:
        generic_schema = self._inspect_and_build_json_schema(tool)
        return {
            "name": generic_schema["name"],
            "description": generic_schema["description"],
            "parameters": generic_schema["parameters_schema"],
        }

    def chat(self, llm_client, messages: list[dict], tools: list[dict], **kwargs) -> Any:
        """
        Formats the request and calls the Gemini API's generate_content method.
        """


        # 1. Prepare the tools in the format Gemini expects.
        gemini_tools = types.Tool(function_declarations=tools)


        # 2. Separate standard generation config from other kwargs.
        #    These are things like temperature, top_p, etc.
        generation_config = kwargs
        # 3. Format the message history
        contents = self._format_contents(messages)

        # 4. Make the API call with the correct parameters
        return llm_client.generate_content(
            contents=contents,
            tools=[gemini_tools], 
            generation_config=generation_config, 
   
        )
    def parse(self, response: Any) -> ParseResult:
        """
        Parses the raw response. If tool calls are present, it returns a tuple:
        (list[ToolCall], assistant_message_dict).
        Otherwise, it returns a FinalAnswer.
        """
        try:
            part = response.candidates[0].content.parts[0]

            if part.function_call:
                fc = part.function_call
                arguments = dict(fc.args)
                tool_call_id = f"call_{fc.name}"
                
                tool_calls_list = [
                    ToolCall(id=tool_call_id, name=fc.name, args=arguments)
                ]
                
                # This is the message that represents the assistant's turn.
                # It gets added to the history.
                assistant_message_dict = {
                    "role": "model",
                    "parts": [{"function_call": {"name": fc.name, "args": arguments}}]
                }
                
                return (tool_calls_list, assistant_message_dict)
            
            return FinalAnswer(content=response.text)

        except (IndexError, AttributeError):
            try:
                return FinalAnswer(content=response.text)
            except Exception:
                return FinalAnswer(content="Failed to parse Gemini response.")


                

    def _format_contents(self, messages: list[dict]) -> list[dict]:
        """
        A helper to convert the generic message history into the list of
        dictionaries that the Gemini API expects. This version correctly
        handles all message types in the conversation history.
        """
        contents = []
        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else msg.get("role")
            
            # This is the key change: we now handle different message structures
            if role == "tool":
                part = {
                    "function_response": {
                        "name": msg["name"],
                        "response": json.loads(msg["content"])
                    }
                }
                role = 'user' # Gemini expects tool responses to have the 'user' role
            elif "parts" in msg:
                # This handles the assistant_message_dict from a previous turn
                part = msg["parts"][0]
            else:
                # This handles a standard user message
                part = {"text": msg.get("content", "")}

            contents.append({"role": role, "parts": [part]})
        
        return contents