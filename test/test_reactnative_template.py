import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, ReactNativeTemplate


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
    reactnative_path = templates_path / "reactnative"
    reactnative_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'npm install',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'build_cmd': {
            'command': 'npm run prebuild && cd android && ./gradlew assembleDebug',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'install_dependencies': {
            'command': 'npm install',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'env': {
            'environment_initialized': True,
            'node_version': '20.18.0',
            'npm_version': '10.8.2'
        },
        'init_files': [],
        'init_minimal': 'Minimal React Native (Expo) application initialized',
        'run_tool': {
            'command': 'npm run web -- --port <port>',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': 'npm run lint',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\nset -e\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm run lint'
        },
        'post_processing': {
            'script': '#!/bin/bash\nset -e\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(reactnative_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (reactnative_path / "app").mkdir()
    (reactnative_path / "app" / "index.tsx").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (reactnative_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')
    (reactnative_path / "app.json").write_text('{"expo": {"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-reactnative-app",
        version="1.0.0",
        description="Test React Native Application",
        author="Test Author",
        project_type=ProjectType.REACT_NATIVE,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_reactnative_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT_NATIVE, ReactNativeTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.configure_environment.command == 'npm install'
    assert init_info.build_cmd.command == 'npm run prebuild && cd android && ./gradlew assembleDebug'
    assert init_info.run_tool.command == 'npm run web -- --port <port>'
    assert init_info.test_tool.command == 'npm run lint'
    assert init_info.env_config.node_version == '20.18.0'
    assert init_info.env_config.npm_version == '10.8.2'


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT_NATIVE, ReactNativeTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "app" / "index.tsx").exists()
    assert (output_dir / "package.json").exists()
    assert (output_dir / "app.json").exists()

    # Verify content replacement
    app_content = (output_dir / "app" / "index.tsx").read_text()
    assert "test-reactnative-app" in app_content

    package_json = (output_dir / "package.json").read_text()
    assert "test-reactnative-app" in package_json

    app_json = (output_dir / "app.json").read_text()
    assert "test-reactnative-app" in app_json


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "reactnative" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.REACT_NATIVE, ReactNativeTemplate)

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
        "project_type": "reactnative",
        "output_path": str(temp_dir / "output"),
        "parameters": {}
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.REACT_NATIVE


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "reactnative" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REACT_NATIVE, ReactNativeTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content
