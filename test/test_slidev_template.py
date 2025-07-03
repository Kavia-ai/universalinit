import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, SlidevTemplate


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
    slidev_path = templates_path / "slidev"
    slidev_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'npm install',
            'working_directory': str(slidev_path)
        },
        'build_cmd': {
            'command': 'npm install && npm run build',
            'working_directory': str(slidev_path)
        },
        'install_dependencies': {
            'command': 'npm install',
            'working_directory': str(slidev_path)
        },
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal Slidev presentation initialized',
        'run_tool': {
            'command': 'npm run dev',
            'working_directory': str(slidev_path)
        },
        'test_tool': {
            'command': 'npm run build',
            'working_directory': str(slidev_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpx prettier --write "**/*.{js,ts,md,vue}"\nPRETTIER_EXIT_CODE=$?\nnpm run build\nBUILD_EXIT_CODE=$?\nif [ $PRETTIER_EXIT_CODE -ne 0 ] || [ $BUILD_EXIT_CODE -ne 0 ]; then\n\t   exit 1\nfi'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(slidev_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (slidev_path / "slides.md").write_text("# ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (slidev_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')
    
    # Create mock components directory and file
    components_dir = slidev_path / "components"
    components_dir.mkdir()
    (components_dir / "Counter.vue").write_text('<template>\n  <div>Counter for ${KAVIA_TEMPLATE_PROJECT_NAME}</div>\n</template>')
    
    # Create mock pages directory and file
    pages_dir = slidev_path / "pages"
    pages_dir.mkdir()
    (pages_dir / "imported-slides.md").write_text('# Imported Slides for ${KAVIA_TEMPLATE_PROJECT_NAME}')
    
    # Create mock netlify.toml and vercel.json (hidden files in production)
    (slidev_path / "netlify.toml").write_text('[build]\n  publish = "dist"\n  command = "npm run build"')
    (slidev_path / "vercel.json").write_text('{\n  "builds": [\n    {\n      "src": "package.json",\n      "use": "@vercel/static-build"\n    }\n  ]\n}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-slidev-deck",
        version="1.0.0",
        description="Test Slidev Presentation",
        author="Test Author",
        project_type=ProjectType.SLIDEV,
        output_path=temp_dir / "output",
        parameters={}  # No custom parameters for Slidev
    )


def test_slidev_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.configure_enviroment.command == 'npm install'


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "slides.md").exists()
    assert (output_dir / "package.json").exists()
    assert (output_dir / "components" / "Counter.vue").exists()
    assert (output_dir / "pages" / "imported-slides.md").exists()
    
    # Verify hidden files were copied
    assert (output_dir / "netlify.toml").exists()
    assert (output_dir / "vercel.json").exists()

    # Verify content replacement
    slides_content = (output_dir / "slides.md").read_text()
    assert "test-slidev-deck" in slides_content

    package_json = (output_dir / "package.json").read_text()
    assert "test-slidev-deck" in package_json
    
    counter_vue = (output_dir / "components" / "Counter.vue").read_text()
    assert "test-slidev-deck" in counter_vue
    
    imported_slides = (output_dir / "pages" / "imported-slides.md").read_text()
    assert "test-slidev-deck" in imported_slides
    
    # Verify deployment config content
    netlify_content = (output_dir / "netlify.toml").read_text()
    assert "dist" in netlify_content
    
    vercel_content = (output_dir / "vercel.json").read_text()
    assert "@vercel/static-build" in vercel_content


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "slidev" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)

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
        "project_type": "slidev",
        "output_path": str(temp_dir / "output"),
        "parameters": {}  # No custom parameters
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.SLIDEV


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "slidev" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SLIDEV, SlidevTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content


def test_slidev_registration():
    """Test that the Slidev template is properly registered and selectable."""
    initializer = ProjectInitializer()
    
    # Check that SLIDEV is registered in the factory
    assert ProjectType.SLIDEV in initializer.template_factory._template_classes
    
    # Create a config with SLIDEV type
    config = ProjectConfig(
        name="test-slidev",
        version="1.0.0",
        description="Test Slidev",
        author="Test Author", 
        project_type=ProjectType.SLIDEV,
        output_path=Path("/tmp/output"),
        parameters={}
    )
    
    # This should not raise an exception if properly registered
    template = initializer.template_factory.create_template(config)
    assert isinstance(template, SlidevTemplate)


def test_slidev_validation():
    """Test that the validate_parameters method works correctly."""
    config = ProjectConfig(
        name="test-slidev-app",
        version="1.0.0",
        description="Test Slidev Application",
        author="Test Author",
        project_type=ProjectType.SLIDEV,
        output_path=Path("/tmp/output"),
        parameters={}  # Empty parameters should be valid for Slidev
    )
    
    template_provider = TemplateProvider()
    template = SlidevTemplate(config, template_provider)
    
    # This should return True since no parameters are required
    assert template.validate_parameters() is True
