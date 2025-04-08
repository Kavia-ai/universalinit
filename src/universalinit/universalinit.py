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

            self.run_pre_processing()
            self.generate_structure()
            self.setup_testing()
            self.run_post_processing()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to initialize project: {str(e)}")
            return False

    def run_pre_processing(self) -> None:
        """Run pre-processing script if available."""
        init_info = self.get_init_info()
        if init_info.pre_processing and init_info.pre_processing.script:
            self._run_processing_script(init_info.pre_processing.script, "Pre-processing")

    def run_post_processing(self) -> None:
        """Run post-processing script if available."""
        init_info = self.get_init_info()
        if init_info.post_processing and init_info.post_processing.script:
            self._run_processing_script(init_info.post_processing.script, "Post-processing")

    def _run_processing_script(self, script_content: str, process_type: str) -> None:
        """Run a processing script with the given content.
        
        Args:
            script_content: The content of the script to run
            process_type: The type of processing ("Pre-processing" or "Post-processing")
        """
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
                print(f"{process_type} errors:\n{result.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"{process_type} failed with exit code {e.returncode}")
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
        self.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
        self.template_factory.register_template(ProjectType.ANGULAR, AngularTemplate)
        self.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)
        self.template_factory.register_template(ProjectType.FLUTTER, FlutterTemplate)
        self.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)
        self.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)
        self.template_factory.register_template(ProjectType.NUXT, NuxtTemplate)
        self.template_factory.register_template(ProjectType.QWIK, QwikTemplate)
        self.template_factory.register_template(ProjectType.REACT, ReactTemplate)
        self.template_factory.register_template(ProjectType.REMIX, RemixTemplate)
        self.template_factory.register_template(ProjectType.REMOTION, RemotionTemplate)
        self.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)
        self.template_factory.register_template(ProjectType.SVELTE, SvelteTemplate)
        self.template_factory.register_template(ProjectType.TYPESCRIPT, TypeScriptTemplate)
        self.template_factory.register_template(ProjectType.VITE, ViteTemplate)
        self.template_factory.register_template(ProjectType.VUE, VueTemplate)

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


class AndroidTemplate(ProjectTemplate):
    """Template implementation for Android projects."""

    def validate_parameters(self) -> bool:
        # No required parameters for basic template, but we'll support optional ones
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Android projects may have hidden files
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class AngularTemplate(ProjectTemplate):
    """Template implementation for Angular projects."""

    def validate_parameters(self) -> bool:
        # Angular template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # Angular testing is already configured in the standard template
        pass


class AstroTemplate(ProjectTemplate):
    """Template implementation for Astro projects."""

    def validate_parameters(self) -> bool:
        # Define which parameters are allowed (not required)
        allowed_params = {'typescript', 'integration_tailwind', 'integration_react', 
                         'integration_vue', 'integration_svelte'}
        # If no parameters provided, that's fine
        if not self.config.parameters:
            return True
        # All provided parameters should be in the allowed list
        return all(param in allowed_params for param in self.config.parameters.keys())

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include hidden files like .gitignore
        )

    def setup_testing(self) -> None:
        # Astro testing is already configured in the standard template
        pass


class FlutterTemplate(ProjectTemplate):
    """Template implementation for Flutter projects."""

    def validate_parameters(self) -> bool:
        # Flutter has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True # Flutter relies on hidden files
        )

    def setup_testing(self) -> None:
        # Flutter testing is already configured in the standard template
        pass


class NativeScriptTemplate(ProjectTemplate):
    """Template implementation for NativeScript projects."""

    def validate_parameters(self) -> bool:
        # No required parameters for the basic NativeScript template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # NativeScript uses hidden files
        )

    def setup_testing(self) -> None:
        # Testing configuration is included in the template
        pass


class NextJSTemplate(ProjectTemplate):
    """Template implementation for NextJS projects."""

    def validate_parameters(self) -> bool:
        # NextJS has similar configuration patterns as React
        required_params = {'typescript', 'styling_solution'}
        for param in required_params:
            if param not in self.config.parameters:
                self.config.parameters[param] = True if param == 'typescript' else 'css'
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Include .gitignore, .eslintrc, etc.
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the NextJS template
        pass


