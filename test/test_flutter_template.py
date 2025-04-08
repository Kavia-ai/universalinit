import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import os
from unittest.mock import patch, MagicMock

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import (
    ProjectInitializer, TemplateProvider, FlutterTemplate
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def template_dir(temp_dir):
    """Create a mock template directory with necessary files for Flutter."""
    templates_path = temp_dir / "templates"
    flutter_path = templates_path / "flutter"
    flutter_path.mkdir(parents=True)

    config = {
        'build_cmd': {
            'command': 'flutter build apk --release --target-platform android-x64',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'env': {
            'environment_initialized': True,
            'flutter_version': '3.27.3',
            'dart_version': '3.6.1'
        },
        'init_files': [],
        'init_minimal': 'Minimal Flutter application initialized',
        'run_tool': {
            'command': 'flutter run',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': 'flutter test',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nflutter analyze'
        },
        'pre_processing': {
            'script': '#!/bin/bash\nflutter create {KAVIA_TEMPLATE_PROJECT_NAME}'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nflutter pub get'
        }
    }

    with open(flutter_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create realistic Flutter template structure
    lib_path = flutter_path / "lib"
    lib_path.mkdir()
    
    # Main application file
    main_dart_content = """
import 'package:flutter/material.dart';

void main() {
  runApp(${KAVIA_TEMPLATE_PROJECT_NAME}App());
}

class ${KAVIA_TEMPLATE_PROJECT_NAME}App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '${KAVIA_TEMPLATE_PROJECT_NAME}',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${KAVIA_TEMPLATE_PROJECT_NAME}'),
      ),
      body: Center(
        child: Text('Welcome to ${KAVIA_TEMPLATE_PROJECT_NAME}!'),
      ),
    );
  }
}
"""
    (lib_path / "main.dart").write_text(main_dart_content)
    
    # Create a realistic pubspec.yaml
    pubspec_content = """
name: ${KAVIA_TEMPLATE_PROJECT_NAME}
description: ${KAVIA_PROJECT_DESCRIPTION}
version: ${KAVIA_PROJECT_VERSION}
author: ${KAVIA_PROJECT_AUTHOR}

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.5
  provider: ^6.1.1
  http: ^1.1.0
  shared_preferences: ^2.2.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  assets:
    - assets/images/
"""
    (flutter_path / "pubspec.yaml").write_text(pubspec_content)
    
    # Create test directory with a sample test
    test_dir = flutter_path / "test"
    test_dir.mkdir()
    widget_test_content = """
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:${KAVIA_TEMPLATE_PROJECT_NAME}/main.dart';

void main() {
  testWidgets('App renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(${KAVIA_TEMPLATE_PROJECT_NAME}App());
    expect(find.text('Welcome to ${KAVIA_TEMPLATE_PROJECT_NAME}!'), findsOneWidget);
  });
}
"""
    (test_dir / "widget_test.dart").write_text(widget_test_content)
    
    # Create Android directory structure
    android_dir = flutter_path / "android"
    android_dir.mkdir()
    app_dir = android_dir / "app"
    app_dir.mkdir(parents=True)
    
    # Create build.gradle file
    build_gradle_content = """
def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}

apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'
apply from: "$flutterRoot/packages/flutter_tools/gradle/flutter.gradle"

android {
    compileSdkVersion 34

    defaultConfig {
        applicationId "com.example.${KAVIA_TEMPLATE_PROJECT_NAME.replace('-', '_')}"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "${KAVIA_PROJECT_VERSION}"
    }

    buildTypes {
        release {
            signingConfig signingConfigs.debug
        }
    }
}

flutter {
    source '../..'
}
"""
    (app_dir / "build.gradle").write_text(build_gradle_content)
    
    # Create hidden files/dirs to test proper handling
    (flutter_path / ".gitignore").write_text("""
# Flutter/Dart
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
build/
""")
    
    idea_dir = flutter_path / ".idea"
    idea_dir.mkdir()
    (idea_dir / "workspace.xml").write_text('<project name="${KAVIA_TEMPLATE_PROJECT_NAME}" />')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration for Flutter."""
    return ProjectConfig(
        name="flutter_test_app",
        version="1.0.0",
        description="Test Flutter Application",
        author="Test Author",
        project_type=ProjectType.FLUTTER,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_flutter_initialization(template_dir, project_config):
    """Test that Flutter project is initialized with correct structure."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    
    # Mock actual Flutter command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Flutter project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(project_config)
        assert success
    
    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "lib").exists()
    assert (output_dir / "lib" / "main.dart").exists()
    assert (output_dir / "pubspec.yaml").exists()
    assert (output_dir / "test").exists()
    assert (output_dir / "android").exists()
    assert (output_dir / "android" / "app" / "build.gradle").exists()
    
    # Verify hidden files/dirs were copied
    assert (output_dir / ".gitignore").exists()
    assert (output_dir / ".idea").exists()
    
    # Verify content replacement in main.dart
    main_content = (output_dir / "lib" / "main.dart").read_text()
    assert "flutter_test_app" in main_content
    # The template is using direct variable substitution, not camel-casing the app name
    assert "$flutter_test_appApp" in main_content
    
    # Verify content replacement in pubspec.yaml
    pubspec = (output_dir / "pubspec.yaml").read_text()
    assert "flutter_test_app" in pubspec
    assert "Test Flutter Application" in pubspec
    assert "Test Author" in pubspec


def test_flutter_template_validates_parameters():
    """Test parameter validation in Flutter template."""
    valid_config = ProjectConfig(
        name="valid_app",
        version="1.0.0",
        description="Valid Flutter Application",
        author="Test Author",
        project_type=ProjectType.FLUTTER,
        output_path=Path("/tmp/output"),
        parameters={}
    )
    
    template_provider = MagicMock()
    flutter_template = FlutterTemplate(valid_config, template_provider)
    
    # Test valid parameters validation
    assert flutter_template.validate_parameters()


def test_flutter_template_basic_replacements(template_dir, project_config):
    """Test that the Flutter template correctly replaces basic project info in files."""
    # Add a file that uses basic project properties
    config_path = template_dir / "flutter" / "lib" / "config.dart"
    config_content = """
class AppConfig {
  static final String appName = "$KAVIA_TEMPLATE_PROJECT_NAME";
  static final String appVersion = "$KAVIA_PROJECT_VERSION";
  static final String appDescription = "$KAVIA_PROJECT_DESCRIPTION";
  static final String appAuthor = "$KAVIA_PROJECT_AUTHOR";
}
"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Flutter project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(project_config)
        assert success
    
    # Verify basic replacement in config file
    output_config_path = project_config.output_path / "lib" / "config.dart"
    assert output_config_path.exists()
    
    config_content = output_config_path.read_text()
    assert 'appName = "flutter_test_app"' in config_content
    assert 'appVersion = "1.0.0"' in config_content
    assert 'appDescription = "Test Flutter Application"' in config_content
    assert 'appAuthor = "Test Author"' in config_content


def test_processing_scripts_failure_handling(template_dir, project_config):
    """Test handling of pre/post processing script failures."""
    # Modify pre_processing script to cause a failure
    config_path = template_dir / "flutter" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Invalid script that will fail
    config['pre_processing']['script'] = '#!/bin/bash\nexit 1'
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    result = initializer.initialize_project(project_config)
    assert not result


def test_flutter_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()
    
    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.build_cmd.command == 'flutter build apk --release --target-platform android-x64'
    assert init_info.build_cmd.working_directory == str(project_config.output_path)
    assert init_info.env_config.flutter_version == '3.27.3'
    assert init_info.env_config.dart_version == '3.6.1'
    assert init_info.run_tool.command == 'flutter run'
    assert init_info.test_tool.command == 'flutter test'


def test_flutter_with_missing_template_config(temp_dir, project_config):
    """Test handling of missing configuration file."""
    templates_path = temp_dir / "templates"
    flutter_path = templates_path / "flutter"
    flutter_path.mkdir(parents=True)
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(templates_path)
    result = initializer.initialize_project(project_config)
    assert not result


def test_template_project_variations(template_dir, temp_dir):
    """Test Flutter template with different project configurations."""
    # Test with minimal project info
    minimal_config = ProjectConfig(
        name="minimal_app",
        version="0.1.0",
        description="Minimal Flutter App",
        author="Test Author",
        project_type=ProjectType.FLUTTER,
        output_path=temp_dir / "minimal_output",
        parameters={}
    )
    
    # Test with more detailed project info
    detailed_config = ProjectConfig(
        name="full_app",
        version="1.2.3",
        description="Full Flutter Application with detailed description that spans multiple words",
        author="Test Team from Acme Corporation",
        project_type=ProjectType.FLUTTER,
        output_path=temp_dir / "full_output",
        parameters={}
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Flutter project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Test minimal configuration
        success1 = initializer.initialize_project(minimal_config)
        assert success1
        
        # Test detailed configuration
        success2 = initializer.initialize_project(detailed_config)
        assert success2
    
    # Verify both projects were created with correct names
    assert (minimal_config.output_path / "pubspec.yaml").exists()
    assert (detailed_config.output_path / "pubspec.yaml").exists()
    
    # Verify content in minimal project
    minimal_pubspec = (minimal_config.output_path / "pubspec.yaml").read_text()
    assert "minimal_app" in minimal_pubspec
    assert "Minimal Flutter App" in minimal_pubspec
    
    # Verify content in detailed project
    detailed_pubspec = (detailed_config.output_path / "pubspec.yaml").read_text()
    assert "full_app" in detailed_pubspec
    assert "Full Flutter Application with detailed description" in detailed_pubspec
    assert "Test Team from Acme Corporation" in detailed_pubspec


def test_special_character_handling(template_dir, temp_dir):
    """Test handling of special characters in project info."""
    # Config with special characters
    special_config = ProjectConfig(
        name="special-app!",
        version="1.0.0-beta",
        description="App with special & characters!",
        author="Author's Name",
        project_type=ProjectType.FLUTTER,
        output_path=temp_dir / "special_output",
        parameters={}
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    
    # Mock subprocess to avoid actual command execution
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.stdout = "Flutter project created successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success = initializer.initialize_project(special_config)
        assert success
    
    # Verify content with special characters
    pubspec = (special_config.output_path / "pubspec.yaml").read_text()
    assert "special-app!" in pubspec
    assert "App with special & characters!" in pubspec
    assert "Author's Name" in pubspec