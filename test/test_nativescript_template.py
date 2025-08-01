import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json
import os

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, NativeScriptTemplate


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
    """Create a mock template directory with necessary files that match NativeScript structure."""
    templates_path = temp_dir / "templates"
    nativescript_path = templates_path / "nativescript"
    nativescript_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'npm install --legacy-peer-deps',
            'working_directory': str(nativescript_path)
        },
        'build_cmd': {
            'command': 'npm install --legacy-peer-deps && ns build',
            'working_directory': str(nativescript_path)
        },
        'install_dependencies': {
            'command': 'npm install --legacy-peer-deps',
            'working_directory': str(nativescript_path)
        },
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal NativeScript application initialized',
        'run_tool': {
            'command': 'ns run',
            'working_directory': str(nativescript_path)
        },
        'test_tool': {
            'command': 'ns test',
            'working_directory': str(nativescript_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nns lint'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install --legacy-peer-deps'
        }
    }

    with open(nativescript_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create a more realistic NativeScript template structure
    
    # Create App_Resources structure for both Android and iOS
    app_resources = nativescript_path / "App_Resources"
    android_dir = app_resources / "Android"
    ios_dir = app_resources / "iOS"
    android_dir.mkdir(parents=True)
    ios_dir.mkdir(parents=True)
    
    # Android resources
    android_src = android_dir / "src" / "main"
    android_res = android_src / "res"
    android_res.mkdir(parents=True)
    (android_dir / "app.gradle").write_text('// ${KAVIA_TEMPLATE_PROJECT_NAME} gradle config')
    (android_src / "AndroidManifest.xml").write_text('<manifest package="${KAVIA_TEMPLATE_PROJECT_NAME}"/>')
    
    # iOS resources
    (ios_dir / "Info.plist").write_text('<dict><key>CFBundleName</key><string>${KAVIA_TEMPLATE_PROJECT_NAME}</string></dict>')
    
    # App directory structure
    app_dir = nativescript_path / "app"
    home_dir = app_dir / "home"
    app_dir.mkdir(parents=True)
    home_dir.mkdir(parents=True)
    
    (app_dir / "app.js").write_text('// ${KAVIA_TEMPLATE_PROJECT_NAME} main app')
    (app_dir / "app.css").write_text('/* ${KAVIA_TEMPLATE_PROJECT_NAME} styles */')
    (app_dir / "app-root.xml").write_text('<Frame defaultPage="home/home-page" />')
    (home_dir / "home-page.js").write_text('// ${KAVIA_TEMPLATE_PROJECT_NAME} home page')
    (home_dir / "home-page.xml").write_text('<Page><ActionBar title="${KAVIA_TEMPLATE_PROJECT_NAME}" /></Page>')
    
    # Root config files
    (nativescript_path / "package.json").write_text('''
    {
      "name": "${KAVIA_TEMPLATE_PROJECT_NAME}",
      "version": "${KAVIA_PROJECT_VERSION}",
      "description": "${KAVIA_PROJECT_DESCRIPTION}",
      "author": "${KAVIA_PROJECT_AUTHOR}",
      "main": "app/app.js",
      "dependencies": {
        "@nativescript/core": "~8.5.0"
      }
    }
    ''')
    (nativescript_path / "nativescript.config.ts").write_text('''
    import { NativeScriptConfig } from '@nativescript/core';

    export default {
      id: "org.nativescript.${KAVIA_TEMPLATE_PROJECT_NAME}",
      appPath: 'app',
      appResourcesPath: 'App_Resources',
      android: {
        v8Flags: '--expose_gc',
        markingMode: 'none'
      }
    } as NativeScriptConfig;
    ''')
    
    # Create hooks directory
    hooks_dir = nativescript_path / "hooks" / "before-checkForChanges"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "nativescript-core.js").write_text('// Hooks for ${KAVIA_TEMPLATE_PROJECT_NAME}')
    
    # Hidden files
    (nativescript_path / ".gitignore").write_text('''
    node_modules/
    platforms/
    hooks/
    ''')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-ns-app",
        version="1.0.0",
        description="Test NativeScript Application",
        author="Test Author",
        project_type=ProjectType.NATIVESCRIPT,
        output_path=temp_dir / "output",
        parameters={}  # No parameters needed for basic template
    )


