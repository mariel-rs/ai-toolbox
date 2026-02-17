"""Example tests for ai_toolbox."""

from ai_toolbox import example_function


def test_example_function():
    """Test the example function."""
    result = example_function()
    assert result == "Hello from ai_toolbox!"
    assert isinstance(result, str)
