import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, FlaskTemplate


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
    flask_path = templates_path / "flask"
    flask_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'python3 -m venv venv && \
                source venv/bin/activate && \
                pip install -r requirements.txt',
            'working_directory': str(flask_path)
        },
        'build_cmd': {
            'command': 'pip install -r requirements.txt',
            'working_directory': str(flask_path)
        },
        'install_dependencies': {
            'command': 'source venv/bin/activate && pip install -r requirements.txt',
            'working_directory': str(flask_path)
        },        
        'env': {
            'environment_initialized': True,
            'python_version': '3.12.3',
            'pip_version': '24.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal Flask application initialized',
        'run_tool': {
            'command': 'uvicorn src.api.main:app',
            'working_directory': str(flask_path)
        },
        "openapi_generation": {
            "command": "python3 -m venv venv && \
            source venv/bin/activate && \
            pip install -r requirements.txt && \
            python src/api/generate_openapi.py",
            "working_directory": str(flask_path)
        },
        'test_tool': {
            'command': 'pytest',
            'working_directory': str(flask_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nflake8 .'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\npip install -r requirements.txt'
        }
    }

    with open(flask_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (flask_path / "src").mkdir()
    (flask_path / "src" / "api").mkdir()
    (flask_path / "src" / "api" / "main.py").write_text("# ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (flask_path / "requirements.txt").write_text('# ${KAVIA_TEMPLATE_PROJECT_NAME}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-flask-app",
        version="1.0.0",
        description="Test Flask Application",
        author="Test Author",
        project_type=ProjectType.FLASK,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.FLASK, FlaskTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "src" / "api" / "main.py").exists()
    assert (output_dir / "requirements.txt").exists()

    # Verify content replacement
    main_content = (output_dir / "src" / "api" / "main.py").read_text()
    assert "test-flask-app" in main_content

    requirements = (output_dir / "requirements.txt").read_text()
    assert "test-flask-app" in requirements


def test_flask_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.FLASK, FlaskTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.openapi_generation.command == "python3 -m venv venv && \
            source venv/bin/activate && \
            pip install -r requirements.txt && \
            python src/api/generate_openapi.py"
    assert init_info.configure_enviroment.command == 'python3 -m venv venv && \
                source venv/bin/activate && \
                pip install -r requirements.txt'


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "flask" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.FLASK, FlaskTemplate)

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
        "project_type": "flask",
        "output_path": str(temp_dir / "output"),
        "parameters": {}
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.FLASK


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "flask" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.FLASK, FlaskTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content
