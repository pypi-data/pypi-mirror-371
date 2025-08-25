import json
import re
from typing import Any, Callable, Sequence

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

class PromptAdapter(BaseAdapter):
    """
    A generic adapter that can be manually configured with interaction paths
    or can automatically discover the correct methods for an unknown LLM client.
    """
    def __init__(
        self,
        call_path: Sequence[str] | None = None,
        response_path: Sequence[str | int] | None = None,
        arg_mapper: Callable[[list[dict], dict], dict] | None = None,
        *args, **kwargs
    ):
        """
        Initializes the adapter. Can be configured manually or left to auto-discover.

        Args:
            call_path: A sequence of attribute names to get to the callable chat method.
            response_path: A sequence of attributes/indices to get to the response text.
            arg_mapper: A function that maps messages/kwargs to the chat method's signature.
        """
        super().__init__(*args, **kwargs)
        # Manual configuration paths
        self._manual_call_path = call_path
        self._manual_response_path = response_path
        self._manual_arg_mapper = arg_mapper

        # Caching for auto-discovery
        self._discovered_call_style = None
        self._discovered_response_style = None
        self._strategies = self._get_strategies()

    def _get_strategies(self) -> list[dict[str, Any]]:
        """Defines all known interaction patterns for different LLM clients."""
        return [
            {
                "name": "openai",
                "call": lambda client, msgs, kw: client.chat.completions.create(messages=msgs, **kw),
                "parse": lambda resp: resp.choices[0].message.content
            },
            {
                "name": "anthropic",
                "call": lambda client, msgs, kw: client.messages.create(
                    messages=[m for m in msgs if m['role'] != 'system'],
                    system=next((m['content'] for m in msgs if m['role'] == 'system'), None),
                    **kw
                ),
                "parse": lambda resp: resp.content[0].text
            },
            {
                "name": "gemini",
                "call": lambda client, msgs, kw: client.generate_content(
                    contents=self._format_gemini_contents(msgs),
                    generation_config=kw
                ),
                "parse": lambda resp: resp.text
            }
        ]

    def _discover_and_cache_style(self, llm_client: Any, messages: list[dict], **kwargs):
        """Discovers and caches the correct API interaction style."""
        test_kwargs = kwargs.copy()
        test_kwargs.setdefault('max_tokens', 2)

        for strategy in self._strategies:
            try:
                response = strategy["call"](llm_client, messages, test_kwargs)
                strategy["parse"](response)
                print(f"--- Discovered LLM style: {strategy['name']} ---")
                self._discovered_call_style = strategy['name']
                self._discovered_response_style = strategy['name']
                return
            except (AttributeError, TypeError, IndexError, KeyError):
                continue
            except Exception as e:
                print(f"--- Assumed LLM style: {strategy['name']} (call failed with error: {e}) ---")
                self._discovered_call_style = strategy['name']
                self._discovered_response_style = strategy['name']
                return

        raise NotImplementedError("The provided LLM client does not match any known interaction style.")

    def _traverse_path(self, obj: Any, path: Sequence[str | int]) -> Any:
        """A helper to dynamically access a value in a nested object."""
        for key in path:
            obj = obj[key] if isinstance(key, int) else getattr(obj, key)
        return obj

    def generate_schema(self, tool: Tool) -> str:
        generic_schema = self._inspect_and_build_json_schema(tool)
        params = [f'{name}: {schema.get("type", "any")}' for name, schema in generic_schema["parameters_schema"]["properties"].items()]
        param_str = ", ".join(params)
        return f"- {generic_schema['name']}({param_str}): {generic_schema['description']}"

    def chat(self, llm_client: Any, messages: list[dict], tools: list[str], **kwargs) -> Any:
        instruction_prompt = f"""
You are a helpful assistant with access to a set of tools.
## AVAILABLE TOOLS:
{"\n".join(tools)}
## RESPONSE INSTRUCTIONS:
When you decide to call one or more tools, you MUST respond with ONLY a single, valid JSON object. Your entire response must be the JSON object. The JSON object must conform to this exact schema: {{"tool_calls": [{{"tool_name": "<tool_name>", "arguments": {{"<arg_name": "<arg_value>"}}}}]}}
If you do not need to call any tools, provide a final, natural language answer to the user.
"""
        final_messages = [{"role": "system", "content": instruction_prompt}]
        final_messages.extend(messages)

        # --- Priority 1: Use manual configuration if provided ---
        if self._manual_call_path and self._manual_arg_mapper:
            try:
                call_func = self._traverse_path(llm_client, self._manual_call_path)
                mapped_args = self._manual_arg_mapper(final_messages, kwargs)
                return call_func(**mapped_args)
            except (AttributeError, IndexError, TypeError) as e:
                raise RuntimeError(f"Failed to call LLM using the provided manual call_path. Error: {e}")

        # --- Priority 2: Use auto-discovery ---
        if not self._discovered_call_style:
            self._discover_and_cache_style(llm_client, final_messages, **kwargs)

        for strategy in self._strategies:
            if strategy['name'] == self._discovered_call_style:
                return strategy['call'](llm_client, final_messages, kwargs)
        
        raise RuntimeError("Could not determine a valid method to call the LLM.")

    def parse(self, response: Any) -> ParseResult:
        response_text = None
        # --- Priority 1: Use manual configuration if provided ---
        if self._manual_response_path:
            try:
                response_text = self._traverse_path(response, self._manual_response_path)
            except Exception:
                response_text = str(response)
        # --- Priority 2: Use auto-discovery ---
        elif self._discovered_response_style:
            for strategy in self._strategies:
                if strategy['name'] == self._discovered_response_style:
                    try:
                        response_text = strategy['parse'](response)
                    except Exception: break
        
        if response_text is None:
            response_text = str(response)

        if isinstance(response_text, str):
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                json_string = match.group(0)
                try:
                    parsed_json = json.loads(json_string)
                    tool_calls_data = parsed_json.get("tool_calls")
                    if isinstance(tool_calls_data, list):
                        tool_calls_list = []
                        for call_data in tool_calls_data:
                            tool_name = call_data.get("tool_name")
                            arguments = call_data.get("arguments")
                            if isinstance(tool_name, str) and isinstance(arguments, dict):
                                tool_call_id = f"call_{tool_name}_{len(tool_calls_list)}"
                                tool_calls_list.append(ToolCall(id=tool_call_id, name=tool_name, args=arguments))
                        if tool_calls_list:
                            assistant_message_dict = {"role": "assistant", "content": json_string}
                            return (tool_calls_list, assistant_message_dict)
                except json.JSONDecodeError: pass
            
            return FinalAnswer(content=response_text)

        return FinalAnswer(content=str(response))

    def _format_gemini_contents(self, messages: list[dict]) -> list[dict]:
        contents = []
        for msg in messages:
            role = "model" if msg.get("role") in ["assistant", "system"] else "user"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
        return contents
