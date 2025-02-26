# Universal Initializer

A versatile tool for initializing software projects from templates. Create React, Python, C++, Node.js, iOS, Android, and more projects with a single command.

## Features

- Configurable template-based project creation
- Support for multiple project types (React, Vue)
- Parameter-based customization
- Variable replacement in template files
- Post-processing support for additional setup tasks
- JSON output for integration with other tools

## Installation

```bash
# Install with pip
pip install universalinit

# Or install directly from source
git clone https://github.com/Kavia-ai/universalinit.git
cd universalinit
pip install -e .
```

## Usage

Create a new project using the command-line interface:

```bash
uniinit --name my-app --type react --output ./my-app --author "Your Name" --parameters typescript=true,styling_solution=styled-components
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--author` | Project author (Required) | `--author "Your Name"` |
| `--config` | Path to JSON config file | `--config ./my-config.json` |
| `--description` | Project description | `--description "An awesome app"` |
| `--name` | Project name (Required) | `--name my-awesome-app` |
| `--output` | Output directory path (Required) | `--output ./my-app` |
| `--parameters` | Additional parameters as key=value pairs | `--parameters typescript=true,styling_solution=styled-components` |
| `--type` | Project type (Required) | `--type react` |
| `--version` | Project version | `--version 0.1.0` |

### Available Project Types

- `react`: React application
- `vue`: Vue application

### Parameter Examples

#### React Project
```bash
uniinit --name my-react-app --type react --output ./my-react-app --author "Your Name" --parameters typescript=true,styling_solution=styled-components
```

#### Vue Project
```bash
uniinit --name myservice --type vue --output ./myservice --author "Your Name"
```

## JSON Configuration

Instead of command-line parameters, you can use a JSON configuration file:

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "description": "My awesome application",
  "author": "Your Name",
  "project_type": "react",
  "output_path": "./my-app",
  "parameters": {
    "typescript": true,
    "styling_solution": "styled-components"
  }
}
```

Then use:
```bash
uniinit --config ./my-config.json
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest

# Run tests
pytest
```

### Adding New Templates

1. Create a new directory in `src/universalinit/templates/` for your template
2. Add a `config.yml` file with template configuration
3. Add new template type in `ProjectType` enum in `src/universalinit/templateconfig.py`
4. Add new replaceable parameters if necessary in the function `get_replaceable_parameters` in `src/universalinit/templateconfig.py`
4. Add new template at `TEMPLATE_MAP` in `src/universalinit/templates.py`
5. Register the template class in the `ProjectInitializer` constructor in `src/universalinit/universalinit.py`
6. Create a new template class in `src/universalinit/universalinit.py`
7. Update the epilog in `main` in `src/universalinit/cli.py`
