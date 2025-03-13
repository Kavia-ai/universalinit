import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, AndroidTemplate


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def template_dir(temp_dir):
    """Create a mock template directory with necessary files."""
    templates_path = temp_dir / "templates"
    android_path = templates_path / "android"
    android_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': './gradlew assembleDebug',
            'working_directory': str(android_path)
        },
        'env': {
            'environment_initialized': True,
            'java_version': '17',
            'gradle_version': '8.0',
            'android_sdk_version': '34'
        },
        'init_files': [],
        'init_minimal': 'Minimal Android application initialized',
        'run_tool': {
            'command': './gradlew installDebug',
            'working_directory': str(android_path)
        },
        'test_tool': {
            'command': './gradlew test',
            'working_directory': str(android_path)
        },
        'init_style': 'android',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\necho "Linting would run here"'
        },
        'post_processing': {
            'script': '#!/bin/bash\necho "Android project post-processing complete"'
        }
    }

    with open(android_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (android_path / "app").mkdir()
    (android_path / "app" / "build.gradle").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (android_path / "settings.gradle").write_text('rootProject.name = "${KAVIA_TEMPLATE_PROJECT_NAME}"')
    
    # Create a mock .idea directory to test hidden directory handling
    idea_path = android_path / ".idea"
    idea_path.mkdir()
    (idea_path / "workspace.xml").write_text('<project name="${KAVIA_TEMPLATE_PROJECT_NAME}" />')

    return templates_path
    
@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="testandroidapp",
        version="1.0.0",
        description="Test Android Application",
        author="Test Author",
        project_type=ProjectType.ANDROID,
        output_path=temp_dir / "output",
        parameters={
            'android_min_sdk': '24',
            'android_target_sdk': '34',
            'android_package_name': 'com.example.testandroidapp'
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "app" / "build.gradle").exists()
    assert (output_dir / "settings.gradle").exists()

    # Verify content replacement
    build_gradle_content = (output_dir / "app" / "build.gradle").read_text()
    assert "testandroidapp" in build_gradle_content

    settings_gradle = (output_dir / "settings.gradle").read_text()
    assert "testandroidapp" in settings_gradle
    
    # Verify hidden directory handling
    assert (output_dir / ".idea").exists()
    assert (output_dir / ".idea" / "workspace.xml").exists()
    
    # Verify content replacement in hidden files
    workspace_content = (output_dir / ".idea" / "workspace.xml").read_text()
    assert "testandroidapp" in workspace_content


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "android" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    assert marker_path.exists()


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "android",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "android_min_sdk": "24",
            "android_target_sdk": "34",
            "android_package_name": "com.example.jsonconfig"
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.ANDROID


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "android" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    Package: {KAVIA_ANDROID_PACKAGE_NAME}
    Min SDK: ${KAVIA_ANDROID_MIN_SDK}
    Target SDK: ${KAVIA_ANDROID_TARGET_SDK}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content
    assert project_config.parameters['android_package_name'] in content
    assert project_config.parameters['android_min_sdk'] in content
    assert project_config.parameters['android_target_sdk'] in content
