# AGENTS.md

## Docstring Rules (Derived from pyproject.toml)

Agents should generate docstrings in the following Google format:

```python
def function_name(param1: TYPE, param2: TYPE) -> RETURN_TYPE:
    """
    Write a short, imperative-mood summary.

    Args:
        param1 (TYPE): Description.
        param2 (TYPE): Description.

    Returns:
        RETURN_TYPE: Description.
    """