def test_nativescript_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.configure_environment.command == 'npm install --legacy-peer-deps'


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization with full NativeScript structure."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    try:
        # Verify output directory structure
        output_dir = project_config.output_path
        assert output_dir.exists()
        
        # Check app structure
        assert (output_dir / "app").exists()
        assert (output_dir / "app" / "app.js").exists()
        assert (output_dir / "app" / "app.css").exists()
        assert (output_dir / "app" / "app-root.xml").exists()
        assert (output_dir / "app" / "home").exists()
        assert (output_dir / "app" / "home" / "home-page.js").exists()
        assert (output_dir / "app" / "home" / "home-page.xml").exists()
        
        # Check resource structure
        assert (output_dir / "App_Resources").exists()
        assert (output_dir / "App_Resources" / "Android").exists()
        assert (output_dir / "App_Resources" / "Android" / "app.gradle").exists()
        assert (output_dir / "App_Resources" / "iOS").exists()
        assert (output_dir / "App_Resources" / "iOS" / "Info.plist").exists()
        
        # Check config files
        assert (output_dir / "package.json").exists()
        assert (output_dir / "nativescript.config.ts").exists()
        assert (output_dir / "hooks").exists()
        
        # Check hidden files
        assert (output_dir / ".gitignore").exists()

        # Verify content replacement
        app_content = (output_dir / "app" / "app.js").read_text()
        assert "test-ns-app" in app_content
        
        package_json = (output_dir / "package.json").read_text()
        assert "test-ns-app" in package_json
        assert "Test Author" in package_json
        assert "Test NativeScript Application" in package_json
        assert "1.0.0" in package_json
        
        # Check platform-specific replacements
        android_manifest = (output_dir / "App_Resources" / "Android" / "src" / "main" / "AndroidManifest.xml").read_text()
        assert "test-ns-app" in android_manifest
        
        ios_plist = (output_dir / "App_Resources" / "iOS" / "Info.plist").read_text()
        assert "test-ns-app" in ios_plist
        
        # Check config file replacements
        ns_config = (output_dir / "nativescript.config.ts").read_text()
        assert "test-ns-app" in ns_config
    finally:
        # Ensure cleanup happens after all checks are complete
        try:
            if project_config.output_path.exists():
                shutil.rmtree(project_config.output_path, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Error cleaning up output directory: {str(e)}")


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "nativescript" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    marker_path = temp_dir / "post_processing_executed"
    # Use curly braces without $ for variable replacement in post-processing script
    config['post_processing']['script'] = f"""#!/bin/bash
    touch {marker_path}
    echo "Project name: {{KAVIA_TEMPLATE_PROJECT_NAME}}" > {marker_path}
    """

    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    assert initializer.wait_for_post_process_completed()
    assert marker_path.exists()
    
    # Check that the post-processing script received the correct variables
    marker_content = Path(marker_path).read_text()
    assert "Project name: test-ns-app" in marker_content


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "nativescript",
        "output_path": str(temp_dir / "output"),
        "parameters": {}  # No parameters needed
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.NATIVESCRIPT
    assert config.description == "Test from JSON config"
    assert config.author == "Test Author"
    assert config.version == "1.0.0"
    assert config.output_path == temp_dir / "output"
    assert config.parameters == {}


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "nativescript" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NATIVESCRIPT, NativeScriptTemplate)
    
    try:
        success = initializer.initialize_project(project_config)
        assert success
        
        output_file = project_config.output_path / "test.txt"
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "test-ns-app" in content
        assert "Test Author" in content
        assert "1.0.0" in content
        assert "Test NativeScript Application" in content
    finally:
        # Make sure we clean up even if assertions fail
        try:
            if project_config.output_path.exists():
                shutil.rmtree(project_config.output_path, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Error cleaning up output directory: {str(e)}")
    assert "Test NativeScript Application" in content
