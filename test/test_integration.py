import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json
import time

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, ReactTemplate, FileSystemHelper


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
    react_path = templates_path / "react"
    react_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'npm install',
            'working_directory': str(react_path)
        },
        'build_cmd': {
            'command': 'npm install && npx tsc --noEmit && npm test -- --ci',
            'working_directory': str(react_path)
        },
        'install_dependencies': {
            'command': 'npm install',
            'working_directory': str(react_path)
        },
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal React application initialized',
        'run_tool': {
            'command': 'npm start',
            'working_directory': str(react_path)
        },
        'test_tool': {
            'command': 'npm test',
            'working_directory': str(react_path)
        },
        'init_style': '',
        'entry_point_url': 'http://localhost:3000',
        'linter': {
            'script_content': '#!/bin/bash\neslint "$@"'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(react_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (react_path / "src").mkdir()
    (react_path / "src" / "index.tsx").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (react_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-react-app",
        version="1.0.0",
        description="Test React Application",
        author="Test Author",
        project_type=ProjectType.REACT,
        output_path=temp_dir / "output",
        parameters={
            "typescript": True,
            "styling_solution": "styled-components"
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)

    success = initializer.initialize_project(project_config)
    assert initializer.wait_for_post_process_completed()
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "src" / "index.tsx").exists()
    assert (output_dir / "package.json").exists()

    # Verify content replacement
    index_content = (output_dir / "src" / "index.tsx").read_text()
    assert "test-react-app" in index_content

    package_json = (output_dir / "package.json").read_text()
    assert "test-react-app" in package_json

def test_get_run_command(template_dir, project_config):
    """Test getting the run command from a template."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    run_command = template.get_run_command()
    
    assert run_command == "npm start"


def test_get_entry_point_url(template_dir, project_config):
    """Test getting the run command from a template."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    entry_point_url = template.get_entry_point_url()
    
    assert entry_point_url == "http://localhost:3000"

def test_missing_required_parameters(template_dir):
    """Test initialization with missing required parameters."""
    config = ProjectConfig(
        name="test-react-app",
        version="1.0.0",
        description="Test React Application",
        author="Test Author",
        project_type=ProjectType.REACT,
        output_path=Path("output"),
        parameters={}  # Missing required parameters
    )

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)

    success = initializer.initialize_project(config)
    assert not success


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "react" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)

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
        "project_type": "react",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "typescript": True,
            "styling_solution": "styled-components"
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.REACT
    assert config.parameters["typescript"] is True


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "react" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT, ReactTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    assert initializer.wait_for_post_process_completed()
    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content

def test_extra_files_single_file(template_dir, project_config, temp_dir):
    """Test copying a single extra file."""
    # Create an extra file outside the template
    extra_file = temp_dir / "extra_config.json"
    extra_file.write_text('{"project": "${KAVIA_TEMPLATE_PROJECT_NAME}", "version": "${KAVIA_PROJECT_VERSION}"}')
    
    # Test FileSystemHelper directly
    replacements = project_config.get_replaceable_parameters()
    FileSystemHelper.copy_template(
        template_dir / "react",
        project_config.output_path,
        replacements,
        extra_files=[str(extra_file)]
    )
    
    # Verify the extra file was copied
    copied_file = project_config.output_path / "extra_config.json"
    assert copied_file.exists()
    
    # Verify replacements were applied
    content = copied_file.read_text()
    assert "test-react-app" in content
    assert "1.0.0" in content
    assert "${KAVIA_TEMPLATE_PROJECT_NAME}" not in content


def test_extra_files_directory(template_dir, project_config, temp_dir):
    """Test copying an extra directory with nested files."""
    # Create an extra directory structure
    extra_dir = temp_dir / "extra_templates"
    extra_dir.mkdir()
    (extra_dir / "components").mkdir()
    (extra_dir / "components" / "Header.tsx").write_text(
        "export const Header = () => <h1>${KAVIA_TEMPLATE_PROJECT_NAME}</h1>;"
    )
    (extra_dir / "styles.css").write_text(
        "/* Styles for ${KAVIA_TEMPLATE_PROJECT_NAME} */"
    )
    
    # Test FileSystemHelper directly
    replacements = project_config.get_replaceable_parameters()
    FileSystemHelper.copy_template(
        template_dir / "react",
        project_config.output_path,
        replacements,
        extra_files=[str(extra_dir)]
    )
    
    # Verify the directory structure was copied
    copied_dir = project_config.output_path / "extra_templates"
    assert copied_dir.exists()
    assert (copied_dir / "components" / "Header.tsx").exists()
    assert (copied_dir / "styles.css").exists()
    
    # Verify replacements in nested files
    header_content = (copied_dir / "components" / "Header.tsx").read_text()
    assert "test-react-app" in header_content
    
    styles_content = (copied_dir / "styles.css").read_text()
    assert "test-react-app" in styles_content


def test_extra_files_nonexistent_path(template_dir, project_config, temp_dir):
    """Test that nonexistent extra files are gracefully handled."""
    nonexistent_file = temp_dir / "does_not_exist.txt"
    
    # Should not raise an error for nonexistent files
    replacements = project_config.get_replaceable_parameters()
    FileSystemHelper.copy_template(
        template_dir / "react",
        project_config.output_path,
        replacements,
        extra_files=[str(nonexistent_file)]
    )
    
    # Verify the template files were still copied
    assert project_config.output_path.exists()
    assert (project_config.output_path / "src" / "index.tsx").exists()
    assert (project_config.output_path / "package.json").exists()


def test_extra_files_with_binary_content(template_dir, project_config, temp_dir):
    """Test copying extra binary files."""
    # Create a binary file
    extra_binary = temp_dir / "logo.png"
    # Create a simple PNG header (not a valid image, but binary data)
    extra_binary.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    
    # Test FileSystemHelper directly
    replacements = project_config.get_replaceable_parameters()
    FileSystemHelper.copy_template(
        template_dir / "react",
        project_config.output_path,
        replacements,
        extra_files=[str(extra_binary)]
    )
    
    # Verify the binary file was copied correctly
    copied_binary = project_config.output_path / "logo.png"
    assert copied_binary.exists()
    assert copied_binary.read_bytes() == extra_binary.read_bytes()
