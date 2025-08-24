# Copyright 2025 The EasyDeL/Calute Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import re
from datetime import datetime
from typing import Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict


class CaluteBase(BaseModel):
    r"""
    Forbids extra attributes, validates default values and use enum values.
    """

    model_config = ConfigDict(extra="forbid", validate_default=True, use_enum_values=True)


def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


def merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, str):
            target[key] += value
        elif value is not None and isinstance(value, dict):
            merge_fields(target[key], value)


def merge_chunk(final_response: dict, delta: dict) -> None:
    delta.pop("role", None)
    merge_fields(final_response, delta)

    tool_calls = delta.get("tool_calls")
    if tool_calls and len(tool_calls) > 0:
        index = tool_calls[0].pop("index")
        merge_fields(final_response["tool_calls"][index], tool_calls[0])


def function_to_json(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.
    Args:
        func: The function to be converted.
    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
        tuple: "array",
        set: "array",
        bytes: "string",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {func.__name__}: {e!s}") from e
    docstring = func.__doc__ or ""
    param_descriptions = {}
    param_pattern = r"(\w+)(?:\s*\([^)]+\))?\s*:\s*(.+?)(?=\n\s*\w+(?:\s*\([^)]+\))?\s*:|$)"
    matches = re.findall(param_pattern, docstring, re.DOTALL | re.MULTILINE)
    for param_name, description in matches:
        param_descriptions[param_name.strip()] = description.strip()

    parameters = {}
    for param in signature.parameters.values():
        param_info = {"type": "string"}

        if param.annotation != inspect.Parameter.empty:
            origin = get_origin(param.annotation)
            args = get_args(param.annotation)

            if origin is Union:
                non_none_types = [arg for arg in args if arg is not type(None)]
                if len(non_none_types) == 1 and type(None) in args:
                    param_info["type"] = type_map.get(non_none_types[0], "string")
                else:
                    param_info = {"type": "union", "types": [type_map.get(arg, "string") for arg in args]}
            elif origin in (list, tuple, set):
                param_info["type"] = "array"
                if args:
                    param_info["items"] = {"type": type_map.get(args[0], "string")}
            elif param.annotation in type_map:
                param_info["type"] = type_map[param.annotation]
            else:
                param_info["type"] = (
                    param.annotation.__name__ if hasattr(param.annotation, "__name__") else str(param.annotation)
                )

        if param.name in param_descriptions:
            param_info["description"] = param_descriptions[param.name]
        if param.default != inspect.Parameter.empty:
            pass

        parameters[param.name] = param_info

    required = [param.name for param in signature.parameters.values() if param.default == inspect.Parameter.empty]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }
