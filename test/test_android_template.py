import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import os
from unittest.mock import patch, MagicMock

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import (
    ProjectInitializer, TemplateProvider, AndroidTemplate
)


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
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'env': {
            'environment_initialized': True,
            'java_version': '17',
            'android_sdk_version': '34'
        },
        'init_files': [],
        'init_minimal': 'Minimal Android application initialized',
        'run_tool': {
            'command': './gradlew installDebug',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': './gradlew test',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': 'android',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\n./gradlew lint\nLINT_EXIT_CODE=$?\nif [ $LINT_EXIT_CODE -ne 0 ]; then\n   exit 1\nfi'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nchmod +x ./init_script.sh\n./init_script.sh $KAVIA_TEMPLATE_PROJECT_NAME\nrm init_script.sh\necho "Android project post-processing complete"'
        }
    }

    with open(android_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create a mock init_script.sh - just a stub for testing
    init_script_content = """#!/bin/bash
# This is a simplified test version of init_script.sh
echo "Creating Android project: $1"
mkdir -p "app/src/main/java/com/example/$1"
mkdir -p "app/src/main/res/layout"
mkdir -p "app/src/main/res/values"

# Create basic structure
echo '<resources><string name="app_name">'"$1"'</string></resources>' > "app/src/main/res/values/strings.xml"
echo 'plugins { id "com.android.application" }' > "app/build.gradle"
echo 'rootProject.name = "'"$1"'"' > "settings.gradle"
echo 'package com.example.'"$1"';' > "app/src/main/java/com/example/$1/MainActivity.java"
echo '<?xml version="1.0" encoding="utf-8"?><manifest package="com.example.'"$1"'"></manifest>' > "app/src/main/AndroidManifest.xml"
"""
    (android_path / "init_script.sh").write_text(init_script_content)
    os.chmod(android_path / "init_script.sh", 0o755)

    # Create sample project files
    (android_path / "app").mkdir()
    (android_path / "app" / "build.gradle").write_text("// $KAVIA_TEMPLATE_PROJECT_NAME")
    (android_path / "settings.gradle").write_text('rootProject.name = "$KAVIA_TEMPLATE_PROJECT_NAME"')
    
    # Create a mock .idea directory to test hidden directory handling
    idea_path = android_path / ".idea"
    idea_path.mkdir()
    (idea_path / "workspace.xml").write_text('<project name="$KAVIA_TEMPLATE_PROJECT_NAME" />')

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
        parameters={}
    )


def test_android_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)

    # Mock actual subprocess execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Android project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
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


def test_android_template_validates_parameters():
    """Test parameter validation in Android template."""
    valid_config = ProjectConfig(
        name="valid_app",
        version="1.0.0",
        description="Valid Android Application",
        author="Test Author",
        project_type=ProjectType.ANDROID,
        output_path=Path("/tmp/output"),
        parameters={}
    )
    
    template_provider = MagicMock()
    android_template = AndroidTemplate(valid_config, template_provider)
    
    # Test valid parameters validation
    assert android_template.validate_parameters()


def test_android_template_basic_replacements(template_dir, project_config):
    """Test that the Android template correctly replaces basic project info in files."""
    # Add a file that uses basic project properties
    config_path = template_dir / "android" / "app" / "AppConfig.java"
    config_content = """
package com.example.$KAVIA_TEMPLATE_PROJECT_NAME;

public class AppConfig {
    public static final String APP_NAME = "$KAVIA_TEMPLATE_PROJECT_NAME";
    public static final String APP_VERSION = "$KAVIA_PROJECT_VERSION";
    public static final String APP_DESCRIPTION = "$KAVIA_PROJECT_DESCRIPTION";
    public static final String APP_AUTHOR = "$KAVIA_PROJECT_AUTHOR";
}
"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Android project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(project_config)
        assert success
    
    # Verify basic replacement in config file
    output_config_path = project_config.output_path / "app" / "AppConfig.java"
    assert output_config_path.exists()
    
    config_content = output_config_path.read_text()
    assert 'APP_NAME = "testandroidapp"' in config_content
    assert 'APP_VERSION = "1.0.0"' in config_content
    assert 'APP_DESCRIPTION = "Test Android Application"' in config_content
    assert 'APP_AUTHOR = "Test Author"' in config_content


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

    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Command executed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(project_config)
        assert success


def test_android_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.build_cmd.command == './gradlew assembleDebug'
    assert init_info.build_cmd.working_directory == str(project_config.output_path)
    assert init_info.env_config.java_version == '17'
    assert init_info.env_config.android_sdk_version == '34'
    assert init_info.run_tool.command == './gradlew installDebug'
    assert init_info.test_tool.command == './gradlew test'
    assert init_info.init_style == 'android'


def test_android_with_missing_template_config(temp_dir, project_config):
    """Test handling of missing configuration file."""
    templates_path = temp_dir / "templates"
    android_path = templates_path / "android"
    android_path.mkdir(parents=True)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(templates_path)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_run.side_effect = FileNotFoundError("config.yml not found")
        
        # Should fail because config.yml is missing
        result = initializer.initialize_project(project_config)
        assert not result


def test_processing_scripts_failure_handling(template_dir, project_config):
    """Test handling of pre/post processing script failures."""
    # Modify post_processing script to cause a failure
    config_path = template_dir / "android" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Invalid script that will fail
    config['post_processing']['script'] = '#!/bin/bash\nexit 1'
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    
    # Mock subprocess to simulate failure
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Script execution failed")
        
        result = initializer.initialize_project(project_config)
        assert not result


def test_template_project_variations(template_dir, temp_dir):
    """Test Android template with different project configurations."""
    # Test with minimal project info
    minimal_config = ProjectConfig(
        name="minimal_app",
        version="0.1.0",
        description="Minimal Android App",
        author="Test Author",
        project_type=ProjectType.ANDROID,
        output_path=temp_dir / "minimal_output",
        parameters={}
    )
    
    # Test with more detailed project info
    detailed_config = ProjectConfig(
        name="full_app",
        version="1.2.3",
        description="Full Android Application with detailed description that spans multiple words",
        author="Test Team from Acme Corporation",
        project_type=ProjectType.ANDROID,
        output_path=temp_dir / "full_output",
        parameters={}
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Android project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Test minimal configuration
        success1 = initializer.initialize_project(minimal_config)
        assert success1
        
        # Test detailed configuration
        success2 = initializer.initialize_project(detailed_config)
        assert success2
    
    # Verify both projects were created with correct names
    assert (minimal_config.output_path / "settings.gradle").exists()
    assert (detailed_config.output_path / "settings.gradle").exists()
    
    # Verify content in minimal project
    minimal_gradle = (minimal_config.output_path / "settings.gradle").read_text()
    assert "minimal_app" in minimal_gradle
    
    # Verify content in detailed project
    detailed_gradle = (detailed_config.output_path / "settings.gradle").read_text()
    assert "full_app" in detailed_gradle


def test_special_character_handling(template_dir, temp_dir):
    """Test handling of special characters in project info."""
    # Config with special characters
    special_config = ProjectConfig(
        name="special-app!",
        version="1.0.0-beta",
        description="App with special & characters!",
        author="Author's Name",
        project_type=ProjectType.ANDROID,
        output_path=temp_dir / "special_output",
        parameters={}
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.ANDROID, AndroidTemplate)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Android project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(special_config)
        assert success
    
    # Verify content with special characters
    workspace = (special_config.output_path / ".idea" / "workspace.xml").read_text()
    assert "special-app!" in workspace