class NuxtTemplate(ProjectTemplate):
    """Template implementation for Nuxt projects."""

    def validate_parameters(self) -> bool:
        # Nuxt template has predetermined configurations, similar to Vue
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True

        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class QwikTemplate(ProjectTemplate):
    """Template implementation for Qwik projects."""

    def validate_parameters(self) -> bool:
        # Qwik template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Qwik may have important hidden files like .vscode
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


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


class RemixTemplate(ProjectTemplate):
    """Template implementation for Remix projects."""

    def validate_parameters(self) -> bool:
        # Required parameters for Remix projects
        required_params = {'typescript', 'styling_solution'}
        return all(param in self.config.parameters for param in required_params)

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()

        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements, 
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Setup testing for Remix if test-setup directory exists
        test_setup_path = self.template_path / "test-setup"
        if test_setup_path.exists():
            FileSystemHelper.copy_template(
                test_setup_path,
                self.config.output_path / "test",
                {'{KAVIA_TEMPLATE_PROJECT_NAME}': self.config.name}
            )


class RemotionTemplate(ProjectTemplate):
    """Template implementation for Remotion projects."""

    def validate_parameters(self) -> bool:
        # Remotion is TypeScript-based by default, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class SlidevTemplate(ProjectTemplate):
    """Template implementation for Slidev presentations."""

    def validate_parameters(self) -> bool:
        # Slidev has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True  # Slidev uses hidden files like .gitignore, netlify.toml, vercel.json
        )

    def setup_testing(self) -> None:
        # Slidev testing is configured through the package.json in the template
        pass


class SvelteTemplate(ProjectTemplate):
    """Template implementation for Svelte projects."""

    def validate_parameters(self) -> bool:
        # Svelte has simpler requirements, most configuration is in the template
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements,
            include_hidden=True
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class TypeScriptTemplate(ProjectTemplate):
    """Template implementation for TypeScript projects."""

    def validate_parameters(self) -> bool:
        # TypeScript has simpler requirements, module configurations can be optional
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # TypeScript testing is already configured in the template
        pass


class ViteTemplate(ProjectTemplate):
    """Template implementation for Vite projects."""

    def validate_parameters(self) -> bool:
        # Vite has no required parameters for basic setup
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # Testing is configured in the template
        pass


class VueTemplate(ProjectTemplate):
    """Template implementation for Vue projects."""

    def validate_parameters(self) -> bool:
        # Vue template has predetermined configurations, no required parameters
        return True

    def generate_structure(self) -> None:
        replacements = self.config.get_replaceable_parameters()
        FileSystemHelper.copy_template(
            self.template_path,
            self.config.output_path,
            replacements
        )

    def setup_testing(self) -> None:
        # Testing is already configured in the template
        pass


class FileSystemHelper:
    """Helper class for file system operations."""

    @staticmethod
    def copy_template(src: Path, dst: Path, replacements: Dict[str, str], include_hidden: bool = False) -> None:
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
                    item.name.startswith('__') and item.name.endswith('__')):
                continue
                
            if not include_hidden and item.name.startswith('.') and item.is_file():
                continue  # Skip hidden files but allow hidden directories

            relative_path = item.relative_to(src)
            destination = dst / relative_path

            if item.is_dir():
                destination.mkdir(exist_ok=True, parents=True)  # Added parents=True
            else:
                # Handle variable replacement in file names
                dest_path_str = str(destination)
                for key, value in replacements.items():
                    dest_path_str = dest_path_str.replace(f"${key}", str(value))
                destination = Path(dest_path_str)

                # Ensure parent directories exist
                destination.parent.mkdir(parents=True, exist_ok=True)

                try:
                    content = item.read_text()
                    for key, value in replacements.items():
                        content = content.replace(f"${key}", str(value))
                        content = content.replace(f"{{{key}}}", str(value))
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
