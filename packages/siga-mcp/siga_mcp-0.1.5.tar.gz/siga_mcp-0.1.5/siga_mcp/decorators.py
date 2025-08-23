import inspect
import re
import types
from functools import wraps
from typing import Literal, Union, get_args, get_origin

from fastmcp import FastMCP


def tool(server: FastMCP, transport: Literal["stdio", "http"]):
    """
    Decorator that conditionally removes CURRENT_USER support based on MCP_TRANSPORT.

    If MCP_TRANSPORT != "stdio", removes Literal["CURRENT_USER"] from function signatures
    and cleans related documentation.
    """

    def decorator(func):
        if transport == "stdio":
            return server.tool(func)

        # Remove CURRENT_USER from annotations
        def remove_current_user_from_annotation(annotation):
            if annotation == inspect.Parameter.empty or annotation is None:
                return annotation

            origin = get_origin(annotation)

            if origin is Union or (
                hasattr(types, "UnionType") and isinstance(annotation, types.UnionType)
            ):
                args = get_args(annotation)
                new_args = [
                    arg
                    for arg in args
                    if not (
                        get_origin(arg) is Literal and "CURRENT_USER" in get_args(arg)
                    )
                ]

                if len(new_args) == 0:
                    return str
                elif len(new_args) == 1:
                    return new_args[0]
                else:
                    if hasattr(types, "UnionType") and isinstance(
                        annotation, types.UnionType
                    ):
                        result = new_args[0]
                        for arg in new_args[1:]:
                            result = result | arg
                        return result
                    else:
                        return Union[tuple(new_args)]

            if get_origin(annotation) is Literal and "CURRENT_USER" in get_args(
                annotation
            ):
                return str

            return annotation

        # Remove CURRENT_USER from docstring
        def remove_current_user_from_docstring(docstring):
            if not docstring:
                return docstring

            lines = docstring.split("\n")
            new_lines = []
            skip_next_lines = False

            for line in lines:
                if any(
                    phrase in line
                    for phrase in [
                        'If "CURRENT_USER"',
                        'Se "CURRENT_USER"',
                        'If matricula == "CURRENT_USER"',
                        '- "CURRENT_USER":',
                    ]
                ):
                    skip_next_lines = True
                    continue

                if skip_next_lines:
                    if line.strip() and (
                        line.strip().endswith(":")
                        or line.lstrip().startswith(
                            ("Args:", "Returns:", "Raises:", "Examples:", "Notes:")
                        )
                        or re.match(r"\s*\w+\s*\([^)]*\):", line)
                    ):
                        skip_next_lines = False
                    else:
                        continue

                cleaned_line = line
                cleaned_line = re.sub(
                    r'\s*\|\s*Literal\["CURRENT_USER"\]', "", cleaned_line
                )
                cleaned_line = re.sub(
                    r'Literal\["CURRENT_USER"\]\s*\|\s*', "", cleaned_line
                )
                cleaned_line = re.sub(r',?\s*"CURRENT_USER"[^,\n]*', "", cleaned_line)
                cleaned_line = re.sub(r'\s*-\s*"CURRENT_USER"[^-\n]*', "", cleaned_line)
                cleaned_line = re.sub(r"\s+", " ", cleaned_line)
                cleaned_line = re.sub(r"\s*\|\s*\)", ")", cleaned_line)
                cleaned_line = re.sub(r",\s*\)", ")", cleaned_line)

                new_lines.append(cleaned_line)

            result = "\n".join(new_lines)
            return re.sub(r"\n\s*\n\s*\n", "\n\n", result)

        # Create modified function
        sig = inspect.signature(func)
        new_params = []

        for param_name, param in sig.parameters.items():
            new_annotation = remove_current_user_from_annotation(param.annotation)
            new_default = (
                param.default
                if param.default != "CURRENT_USER"
                else inspect.Parameter.empty
            )
            new_param = param.replace(annotation=new_annotation, default=new_default)
            new_params.append(new_param)

        new_sig = sig.replace(parameters=new_params)
        new_docstring = remove_current_user_from_docstring(func.__doc__ or "")

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        wrapper.__signature__ = new_sig
        wrapper.__doc__ = new_docstring

        new_annotations = {}
        for param_name, param in new_sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                new_annotations[param_name] = param.annotation

        if hasattr(func, "__annotations__") and "return" in func.__annotations__:
            new_annotations["return"] = func.__annotations__["return"]

        wrapper.__annotations__ = new_annotations

        return server.tool(wrapper)

    return decorator
