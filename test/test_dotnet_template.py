import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, DotNetTemplate


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def template_dir(temp_dir):
    """Create a mock template directory with necessary files."""
    templates_path = temp_dir / "templates"
    dotnet_path = templates_path / "dotnet"
    dotnet_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'dotnet restore',
            'working_directory': str(dotnet_path)
        },
        'build_cmd': {
            'command': 'dotnet build',
            'working_directory': str(dotnet_path)
        },
        'install_dependencies': {
            'command': 'dotnet restore',
            'working_directory': str(dotnet_path)
        },
        'env': {
            'environment_initialized': True,
            'dotnet_version': '8.0'
        },
        'openapi_generation': {
            'command': 'chmod +x generate_openapi.sh && ./generate_openapi.sh',
            'working_directory': str(dotnet_path)
        },
        'init_files': [],
        'init_minimal': 'Minimal .NET API application initialized',
        'run_tool': {
            'command': 'dotnet run --urls "http://<host>:<port>"',
            'working_directory': str(dotnet_path)
        },
        'test_tool': {
            'command': 'dotnet test',
            'working_directory': str(dotnet_path)
        },
        'init_style': '',
        'entry_point_url': 'http://localhost:3000/docs',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\ndotnet build --no-restore /p:TreatWarningsAsErrors=false /p:WarningLevel=0\nLINT_EXIT_CODE=$?\nif [ $LINT_EXIT_CODE -ne 0 ]; then\n  exit 1\nfi'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\ndotnet restore'
        }
    }

    with open(dotnet_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create mock template files
    (dotnet_path / "Program.cs").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (dotnet_path / "dotnet.csproj").write_text(f'<Project Sdk="Microsoft.NET.Sdk.Web">\n  <PropertyGroup>\n    <TargetFramework>net8.0</TargetFramework>\n    <RootNamespace>${{KAVIA_TEMPLATE_PROJECT_NAME}}</RootNamespace>\n  </PropertyGroup>\n</Project>')
    (dotnet_path / "generate_openapi.sh").write_text("#!/bin/bash\necho 'Generating OpenAPI...'")

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-dotnet-app",
        version="1.0.0",
        description="Test Dotnet Application",
        author="Test Author",
        project_type=ProjectType.DOTNET,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.DOTNET, DotNetTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "Program.cs").exists()
    assert (output_dir / "dotnet.csproj").exists()
    assert (output_dir / "generate_openapi.sh").exists()

    # Verify content replacement
    program_content = (output_dir / "Program.cs").read_text()
    assert "test-dotnet-app" in program_content

    csproj_content = (output_dir / "dotnet.csproj").read_text()
    assert "test-dotnet-app" in csproj_content


def test_dotnet_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.DOTNET, DotNetTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.openapi_generation.command == 'chmod +x generate_openapi.sh && ./generate_openapi.sh'
    assert init_info.configure_environment.command == 'dotnet restore'
    assert init_info.entry_point_url == 'http://localhost:3000/docs'


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "dotnet" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    marker_path = temp_dir / "post_processing_executed"
    config['post_processing']['script'] = f"""#!/bin/bash
    touch {marker_path}
    """

    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.DOTNET, DotNetTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    assert initializer.wait_for_post_process_completed()
    assert marker_path.exists()


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "dotnet",
        "output_path": str(temp_dir / "output"),
        "parameters": {}
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.DOTNET


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "dotnet" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.DOTNET, DotNetTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content
