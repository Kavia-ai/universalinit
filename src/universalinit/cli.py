import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any

from universalinit.templateconfig import TemplateInitInfo
from universalinit.universalinit import ProjectConfig, ProjectType, ProjectInitializer


def parse_parameters(params_str: str) -> Dict[str, Any]:
    if not params_str:
        return {}

    params = {}
    for param in params_str.split(','):
        if '=' not in param:
            continue
        key, value = param.split('=', 1)
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit() and value.count('.') == 1:
            value = float(value)
        params[key.strip()] = value
    return params


def create_project_config(args) -> ProjectConfig:
    """Create ProjectConfig from CLI arguments."""
    return ProjectConfig(
        name=args.name,
        version=args.version,
        description=args.description,
        author=args.author,
        project_type=ProjectType.from_string(args.type),
        output_path=Path(args.output),
        parameters=parse_parameters(args.parameters)
    )

def make_path_absolute(path: str, base_path: Path) -> str:
    """Convert a relative path to absolute path."""
    return str(base_path / path)

def template_init_info_to_dict(init_info: TemplateInitInfo, project_path: Path) -> dict:
    """Convert TemplateInitInfo to a dictionary with absolute paths for JSON serialization."""

    return {
        "build_cmd": {
            "command": init_info.build_cmd.command,
            "working_directory": init_info.build_cmd.working_directory
        },
        "env_config": {
            "environment_initialized": init_info.env_config.environment_initialized,
            "node_version": init_info.env_config.node_version,
            "npm_version": init_info.env_config.npm_version
        },
        "init_files": [make_path_absolute(f, project_path) for f in init_info.init_files],
        "init_minimal": init_info.init_minimal,
        "run_tool": {
            "command": init_info.run_tool.command,
            "working_directory": init_info.run_tool.working_directory
        },
        "test_tool": {
            "command": init_info.test_tool.command,
            "working_directory": init_info.test_tool.working_directory
        },
        "init_style": init_info.init_style,
        "linter_script": init_info.linter_script,
        "pre_processing": {
            "script": init_info.pre_processing.script
        },
        "post_processing": {
            "script": init_info.post_processing.script
        }
    }

def output_json(success: bool, message: str, template_info: TemplateInitInfo = None, project_path: Path = None):
    """Helper function to format JSON output."""
    result = {
        "success": success,
        "message": message,
        "template_config": template_init_info_to_dict(template_info, project_path) if template_info and project_path else {}
    }
    print("[OUTPUT]")
    print(json.dumps(result, indent=2))
    return 0 if success else 1

def main():
    parser = argparse.ArgumentParser(
        description='Universal Project Initializer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  uniinit --name my-app --type react --author "Kavia" --output ./my-react-app --parameters typescript=true,styling_solution=styled-components
  uniinit --name myservice --type python --author "Kavia" --output ./myservice --parameters async=true,use_fastapi=true
  uniinit --name my-vue-app --type vue --author "Kavia" --output ./my-vue-app
  uniinit --name my-flutter-app --type flutter --author "Kavia" --output ./my-flutter-app
  uniinit --name my-android-app --type android --author "Kavia" --output ./my-android-app --parameters min_sdk=24,target_sdk=34,gradle_version=8.12
  uniinit --name my-astro-site --type astro --author "Kavia" --output ./my-astro-site --parameters typescript=true
  uniinit --name my-django-site --type django --author "Kavia" --output ./my-django-site
  uniinit --name my-express-site --type express --author "Kavia" --output ./my-express-site --parameters typescript=true
  uniinit --name my-fastapi-site --type fastapi --author "Kavia" --output ./my-fastapi-site
  uniinit --name my-flask-site --type flask --author "Kavia" --output ./my-flask-site
  uniinit --name my-vite-app --type vite --author "Kavia" --output ./my-vite-app --parameters typescript=true
  uniinit --name my-nextjs-app --type nextjs --author "Kavia" --output ./my-nextjs-app
  uniinit --name my-nuxt-app --type nuxt --author "Kavia" --output ./my-nuxt-app
  uniinit --name my-ns-app --type nativescript --author "Kavia" --output ./my-ns-app --parameters typescript=true
  uniinit --name my-slides --type slidev --author "Kavia" --output ./my-slides
  uniinit --name my-svelte-app --type svelte --author "Kavia" --output ./my-svelte-app
  uniinit --name my-remix-app --type remix --author "Kavia" --output ./my-remix-app --parameters typescript=true,styling_solution=tailwind
  uniinit --name my-ts-app --type typescript --author "Kavia" --output ./my-ts-app
  uniinit --name my-remotion-app --type remotion --author "Kavia" --output ./my-remotion-app
  uniinit --name my-angular-app --type angular --author "Kavia" --output ./my-angular-app
  uniinit --name my-qwik-app --type qwik --author "Kavia" --output ./my-qwik-app


Available project types:
  - android
  - angular
  - astro
  - django
  - express
  - fastapi
  - flask
  - flutter
  - ios
  - nativescript
  - nextjs
  - node
  - nuxt
  - python
  - qwik
  - react
  - remix
  - remotion
  - slidev
  - svelte
  - typescript
  - vite
  - vue
    """
)

    parser.add_argument('--name', required=True, help='Project name')
    parser.add_argument('--version', default='0.1.0', help='Project version (default: 0.1.0)')
    parser.add_argument('--description', default='', help='Project description')
    parser.add_argument('--author', required=True, help='Project author')
    parser.add_argument('--type', required=True, help='Project type (react, ios, android, python, node)')
    parser.add_argument('--output', required=True, help='Output directory path')
    parser.add_argument('--parameters', help='Additional parameters as key=value pairs, comma-separated')
    parser.add_argument('--config', help='Path to JSON config file (overrides other arguments)')

    args = parser.parse_args()

    initializer = ProjectInitializer()

    try:
        config = create_project_config(args)

        template = initializer.template_factory.create_template(config)
        init_info = template.get_init_info()

        print(f"\nInitializing {config.project_type.value} project: {config.name}")
        print(f"Output directory: {config.output_path}")
        print("\nTemplate configuration:")
        print(f"Build command: {init_info.build_cmd.command}")
        print(f"Required environment:")
        if hasattr(init_info.env_config, 'node_version'):
            print(f"  Node.js: {init_info.env_config.node_version}")
        if hasattr(init_info.env_config, 'npm_version'):
            print(f"  npm: {init_info.env_config.npm_version}")

        success = initializer.initialize_project(config)

        if success:
            return output_json(True, "Project initialized successfully!", init_info, config.output_path)
        else:
            return output_json(False, "Project initialization failed", init_info, config.output_path)

    except Exception as e:
        return output_json(False, f"Error: {str(e)}")

if __name__ == '__main__':
    main()