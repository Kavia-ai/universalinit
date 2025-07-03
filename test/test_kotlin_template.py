import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json
import os
from unittest.mock import patch, MagicMock

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, KotlinTemplate


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
    kotlin_path = templates_path / "kotlin"
    kotlin_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': './gradlew assembleDebug',
            'working_directory': str(kotlin_path)
        },
        'build_cmd': {
            'command': './gradlew build',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'install_dependencies': {
            'command': 'ls',
            'working_directory': str(kotlin_path)
        },
        'env': {
            'environment_initialized': True,
            'java_version': '17',
            'android_sdk_version': '34'
        },
        'init_files': [],
        'init_minimal': 'Minimal Kotlin application initialized',
        'run_tool': {
            'command': './gradlew run',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': './gradlew test',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': 'kotlin',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\n./gradlew ktlintCheck\nLINT_EXIT_CODE=$?\nif [ $LINT_EXIT_CODE -ne 0 ]; then\n   exit 1\nfi'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nchmod +x ./gradlew\n./gradlew assembleDebug\necho "Kotlin project post-processing complete"'
        }
    }

    with open(kotlin_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create sample project files
    kotlin_dir = kotlin_path / "src" / "main" / "kotlin"
    kotlin_dir.mkdir(parents=True)
    (kotlin_dir / "Main.kt").write_text("""
    fun main() {
        println("Hello, ${KAVIA_TEMPLATE_PROJECT_NAME}!")
    }
    """)
    
    (kotlin_path / "build.gradle.kts").write_text("""
    plugins {
        kotlin("jvm") version "1.9.0"
        application
    }
    
    group = "com.example"
    version = "${KAVIA_PROJECT_VERSION}"
    
    application {
        mainClass.set("MainKt")
    }
    
    repositories {
        mavenCentral()
    }
    
    dependencies {
        implementation(kotlin("stdlib"))
        testImplementation(kotlin("test"))
    }
    """)
    
    (kotlin_path / "settings.gradle.kts").write_text('rootProject.name = "${KAVIA_TEMPLATE_PROJECT_NAME}"')
    
    # Create a mock .idea directory to test hidden directory handling
    idea_path = kotlin_path / ".idea"
    idea_path.mkdir()
    (idea_path / "workspace.xml").write_text('<project name="${KAVIA_TEMPLATE_PROJECT_NAME}" />')

    return templates_path
    

@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="testkotlinapp",
        version="1.0.0",
        description="Test Kotlin Application",
        author="Test Author",
        project_type=ProjectType.KOTLIN,
        output_path=temp_dir / "output",
        parameters={
            "kotlin_version": "1.9.0",
            "build_system": "gradle"
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)

    with patch('subprocess.run'):  # Mock subprocess to avoid actual execution
        success = initializer.initialize_project(project_config)
        assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "src" / "main" / "kotlin" / "Main.kt").exists()
    assert (output_dir / "build.gradle.kts").exists()
    assert (output_dir / "settings.gradle.kts").exists()

    # Verify content replacement
    main_content = (output_dir / "src" / "main" / "kotlin" / "Main.kt").read_text()
    assert project_config.name in main_content

    settings_gradle = (output_dir / "settings.gradle.kts").read_text()
    assert project_config.name in settings_gradle
    
    # Verify hidden directory handling
    assert (output_dir / ".idea").exists()
    assert (output_dir / ".idea" / "workspace.xml").exists()


def test_kotlin_template_validates_parameters():
    """Test parameter validation in Kotlin template."""
    # The Kotlin template accepts any parameters, so all configs should be valid
    valid_config = ProjectConfig(
        name="valid_app",
        version="1.0.0",
        description="Valid Kotlin Application",
        author="Test Author",
        project_type=ProjectType.KOTLIN,
        output_path=Path("/tmp/output"),
        parameters={
            "kotlin_version": "1.9.0",
            "build_system": "gradle"
        }
    )
    
    # Even empty parameters should be valid
    empty_params_config = ProjectConfig(
        name="empty_params_app",
        version="1.0.0",
        description="App with empty params",
        author="Test Author",
        project_type=ProjectType.KOTLIN,
        output_path=Path("/tmp/output"),
        parameters={}
    )
    
    template_provider = MagicMock()
    
    # Both configurations should be valid
    assert KotlinTemplate(valid_config, template_provider).validate_parameters()
    assert KotlinTemplate(empty_params_config, template_provider).validate_parameters()


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "kotlin" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    assert initializer.wait_for_post_process_completed()

    assert project_config.output_path.exists()
    assert (project_config.output_path / "src").exists()


