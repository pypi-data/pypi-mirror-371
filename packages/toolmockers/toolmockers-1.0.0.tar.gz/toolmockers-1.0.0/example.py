"""
Example usage of the toolmockers library.

This demonstrates how to use LLM-powered mocking for various types of functions
during development and testing.
"""

import logging
from os import getenv
from langchain.chat_models import init_chat_model
from toolmockers import get_mock_decorator

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

# Instantiate a chat model
llm = init_chat_model(
    "openai:gpt-5-chat-latest",
    api_key=getenv("OPENAI_API_KEY"),
    use_responses_api=True,
    store=False,
)

# Create a mock decorator with default settings
mock = get_mock_decorator(
    llm=llm,
    enabled=getenv("USE_MOCKS") == "true",
    use_docstring=True,  # Include function docstrings in prompts
    use_code=False,      # Don't include source code by default
    use_examples=True    # Include examples when provided
)


@mock
def add(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b


@mock(use_code=True)  # Override to include source code for this function
def fetch_user_data(user_id: str) -> dict:
    """Fetch user data from a database.

    Args:
        user_id: The unique identifier for the user

    Returns:
        A dictionary containing user information
    """
    # Simulate database call
    import time

    time.sleep(2)  # Simulate network delay
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


@mock(
    examples=[
        {
            "input": "analyze_sentiment('I love this product!')",
            "output": {"sentiment": "positive", "confidence": 0.95},
        },
        {
            "input": "analyze_sentiment('This is terrible')",
            "output": {"sentiment": "negative", "confidence": 0.89},
        },
    ]
)
def analyze_sentiment(text: str) -> dict:
    """Analyze the sentiment of the given text.

    Args:
        text: The text to analyze

    Returns:
        A dictionary with sentiment and confidence score
    """
    # Simulate ML model call
    import random

    sentiments = ["positive", "negative", "neutral"]
    return {"sentiment": random.choice(sentiments), "confidence": random.random()}


@mock(enabled=False)  # This function will never be mocked
def critical_function(data: str) -> str:
    """A critical function that should never be mocked."""
    return f"CRITICAL: {data}"


if __name__ == "__main__":
    print("=== ToolMockers Example ===")
    print(f"Mocking enabled: {getenv('USE_MOCKS') == 'true'}")

    # These calls will use the original functions since mocking is disabled

    print("1. Simple math function:")
    result = add(5, 3)
    print(f"add(5, 3) = {result}")
    print()

    print("2. Database function (with source code context):")
    user = fetch_user_data("user123")
    print(f"fetch_user_data('user123') = {user}")
    print()

    print("3. ML function (with examples):")
    sentiment = analyze_sentiment("I'm feeling great today!")
    print(f"analyze_sentiment('I'm feeling great today!') = {sentiment}")
    print()

    print("4. Critical function (never mocked):")
    result = critical_function("important data")
    print(f"critical_function('important data') = {result}")
    print()

    print("=== Introspection ===")
    print(f"add is mocked: {hasattr(add, '_is_mock')}")
    print(f"fetch_user_data is mocked: {hasattr(fetch_user_data, '_is_mock')}")
    print(f"critical_function is mocked: {hasattr(critical_function, '_is_mock')}")
