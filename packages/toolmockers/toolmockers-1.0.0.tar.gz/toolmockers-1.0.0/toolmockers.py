"""Tool mocking library for generating realistic mock responses using LLMs."""

import ast
import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


def generate_prompt(
    func: Callable,
    args: tuple,
    kwargs: dict,
    use_docstring: bool,
    use_code: bool,
    use_examples: bool,
    examples: Optional[List[Dict[str, Any]]],
) -> str:
    """Generate a prompt for the LLM to create a mock response.

    Args:
        func: The function to mock
        args: Positional arguments passed to the function
        kwargs: Keyword arguments passed to the function
        use_docstring: Whether to include the function's docstring
        use_code: Whether to include the function's source code
        use_examples: Whether to include examples
        examples: List of example input/output pairs

    Returns:
        The generated prompt string
    """
    logger.debug(f"Generating prompt for function: {func.__name__}")
    prompt_parts = []

    prompt_parts.append(
        """Generate a realistic mock response for this function call.
        Return only the result that the function should return, formatted as valid Python data (string, number, list, dict, etc.).
        Use the following data:"""
    )

    # Function signature
    sig = inspect.signature(func)
    prompt_parts.append(f"Function: {func.__name__}{sig}")

    # Function call
    call_args = []
    param_names = list(sig.parameters.keys())
    for i, arg in enumerate(args):
        if i < len(param_names):
            call_args.append(f"{param_names[i]}={repr(arg)}")
    for key, value in kwargs.items():
        call_args.append(f"{key}={repr(value)}")

    function_call = f"{func.__name__}({', '.join(call_args)})"
    prompt_parts.append(f"Called with: {function_call}")
    logger.debug(f"Function call: {function_call}")

    # Docstring
    if use_docstring and func.__doc__:
        prompt_parts.append(f"Docstring:\n{func.__doc__}")
        logger.debug(f"Including docstring for {func.__name__}")

    # Source code
    if use_code:
        try:
            source = inspect.getsource(func)
            prompt_parts.append(f"Source code:\n{source}")
            logger.debug(f"Including source code for {func.__name__}")
        except (OSError, TypeError):
            logger.warning(f"Could not retrieve source code for {func.__name__}")
            # Source not available

    # Examples
    if use_examples and examples:
        examples_text = "Examples:\n"
        for example in examples:
            if "input" in example and "output" in example:
                examples_text += f"Input: {example['input']}\nOutput: {example['output']}\n\n"
        prompt_parts.append(examples_text.strip())
        logger.debug(f"Including {len(examples)} examples for {func.__name__}")

    prompt = "\n\n".join(prompt_parts)
    logger.debug(f"Generated prompt length: {len(prompt)} characters")
    return prompt


def default_mock_response_parser(
    response_str: Union[str, list], func: Callable, args: tuple, kwargs: dict
) -> Any:
    """Parse the LLM response into a Python object.

    Args:
        response_str: The raw response from the LLM
        func: The function being mocked
        args: Positional arguments passed to the function
        kwargs: Keyword arguments passed to the function

    Returns:
        The parsed response as a Python object
    """
    logger.debug(f"Parsing mock response for {func.__name__}")
    # Ensure we have a string to work with
    if isinstance(response_str, list):
        response_str = str(response_str)
    elif not isinstance(response_str, str):
        response_str = str(response_str)

    response_str = response_str.removeprefix("```python").removesuffix("```")

    # Default parsing: try to parse as Python literal
    try:
        result = ast.literal_eval(response_str)
        logger.debug(f"Successfully parsed mock response for {func.__name__}: {type(result).__name__}")
        return result
    except (ValueError, SyntaxError) as e:
        logger.warning(f"Failed to parse mock response for {func.__name__} as literal: {e}")
        # If parsing fails, return as string
        result = response_str.strip("\"'")
        logger.debug(f"Returning mock response as string for {func.__name__}")
        return result


