from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class ProjectType(Enum):
    """Supported project types."""
    ANDROID = "android"
    ANGULAR = "angular"
    ASTRO = "astro"
    DJANGO = "django"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    FLASK = "flask"
    FLUTTER = "flutter"
    IOS = "ios"
    NATIVESCRIPT = "nativescript"
    NEXTJS = "nextjs"
    NODE = "node"
    NUXT = "nuxt"
    PYTHON = "python"
    QWIK = "qwik"
    REACT = "react"
    REMIX = "remix"
    REMOTION = "remotion"
    SLIDEV = "slidev"
    SVELTE = "svelte"
    TYPESCRIPT = "typescript"
    VITE = "vite"
    VUE = "vue"

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
            str_value = str(value)
            content = content.replace(f"${key}", str_value)
            content = content.replace(f"{{{key}}}", str_value)
        return content


@dataclass
class ProcessingScript:
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
    node_version: str = ""
    npm_version: str = ""
    flutter_version: str = ""
    dart_version: str = ""
    java_version: str = ""
    gradle_version: str = ""
    android_sdk_version: str = ""

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
    pre_processing: ProcessingScript
    post_processing: ProcessingScript
    entry_point_url: Optional[str] = None

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
                node_version=config_data['env'].get('node_version', ''),
                npm_version=config_data['env'].get('npm_version', ''),
                flutter_version=config_data['env'].get('flutter_version', ''),
                dart_version=config_data['env'].get('dart_version', ''),
                java_version=config_data['env'].get('java_version', ''),
                gradle_version=config_data['env'].get('gradle_version', ''),
                android_sdk_version=config_data['env'].get('android_sdk_version', '')
            ),
            init_files=config_data.get('init_files', []),
            init_minimal=config_data['init_minimal'],
            run_tool=RunTool(
                command=config_data['run_tool']['command'],
                working_directory=config_data['run_tool']['working_directory']
            ),
            entry_point_url=config_data.get('entry_point_url', None),
            test_tool=TestTool(
                command=config_data['test_tool']['command'],
                working_directory=config_data['test_tool']['working_directory']
            ),
            init_style=config_data.get('init_style', ''),
            linter_script=config_data['linter']['script_content'],
            pre_processing=ProcessingScript(
                script=config_data.get('pre_processing', {}).get('script', '')
            ),
            post_processing=ProcessingScript(
                script=config_data.get('post_processing', {}).get('script', '')
            )
        )