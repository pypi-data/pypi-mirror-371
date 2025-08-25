from abc import ABC, abstractmethod
from toolchain.core import Tool
from typing import get_type_hints

import inspect
from toolchain.models import ParseResult, ToolCall, FinalAnswer

class BaseAdapter(ABC):

    def __init__(self, system_prompt: str | None = None):
        self.system_prompt = system_prompt

    def _inspect_and_build_json_schema(self, tool: Tool) -> dict:
        """
        A universal helper to inspect a Tool and build a generic
        JSON Schema representation of its parameters.
        
        This is the common logic that all adapters will need.
        """
        type_hints = get_type_hints(tool.function)
        properties = {}
        required = []

        for name, param in tool.signature.parameters.items():
            py_type = type_hints.get(name, str)
            
            # Universal Python-to-JSON Schema type mapping
            if py_type is str:
                properties[name] = {"type": "string"}
            elif py_type is int:
                properties[name] = {"type": "integer"}
            elif py_type is float:
                properties[name] = {"type": "number"}
            elif py_type is bool:
                properties[name] = {"type": "boolean"}
            else:
                properties[name] = {"type": "string"} # Default for complex types

            if param.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    
    @abstractmethod
    def generate_schema(self, tool: Tool) -> dict:
        """Generates the model-specific JSON schema for a given tool."""
        pass

    @abstractmethod
    def chat(self, llm_client, messages: list[dict], tools: list[dict]) -> any:
        """Formats the request and calls the LLM API."""
        pass

    @abstractmethod
    def parse(self, response: any) -> ParseResult:
        """Parses the raw LLM response into a standard ToolCall or FinalAnswer."""
        pass
    