def generate_mock_response(
    func: Callable,
    args: tuple,
    kwargs: dict,
    llm: BaseChatModel,
    use_docstring: bool,
    use_code: bool,
    use_examples: bool,
    examples: Optional[List[Dict[str, Any]]],
    parser: Callable[[Union[str, list], Callable, tuple, dict], Any],
) -> Any:
    """Generate a mock response for the given function call.

    Args:
        func: The function to mock
        args: Positional arguments passed to the function
        kwargs: Keyword arguments passed to the function
        llm: The language model to use for generation
        use_docstring: Whether to include the function's docstring
        use_code: Whether to include the function's source code
        use_examples: Whether to include examples
        examples: List of example input/output pairs
        parser: Function to parse the LLM response

    Returns:
        The generated mock response

    Raises:
        Exception: If LLM invocation or response parsing fails
    """
    logger.info(f"Generating mock response for {func.__name__}")

    prompt = generate_prompt(func, args, kwargs, use_docstring, use_code, use_examples, examples)

    # Call the LLM to generate a mock response
    logger.debug(f"Invoking LLM for {func.__name__}")
    try:
        response = llm.invoke(prompt)
        response_str = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"LLM response received for {func.__name__}, length: {len(response_str)}")
    except Exception as e:
        logger.error(f"LLM invocation failed for {func.__name__}: {e}")
        raise

    try:
        result = parser(response_str, func, args, kwargs)
        logger.info(f"Successfully generated mock response for {func.__name__}")
        return result
    except Exception as e:
        logger.error(f"Failed to parse mock response for {func.__name__}: {e}")
        raise



def get_mock_decorator(
    llm: BaseChatModel,
    enabled: bool = False,
    use_docstring: bool = True,
    use_code: bool = False,
    use_examples: bool = True,
    parser: Callable[[Union[str, list], Callable, tuple, dict], Any] = default_mock_response_parser,
) -> Callable:
    """Create a mock decorator function.

    Args:
        llm: The language model to use for generation
        enabled: Whether mocking is enabled by default
        use_docstring: Whether to include function docstrings by default
        use_code: Whether to include source code by default
        use_examples: Whether to include examples by default
        parser: Default parser function for LLM responses

    Returns:
        A mock decorator function
    """

    def mock(
        _func: Optional[Callable] = None,
        *,
        enabled: bool = enabled,
        llm: BaseChatModel = llm,
        use_docstring: bool = use_docstring,
        use_code: bool = use_code,
        use_examples: bool = use_examples,
        parser: Callable[[Union[str, list], Callable, tuple, dict], Any] = parser,
        examples: Optional[List[Dict[str, Any]]] = None,
    ):
        """Mock decorator that can be used with or without parameters.

        Args:
            _func: The function to decorate (when used without parentheses)
            enabled: Whether mocking is enabled for this function
            llm: The language model to use
            use_docstring: Whether to include the function's docstring
            use_code: Whether to include the function's source code
            use_examples: Whether to include examples
            parser: Function to parse the LLM response
            examples: List of example input/output pairs

        Returns:
            The decorated function or decorator
        """
        def decorator(func: Callable):
            if not enabled:
                logger.debug(f"Mock decorator disabled for {func.__name__}, using original function")
                return func

            logger.info(f"Mock decorator enabled for {func.__name__}")

            @wraps(func)
            def wrapper(*args: tuple, **kwargs: dict) -> Any:
                logger.debug(f"Mock wrapper called for {func.__name__}")
                return generate_mock_response(
                    func, args, kwargs, llm, use_docstring, use_code, use_examples, examples, parser
                )

            # Add attributes to track the original function and mock status
            setattr(wrapper, "_original_func", func)
            setattr(wrapper, "_is_mock", True)

            return wrapper

        if _func is None:
            return decorator
        else:
            return decorator(_func)

    return mock


__all__ = [
    "get_mock_decorator",
    "generate_mock_response",
    "generate_prompt",
    "default_mock_response_parser",
]
