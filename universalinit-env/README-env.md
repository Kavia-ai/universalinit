# UniversalInit Environment Package

A Python package for mapping environment variables between different frameworks and a common format.

## Features

- Map environment variables from framework-specific formats to a common format
- Map environment variables from common format to framework-specific formats
- Support for multiple frameworks through YAML template files
- Easy extensibility for new frameworks
- Optional prefix support for bulk environment variable transformation

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
- `parse_template_file(template_path)`: Parse a YAML template file and extract the prefix and mapping
- `map_common_to_framework(framework, common_env)`: Map common environment variables to framework-specific ones
- `map_framework_to_common(framework, framework_env)`: Map framework-specific environment variables to common ones
- `get_supported_frameworks()`: Get a list of supported frameworks

### Supported Frameworks

Currently supports:
- React (via `react/env.template`)

### Template File Format

Environment template files use YAML syntax with the following structure:

```yaml
# Optional prefix that will be added to all environment variables
# prefix: REACT_APP_

# Direct mapping of environment variables
mapping:
  # Example: maps FOO environment variable to REACT_FOO in the React app
  REACT_FOO: FOO
  
  # Example: maps API_URL environment variable to REACT_API_URL in the React app
  REACT_API_URL: API_URL
  
  # Example: maps DATABASE_URL environment variable to REACT_DB_URL in the React app
  REACT_DB_URL: DATABASE_URL
```

#### Template Rules:

1. **Prefix (Optional)**: If specified, all unmapped environment variables will have this prefix added
2. **Direct Mapping**: Specific environment variable name transformations
3. **Fallback**: Any environment variable not matched by mapping rules preserves its original name

#### Mapping Priority:

1. Direct mappings in the `mapping` section are applied first
2. If a prefix is specified, it's applied to remaining unmapped variables
3. Any variables still unmapped are preserved as-is

### Adding New Frameworks

To add support for a new framework:

1. Create a new directory under `src/universalinit_env/` with your framework name
2. Add an `env.template` file with YAML mappings:
   ```yaml
   # Optional prefix
   prefix: FRAMEWORK_PREFIX_
   
   # Direct mappings
   mapping:
     FRAMEWORK_VAR: COMMON_VAR
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