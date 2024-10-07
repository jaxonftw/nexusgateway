import json
from typing import Any, Dict, List


CURVE_FUNCTION_CALLING_TASK_PROMPT = """
You are a helpful assistant.
""".strip()


CURVE_FUNCTION_CALLING_TOOL_PROMPT = """
# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tool_text}
</tools>
""".strip()


CURVE_FUNCTION_CALLING_FORMAT_PROMPT = """
For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
""".strip()


class CurveHandler:
    def __init__(self) -> None:
        super().__init__()

    def _format_system(self, tools: List[Dict[str, Any]]):
        def convert_tools(tools):
            return "\n".join([json.dumps(tool) for tool in tools])

        tool_text = convert_tools(tools)

        system_prompt = (
            CURVE_FUNCTION_CALLING_TASK_PROMPT
            + "\n\n"
            + CURVE_FUNCTION_CALLING_TOOL_PROMPT.format(tool_text=tool_text)
            + "\n\n"
            + CURVE_FUNCTION_CALLING_FORMAT_PROMPT
        )

        return system_prompt

    def _add_execution_results_prompting(
        self,
        messages: list[dict],
        execution_results: list,
    ) -> dict:
        content = []
        for result in execution_results:
            content.append(f"<tool_response>\n{json.dumps(result)}\n</tool_response>")

        content = "\n".join(content)
        messages.append({"role": "user", "content": content})

        return messages

    def extract_tools(self, result: str):
        lines = result.split("\n")
        flag = False
        func_call = []
        for line in lines:
            if "<tool_call>" == line:
                flag = True
            elif "</tool_call>" == line:
                flag = False
            else:
                if flag:
                    try:
                        tool_result = json.loads(line)
                    except Exception:
                        fixed_content = self.fix_json_string(line)
                        try:
                            tool_result = json.loads(fixed_content)
                        except json.JSONDecodeError:
                            return result
                    func_call.append({tool_result["name"]: tool_result["arguments"]})
                flag = False
        return func_call

    def fix_json_string(self, json_str: str):
        # Remove any leading or trailing whitespace or newline characters
        json_str = json_str.strip()

        # Stack to keep track of brackets
        stack = []

        # Clean string to collect valid characters
        fixed_str = ""

        # Dictionary for matching brackets
        matching_bracket = {")": "(", "}": "{", "]": "["}

        # Dictionary for the opposite of matching_bracket
        opening_bracket = {v: k for k, v in matching_bracket.items()}

        for char in json_str:
            if char in "{[(":
                stack.append(char)
                fixed_str += char
            elif char in "}])":
                if stack and stack[-1] == matching_bracket[char]:
                    stack.pop()
                    fixed_str += char
                else:
                    # Ignore the unmatched closing brackets
                    continue
            else:
                fixed_str += char

        # If there are unmatched opening brackets left in the stack, add corresponding closing brackets
        while stack:
            unmatched_opening = stack.pop()
            fixed_str += opening_bracket[unmatched_opening]

        # Attempt to parse the corrected string to ensure it’s valid JSON
        return fixed_str
