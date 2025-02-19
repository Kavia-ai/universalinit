import argparse
import json
from pathlib import Path
from typing import Dict, Any

from universalinit import (
    ProjectInitializer,
    ProjectConfig,
    ProjectType
)


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


def main():
    parser = argparse.ArgumentParser(
        description='Universal Project Initializer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  uniinit --name my-app --type react --output ./my-app --parameters typescript=true,styling_solution=styled-components
  uniinit --name myservice --type python --output ./myservice --parameters async=true,use_fastapi=true

Available project types:
  - react
  - ios
  - android
  - python
  - node
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
        if args.config:
            config = ProjectInitializer.load_config(Path(args.config))
        else:
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
            print("\n✅ Project initialized successfully!")
            print(f"\nNext steps:")
            print(f"1. cd {config.output_path}")
            if init_info.build_cmd.command:
                print(f"2. {init_info.build_cmd.command}")
            if init_info.run_tool.command:
                print(f"3. {init_info.run_tool.command}")
        else:
            print("\n❌ Project initialization failed")
            exit(1)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()