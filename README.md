# Universal Initializer

A versatile tool for initializing software projects from templates. Create React, Python, C++, Node.js, iOS, Android, and more projects with a single command.

## Features

- Configurable template-based project creation
- Support for multiple project types (React, Vue, Flutter, and many more)
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

- `android`: Android application
- `angular`: Angular application
- `astro`: Astro website
- `flutter`: Flutter application
- `nativescript`: NativeScript application
- `nextjs`: Next.js application
- `nuxt`: Nuxt.js application
- `qwik`: Qwik application
- `react`: React application
- `remix`: Remix application
- `remotion`: Remotion video project
- `slidev`: Slidev presentation
- `svelte`: Svelte application
- `typescript`: TypeScript application
- `vite`: Vite application
- `vue`: Vue application
- `fastapi`: FastAPI backend
- `django`: Django backend

### Parameter Examples

#### React Project
```bash
uniinit --name my-react-app --type react --output ./my-react-app --author "Your Name" --parameters typescript=true,styling_solution=styled-components
```

#### Vue Project
```bash
uniinit --name myservice --type vue --output ./myservice --author "Your Name"
```

#### Flutter Project
```bash
uniinit --name my-flutter-app --type flutter --output ./my-flutter-app --author "Your Name"
```

#### Android Project
```bash
uniinit --name my-android-app --type android --output ./my-android-app --author "Your Name" --parameters min_sdk=24,target_sdk=34,gradle_version=8.12
```

#### Astro Project
```bash
uniinit --name my-astro-site --type astro --output ./my-astro-site --author "Your Name" --parameters typescript=true
```

#### Next.js Project
```bash
uniinit --name my-nextjs-app --type nextjs --output ./my-nextjs-app --author "Your Name" --parameters typescript=true,styling_solution=tailwind
```

#### Nuxt Project
```bash
uniinit --name my-nuxt-app --type nuxt --output ./my-nuxt-app --author "Your Name"
```

#### NativeScript Project
```bash
uniinit --name my-ns-app --type nativescript --output ./my-ns-app --author "Your Name" --parameters typescript=true
```

#### Slidev Project
```bash
uniinit --name my-slides --type slidev --output ./my-slides --author "Your Name"
```

#### Svelte Project
```bash
uniinit --name my-svelte-app --type svelte --output ./my-svelte-app --author "Your Name" --parameters typescript=true,styling_solution=css
```

#### Remix Project
```bash
uniinit --name my-remix-app --type remix --output ./my-remix-app --author "Your Name" --parameters typescript=true,styling_solution=tailwind
```

#### TypeScript Project
```bash
uniinit --name my-ts-app --type typescript --output ./my-ts-app --author "Your Name"
```

#### Remotion Project
```bash
uniinit --name my-remotion-app --type remotion --output ./my-remotion-app --author "Your Name"
```

#### Angular Project
```bash
uniinit --name my-angular-app --type angular --output ./my-angular-app --author "Your Name"
```

#### Qwik Project
```bash
uniinit --name my-qwik-app --type qwik --output ./my-qwik-app --author "Your Name"
```

#### Vite Project
```bash
uniinit --name my-vite-app --type vite --output ./my-vite-app --author "Your Name" --parameters typescript=true,framework=react
```

#### FastAPI Project
```bash
uniinit --name my-fastapi-app --type fastapi --output ./my-fastapi-app --author "Your Name"
```

#### Django Project
```bash
uniinit --name my-django-app --type django --output ./my-django-app --author "Your Name"
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
4. Add new replaceable parameters if necessary in the function `ProjectConfig.get_replaceable_parameters` in `src/universalinit/templateconfig.py`
5. Add new environment parameters if necessary in the function `TemplateConfigProvider.get_init_info` in `src/universalinit/templateconfig.py`
6. Add new template at `TEMPLATE_MAP` in `src/universalinit/templates.py`
7. Register the template class in the `ProjectInitializer` constructor in `src/universalinit/universalinit.py`
8. Create a new template class in `src/universalinit/universalinit.py`
9. Update the epilog in `main` in `src/universalinit/cli.py`
