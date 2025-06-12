import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, AstroTemplate


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    try:
        # Use ignore_errors=True to handle directories that might have read-only files
        shutil.rmtree(temp_path, ignore_errors=True)
    except OSError:
        # If that still fails, log the error but don't fail the test
        print(f"Warning: Could not remove temporary directory {temp_path}")


@pytest.fixture
def template_dir(temp_dir):
    """Create a mock template directory with necessary files."""
    templates_path = temp_dir / "templates"
    astro_path = templates_path / "astro"
    astro_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': 'npm install && npm run build',
            'working_directory': str(astro_path)
        },
        'install_dependencies': {
            'command': 'npm install',
            'working_directory': str(astro_path)
        },    
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal Astro application initialized',
        'run_tool': {
            'command': 'npm run dev',
            'working_directory': str(astro_path)
        },
        'test_tool': {
            'command': 'npm test',
            'working_directory': str(astro_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpx eslint "$@"'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(astro_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (astro_path / "src").mkdir(parents=True)
    (astro_path / "src" / "pages").mkdir()
    (astro_path / "src" / "pages" / "index.astro").write_text("<!-- ${KAVIA_TEMPLATE_PROJECT_NAME} -->")
    (astro_path / "astro.config.mjs").write_text('// Config for ${KAVIA_TEMPLATE_PROJECT_NAME}')
    (astro_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')

    # Create a hidden file to test hidden file handling
    (astro_path / ".gitignore").write_text("node_modules\ndist\n.env")

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-astro-app",
        version="1.0.0",
        description="Test Astro Application",
        author="Test Author",
        project_type=ProjectType.ASTRO,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "src" / "pages" / "index.astro").exists()
    assert (output_dir / "astro.config.mjs").exists()
    assert (output_dir / "package.json").exists()
    
    # Verify hidden files were copied
    assert (output_dir / ".gitignore").exists()

    # Verify content replacement
    index_content = (output_dir / "src" / "pages" / "index.astro").read_text()
    assert "test-astro-app" in index_content

    config_content = (output_dir / "astro.config.mjs").read_text()
    assert "test-astro-app" in config_content
    
    package_json = (output_dir / "package.json").read_text()
    assert "test-astro-app" in package_json


def test_parameter_validation(template_dir, temp_dir):
    """Test parameter validation for Astro template."""
    # Use unique subdirectories for each test
    output_valid_dir = temp_dir / "output-valid"
    output_invalid_dir = temp_dir / "output-invalid"
    
    # Valid parameters
    valid_config = ProjectConfig(
        name="valid-params",
        version="1.0.0",
        description="Test with valid parameters",
        author="Test Author",
        project_type=ProjectType.ASTRO,
        output_path=output_valid_dir,
        parameters={
            "typescript": True,
            "integration_tailwind": True,
            "integration_react": False
        }
    )
    
    # Invalid parameters
    invalid_config = ProjectConfig(
        name="invalid-params",
        version="1.0.0",
        description="Test with invalid parameters",
        author="Test Author",
        project_type=ProjectType.ASTRO,
        output_path=output_invalid_dir,
        parameters={
            "invalid_param": True
        }
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)
    
    # Valid parameters should succeed
    success_valid = initializer.initialize_project(valid_config)
    assert success_valid
    
    # Invalid parameters should fail
    success_invalid = initializer.initialize_project(invalid_config)
    assert not success_invalid
    
    # Clean up directories directly to prevent teardown issues
    try:
        if output_valid_dir.exists():
            shutil.rmtree(output_valid_dir, ignore_errors=True)
        if output_invalid_dir.exists():
            shutil.rmtree(output_invalid_dir, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Error cleaning up test directories: {str(e)}")


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "astro" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)

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
        "project_type": "astro",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "typescript": True,
            "integration_tailwind": True
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.ASTRO
    assert config.parameters["typescript"] is True
    assert config.parameters["integration_tailwind"] is True


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "astro" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ASTRO, AstroTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content