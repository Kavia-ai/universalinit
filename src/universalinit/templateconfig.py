from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class ProjectType(Enum):
    """Supported project types."""
    REACT = "react"
    IOS = "ios"
    ANDROID = "android"
    PYTHON = "python"
    NODE = "node"

    @classmethod
    def from_string(cls, value: str) -> 'ProjectType':
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unsupported project type: {value}")

@dataclass
class ProjectConfig:
    """Configuration for project initialization."""
    name: str
    version: str
    description: str
    author: str
    project_type: ProjectType
    output_path: Path
    parameters: Dict[str, Any]

    def get_replaceable_parameters(self) -> Dict[str, str]:
        """Get dictionary of replaceable parameters."""
        replacements = {
            'KAVIA_TEMPLATE_PROJECT_NAME': self.name,
            'KAVIA_PROJECT_DESCRIPTION': self.description,
            'KAVIA_PROJECT_AUTHOR': self.author,
            'KAVIA_PROJECT_VERSION': self.version,
            'KAVIA_USE_TYPESCRIPT': str(self.parameters.get('typescript', False)).lower(),
            'KAVIA_STYLING_SOLUTION': self.parameters.get('styling_solution', 'css'),
            'KAVIA_PROJECT_DIRECTORY': str(self.output_path)
        }
        return replacements

    def replace_parameters(self, content: str) -> str:
        """Replace parameters in content."""
        replacements = self.get_replaceable_parameters()
        for key, value in replacements.items():
            content = content.replace(f"${key}", value)
            content = content.replace(f"{{{key}}}", value)
        return content


@dataclass
class PostProcessing:
    """Post processing configuration."""
    script: str

@dataclass
class BuildCommand:
    """Build command configuration."""
    command: str
    working_directory: str

@dataclass
class EnvironmentConfig:
    """Environment configuration."""
    environment_initialized: bool
    node_version: str
    npm_version: str

@dataclass
class RunTool:
    """Run tool configuration."""
    command: str
    working_directory: str

@dataclass
class TestTool:
    """Test tool configuration."""
    command: str
    working_directory: str

@dataclass
class TemplateInitInfo:
    """Complete template initialization information."""
    build_cmd: BuildCommand
    env_config: EnvironmentConfig
    init_files: List[str]
    init_minimal: str
    run_tool: RunTool
    test_tool: TestTool
    init_style: str
    linter_script: str
    post_processing: PostProcessing


class TemplateConfigProvider:
    """Provides template initialization configuration."""
    def __init__(self, template_path: Path, config: ProjectConfig):
        self.template_path = template_path
        self.config_path = template_path / "config.yml"
        self.project_config = config

    def get_init_info(self) -> TemplateInitInfo:
        """Get template initialization information."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")

        with open(self.config_path, 'r') as f:
            data = f.read()
            data = self.project_config.replace_parameters(data)

            config_data = yaml.safe_load(data)

        return TemplateInitInfo(
            build_cmd=BuildCommand(
                command=config_data['build_cmd']['command'],
                working_directory=config_data['build_cmd']['working_directory']
            ),
            env_config=EnvironmentConfig(
                environment_initialized=config_data['env']['environment_initialized'],
                node_version=config_data['env']['node_version'],
                npm_version=config_data['env']['npm_version']
            ),
            init_files=config_data.get('init_files', []),
            init_minimal=config_data['init_minimal'],
            run_tool=RunTool(
                command=config_data['run_tool']['command'],
                working_directory=config_data['run_tool']['working_directory']
            ),
            test_tool=TestTool(
                command=config_data['test_tool']['command'],
                working_directory=config_data['test_tool']['working_directory']
            ),
            init_style=config_data.get('init_style', ''),
            linter_script=config_data['linter']['script_content'],
            post_processing=PostProcessing(
                script=config_data.get('post_processing', {}).get('script', '')
            )
        )