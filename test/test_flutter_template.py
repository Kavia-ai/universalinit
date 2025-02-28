import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, FlutterTemplate


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
    flutter_path = templates_path / "flutter"
    flutter_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': 'flutter pub get',
            'working_directory': str(flutter_path)
        },
        'env': {
            'environment_initialized': True,
            'flutter_version': 'stable',
            'dart_version': '3.3.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal Flutter application initialized',
        'run_tool': {
            'command': 'flutter run',
            'working_directory': str(flutter_path)
        },
        'test_tool': {
            'command': 'flutter test',
            'working_directory': str(flutter_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nflutter analyze'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nflutter pub get'
        }
    }

    with open(flutter_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (flutter_path / "lib").mkdir()
    (flutter_path / "lib" / "main.dart").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    
    # Update this line with a proper pubspec.yaml that includes SDK constraint
    (flutter_path / "pubspec.yaml").write_text('''
name: {KAVIA_TEMPLATE_PROJECT_NAME}
description: {KAVIA_PROJECT_DESCRIPTION}

environment:
  sdk: "^3.5.4"

dependencies:
  flutter:
    sdk: flutter
''')
    
    # Create a mock .idea directory to test hidden directory handling
    idea_path = flutter_path / ".idea"
    idea_path.mkdir()
    (idea_path / "workspace.xml").write_text('<project name="${KAVIA_TEMPLATE_PROJECT_NAME}" />')

    return templates_path
    
@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="testflutterapp",
        version="1.0.0",
        description="Test Flutter Application",
        author="Test Author",
        project_type=ProjectType.FLUTTER,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.FLUTTER, FlutterTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "lib" / "main.dart").exists()
    assert (output_dir / "pubspec.yaml").exists()

    # Verify content replacement
    main_content = (output_dir / "lib" / "main.dart").read_text()
    assert "testflutterapp" in main_content

    pubspec = (output_dir / "pubspec.yaml").read_text()
    assert "testflutterapp" in pubspec
    
    # Verify hidden directory handling
    assert (output_dir / ".idea").exists()
    assert (output_dir / ".idea" / "workspace.xml").exists()
    
    # Verify content replacement in hidden files
    workspace_content = (output_dir / ".idea" / "workspace.xml").read_text()
    assert "testflutterapp" in workspace_content


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "flutter" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.FLUTTER, FlutterTemplate)

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
        "project_type": "flutter",
        "output_path": str(temp_dir / "output"),
        "parameters": {}
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.FLUTTER


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "flutter" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.FLUTTER, FlutterTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content