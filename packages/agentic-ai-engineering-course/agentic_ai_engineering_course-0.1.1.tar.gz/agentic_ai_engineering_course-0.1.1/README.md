# Course AI Agents Utils

A collection of utility functions for AI agents development, extracted from the AI Agents course by Towards AI and Decoding ML.

## Installation

```bash
pip install course-ai-agents-utils
```

## Usage

### Environment Utilities

```python
from lessons.utils import load

# Load environment variables from .env file
load()

# Load with custom path and required variables
load(dotenv_path="path/to/.env", required_env_vars=["API_KEY", "SECRET"])
```

### Pretty Print Utilities

```python
from lessons.utils import wrapped, function_call, Color

# Pretty print text with custom formatting
wrapped("Hello World", title="My Message", header_color=Color.BLUE)

# Pretty print function calls
function_call(
    function_call=my_function_call,
    title="Function Execution",
    header_color=Color.GREEN
)
```

## Development

This package is part of the AI Agents course materials. For the full course experience, visit the main repository.

## License

Apache License 2.0 - see LICENSE file for details.