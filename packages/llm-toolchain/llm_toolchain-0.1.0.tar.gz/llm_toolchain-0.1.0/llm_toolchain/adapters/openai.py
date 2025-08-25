import inspect
import json
from typing import get_type_hints, Any

# Import from your library's modules
from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

class OpenAIAdapter(BaseAdapter):
    """
    An adapter specifically for the official 'openai' library,
    handling its native tool-calling API.
    """

    def generate_schema(self, tool: Tool) -> dict:
        """
        Generates the OpenAI-specific schema.
        
        It calls the base class's helper to get the universal schema parts
        and then wraps them in the OpenAI-specific 'function' envelope.
        """
        # 1. Get the pre-built, generic schema from the parent.

        generic_schema = self._inspect_and_build_json_schema(tool)


        # 2. Perform the ONLY adapter-specific task: formatting the envelope.
        return {
            "type": "function",
            "function": {
                "name": generic_schema["name"],
                "description": generic_schema["description"],
                "parameters": generic_schema["parameters_schema"],
            },
        }
    def chat(self, llm_client: Any, messages: list[dict], tools: list[dict], **kwargs) -> Any:

        """
        Formats the request and calls the OpenAI Chat Completions API.
        It passes through any extra keyword arguments like 'tool_choice'.
        """
        final_messages = []
        if self.system_prompt:
            final_messages.append({"role": "system", "content": self.system_prompt})
        
        final_messages.extend(messages)
        
        # This is the actual call to the openai library
        return llm_client.chat.completions.create(
            messages=final_messages,
            tools=tools,
            model="gpt-4o",  # Default model, can be overridden
            **kwargs  # Pass through extra options
        )

    def parse(self, response: Any) -> ParseResult:
        """
        Parses the raw response. If tool calls are present, it returns a tuple:
        (list[ToolCall], assistant_message_dict).
        Otherwise, it returns a FinalAnswer.
        """
        response_message = response.choices[0].message

        if response_message.tool_calls:
            tool_calls = []
            for tc in response_message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {"error": f"Malformed JSON from LLM: {tc.function.arguments}"}

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        args=arguments
                    )
                )
            
            # Convert the Pydantic message object to a plain dictionary
            # This is the key change for the OpenAI adapter
            assistant_message_dict = response_message.model_dump(exclude_unset=True)
            return (tool_calls, assistant_message_dict)
        
        # If there are no tool calls, return a FinalAnswer as before
        return FinalAnswer(content=response_message.content)
        
        # If there are no tool calls, it's a final text answer
        return FinalAnswer(content=response_message.content)