def test_kotlin_template_basic_replacements(template_dir, project_config):
    """Test that the Kotlin template correctly replaces basic project info in files."""
    # Add a file that uses basic project properties
    config_path = template_dir / "kotlin" / "src" / "main" / "kotlin" / "AppConfig.kt"
    config_content = """
object AppConfig {
    const val APP_NAME = "{KAVIA_TEMPLATE_PROJECT_NAME}"
    const val APP_VERSION = "{KAVIA_PROJECT_VERSION}"
    const val APP_DESCRIPTION = "{KAVIA_PROJECT_DESCRIPTION}"
    const val APP_AUTHOR = "{KAVIA_PROJECT_AUTHOR}"
}
"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)
    
    with patch('subprocess.run'):  # Mock subprocess to avoid actual execution
        success = initializer.initialize_project(project_config)
        assert success
    
    # Verify basic replacement in config file
    output_config_path = project_config.output_path / "src" / "main" / "kotlin" / "AppConfig.kt"
    assert output_config_path.exists()
    
    config_content = output_config_path.read_text()
    assert project_config.name in config_content
    assert project_config.version in config_content
    assert project_config.description in config_content
    assert project_config.author in config_content


def test_kotlin_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.build_cmd.command == './gradlew build'
    assert init_info.build_cmd.working_directory == str(project_config.output_path)
    assert init_info.env_config.java_version == '17'
    # Note: The Kotlin template config doesn't have kotlin_version, only java_version and android_sdk_version
    assert init_info.env_config.android_sdk_version == '34'
    assert init_info.run_tool.command == './gradlew run'
    assert init_info.test_tool.command == './gradlew test'
    assert init_info.init_style == 'kotlin'
    assert init_info.configure_enviroment == './gradlew assembleDebug'


def test_kotlin_with_missing_template_config(temp_dir, project_config):
    """Test handling of missing configuration file."""
    templates_path = temp_dir / "templates"
    kotlin_path = templates_path / "kotlin"
    kotlin_path.mkdir(parents=True)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(templates_path)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)
    
    # Should fail because config.yml is missing
    result = initializer.initialize_project(project_config)
    assert not result


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "kotlin",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "kotlin_version": "1.9.0",
            "build_system": "gradle"
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.KOTLIN
    assert config.parameters["kotlin_version"] == "1.9.0"
    assert config.parameters["build_system"] == "gradle"


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    # Only use variables that are actually supported by the implementation
    test_file = template_dir / "kotlin" / "test.txt"
    test_content = """
    Project: {KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: {KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)

    with patch('subprocess.run'):  # Mock subprocess to avoid actual execution
        success = initializer.initialize_project(project_config)
        assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content


def test_special_character_handling(template_dir, temp_dir):
    """Test handling of special characters in project info."""
    # Config with special characters
    special_config = ProjectConfig(
        name="special-kotlin!",
        version="1.0.0-beta",
        description="App with special & characters!",
        author="Author's Name",
        project_type=ProjectType.KOTLIN,
        output_path=temp_dir / "special_output",
        parameters={
            "kotlin_version": "1.9.0",
            "build_system": "gradle"
        }
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.KOTLIN, KotlinTemplate)
    
    with patch('subprocess.run'):  # Mock subprocess to avoid actual execution
        success = initializer.initialize_project(special_config)
        assert success
    
    # Verify content with special characters was properly handled
    workspace = (special_config.output_path / ".idea" / "workspace.xml").read_text()
    assert "special-kotlin!" in workspace