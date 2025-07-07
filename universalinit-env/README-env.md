# UniversalInit Environment Package

A Python package for mapping environment variables between different frameworks and a common format.

## Features

- Map environment variables from framework-specific formats to a common format
- Map environment variables from common format to framework-specific formats
- Support for multiple frameworks through template files
- Easy extensibility for new frameworks

## Installation

```bash
pip install universalinit-env
```

## Usage

### Basic Usage

```python
from universalinit_env import map_framework_to_common, map_common_to_framework

# Map React-specific env vars to common format
react_env = {
    "REACT_APP_SUPABASE_URL": "https://example.supabase.co",
    "REACT_APP_API_KEY": "your-api-key",
    "REACT_APP_DATABASE_URL": "postgresql://..."
}

common_env = map_framework_to_common("react", react_env)
# Result: {"SUPABASE_URL": "https://example.supabase.co", ...}

# Map common env vars to React format
framework_env = map_common_to_framework("react", common_env)
# Result: {"REACT_APP_SUPABASE_URL": "https://example.supabase.co", ...}
```

### Available Functions

- `get_template_path(framework)`: Get the path to the environment template file for a given framework
- `parse_template_file(template_path)`: Parse a template file and extract the mapping
- `map_common_to_framework(framework, common_env)`: Map common environment variables to framework-specific ones
- `map_framework_to_common(framework, framework_env)`: Map framework-specific environment variables to common ones
- `get_supported_frameworks()`: Get a list of supported frameworks

### Supported Frameworks

Currently supports:
- React (via `react/env.template`)

### Adding New Frameworks

To add support for a new framework:

1. Create a new directory under `src/universalinit_env/` with your framework name
2. Add an `env.template` file with mappings in the format:
   ```
   FRAMEWORK_VAR = COMMON_VAR
   ```
3. The framework will automatically be detected and available

## Development

```bash
# Install dependencies
poetry install

# Run tests
pytest
```

## License

Same license as the main UniversalInit project. 