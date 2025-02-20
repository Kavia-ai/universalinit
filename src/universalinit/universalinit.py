import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from .templateconfig import TemplateConfigProvider, TemplateInitInfo, ProjectType, ProjectConfig


class TemplateProvider:
    """Manages template locations and access."""

    def __init__(self, base_template_path: Optional[Path] = None):
        if base_template_path is None:
            # Default to a 'templates' directory in the package
            self.base_path = Path(__file__).parent / "templates"
        else:
            self.base_path = base_template_path

    def get_template_path(self, project_type: ProjectType) -> Path:
        """Get the template path for a specific project type."""
        template_path = self.base_path / project_type.value
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found for {project_type.value}")
        return template_path


class ProjectTemplate(ABC):
    """Base class for project templates."""

    def __init__(self, config: ProjectConfig, template_provider: TemplateProvider):
        self.config = config
        self.template_provider = template_provider
        self.template_path = template_provider.get_template_path(config.project_type)
        self.config_provider = TemplateConfigProvider(self.template_path, self.config)

    @abstractmethod
    def validate_parameters(self) -> bool:
        """Validate the project parameters."""
        pass

    def get_init_info(self) -> TemplateInitInfo:
        """Get template initialization information."""
        return self.config_provider.get_init_info()

    @abstractmethod
    def generate_structure(self) -> None:
        """Generate the project structure."""
        pass

    @abstractmethod
    def setup_testing(self) -> None:
        """Setup testing infrastructure."""
        pass

    def initialize(self) -> bool:
        """Initialize the project."""
        try:
            if not self.validate_parameters():
                raise ValueError("Invalid project parameters")

            self.generate_structure()
            self.setup_testing()
            self.run_post_processing()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to initialize project: {str(e)}")
            return False

    def run_post_processing(self) -> None:
        """Run post-processing script if available."""
        init_info = self.get_init_info()
        if init_info.post_processing and init_info.post_processing.script:
            script_content = init_info.post_processing.script

            # Create a temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_file:
                temp_file.write(script_content)
                temp_file.flush()
                script_path = temp_file.name

            try:
                os.chmod(script_path, 0o755)

                result = subprocess.run(
                    [script_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.stderr:
                    print(f"Post-processing errors:\n{result.stderr}")

            except subprocess.CalledProcessError as e:
                print(f"Post-processing failed with exit code {e.returncode}")
                print(f"Error output:\n{e.stderr}")
                raise
            finally:
                # Clean up the temporary script file
                Path(script_path).unlink()


class ProjectTemplateFactory:
    """Factory for creating project templates."""

    def __init__(self):
        self._template_classes: Dict[ProjectType, type[ProjectTemplate]] = {}
        self.template_provider = TemplateProvider()

    def register_template(self, project_type: ProjectType,
                          template_class: type[ProjectTemplate]) -> None:
        """Register a new template class for a project type."""
        self._template_classes[project_type] = template_class

    def create_template(self, config: ProjectConfig) -> ProjectTemplate:
        """Create a template instance for the specified project type."""
        template_class = self._template_classes.get(config.project_type)
        if not template_class:
            raise ValueError(f"---> No template registered for {config.project_type.value}")
        return template_class(config, self.template_provider)


class ProjectInitializer:
    """Main project initialization orchestrator."""

    def __init__(self):
        self.template_factory = ProjectTemplateFactory()
        self.template_factory.register_template(ProjectType.REACT, ReactTemplate)

    def initialize_project(self, config: ProjectConfig) -> bool:
        """Initialize a project using the appropriate template."""
        template = self.template_factory.create_template(config)
        return template.initialize()

    @staticmethod
    def load_config(config_path: Path) -> ProjectConfig:
        """Load project configuration from a JSON file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return ProjectConfig(
                name=config_data['name'],
                version=config_data['version'],
                description=config_data['description'],
                author=config_data['author'],
                project_type=ProjectType.from_string(config_data['project_type']),
                output_path=Path(config_data['output_path']),
                parameters=config_data.get('parameters', {})
            )


# Example implementation for React projects
class ReactTemplate(ProjectTemplate):
    """Template implementation for React projects."""

    def validate_parameters(self) -> bool:
        required_params = {'typescript', 'styling_solution'}
        return all(param in self.config.parameters for param in required_params)

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # Setup Jest and React Testing Library
        test_setup_path = self.template_path / "test-setup"
        if test_setup_path.exists():
            FileSystemHelper.copy_template(
                test_setup_path,
                self.config.output_path / "test",
                {'{KAVIA_TEMPLATE_PROJECT_NAME}': self.config.name}
            )


class FileSystemHelper:
    """Helper class for file system operations."""

    @staticmethod
    def copy_template(src: Path, dst: Path, replacements: Dict[str, str]) -> None:
        """Copy template files with variable replacement."""
        if not src.exists():
            raise FileNotFoundError(f"Template path {src} does not exist")

        if not dst.exists():
            dst.mkdir(parents=True)

        # Define files to exclude
        excluded_files = {'config.yml'}  # Add config.yml to exclusions

        for item in src.rglob("*"):
            # Skip excluded files, hidden files, and python special files
            if (item.name in excluded_files or
                    item.name.startswith('.') or
                    item.name.startswith('__')):
                continue

            relative_path = item.relative_to(src)
            destination = dst / relative_path

            if item.is_dir():
                destination.mkdir(exist_ok=True)
            else:

                # Handle variable replacement in file names
                dest_path_str = str(destination)
                for key, value in replacements.items():
                    dest_path_str = dest_path_str.replace(f"${key}", value)
                destination = Path(dest_path_str)

                destination.parent.mkdir(parents=True, exist_ok=True)

                try:
                    content = item.read_text()
                    for key, value in replacements.items():
                        content = content.replace(f"${key}", value)
                        content = content.replace(f"{{{key}}}", value)
                    destination.write_text(content)
                except UnicodeDecodeError:
                    # Just copy the file as is if it can't be decoded as text
                    destination.write_bytes(item.read_bytes())


def main():
    initializer = ProjectInitializer()

    # Register templates
    factory = initializer.template_factory
    config = ProjectConfig(
        name="my-react-app",
        version="1.0.0",
        description="A new React application",
        author="John Doe",
        project_type=ProjectType.REACT,
        output_path=Path("./output"),
        parameters={
            "typescript": True,
            "styling_solution": "styled-components"
        }
    )

    template = factory.create_template(config)
    init_info = template.get_init_info()

    # Print out the initialization configuration
    print("\nTemplate Initialization Configuration:")
    print(f"Build Command: {init_info.build_cmd.command}")
    print(f"Working Directory: {init_info.build_cmd.working_directory}")
    print(f"\nEnvironment:")
    print(f"Node Version: {init_info.env_config.node_version}")
    print(f"NPM Version: {init_info.env_config.npm_version}")
    print(f"\nInit Minimal: {init_info.init_minimal}")
    print(f"\nRun Tool Command: {init_info.run_tool.command}")
    print(f"Test Tool Command: {init_info.test_tool.command}")

    success = initializer.initialize_project(config)
    print(f"\nProject initialization {'successful' if success else 'failed'}")


if __name__ == "__main__":
    main()
