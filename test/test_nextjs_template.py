import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, NextJSTemplate


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
    nextjs_path = templates_path / "nextjs"
    nextjs_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': 'npm install',
            'working_directory': str(nextjs_path)
        },
        'build_cmd': {
            'command': 'npm install && npm run lint && npm run test',
            'working_directory': str(nextjs_path)
        },
        'install_dependencies': {
            'command': 'npm install',
            'working_directory': str(nextjs_path)
        },
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal NextJS application initialized',
        'run_tool': {
            'command': 'npm run dev',
            'working_directory': str(nextjs_path)
        },
        'test_tool': {
            'command': 'npm run test',
            'working_directory': str(nextjs_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpx eslint "$@"\nESLINT_EXIT_CODE=$?\nnpm run build\nBUILD_EXIT_CODE=$?\nif [ $ESLINT_EXIT_CODE -ne 0 ] || [ $BUILD_EXIT_CODE -ne 0 ]; then\n\t   exit 1\nfi'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(nextjs_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (nextjs_path / "src").mkdir(parents=True)
    (nextjs_path / "src" / "app").mkdir()
    (nextjs_path / "src" / "app" / "page.tsx").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (nextjs_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')
    
    # Create mock hidden files to test proper inclusion
    (nextjs_path / ".gitignore").write_text("node_modules\n.next\n")
    (nextjs_path / ".eslintrc.json").write_text('{"extends": "next/core-web-vitals"}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-nextjs-app",
        version="1.0.0",
        description="Test NextJS Application",
        author="Test Author",
        project_type=ProjectType.NEXTJS,
        output_path=temp_dir / "output",
        parameters={
            "typescript": True,
            "styling_solution": "tailwind"
        }
    )


def test_nextjs_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.configure_environment.command == 'npm install'


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "src" / "app" / "page.tsx").exists()
    assert (output_dir / "package.json").exists()

    # Verify content replacement
    page_content = (output_dir / "src" / "app" / "page.tsx").read_text()
    assert "test-nextjs-app" in page_content

    package_json = (output_dir / "package.json").read_text()
    assert "test-nextjs-app" in package_json
    
    # Verify hidden files are included
    assert (output_dir / ".gitignore").exists()
    assert (output_dir / ".eslintrc.json").exists()


def test_parameter_defaults(template_dir, temp_dir):
    """Test that NextJS template applies parameter defaults correctly."""
    # Create config with no parameters
    project_config = ProjectConfig(
        name="test-nextjs-app",
        version="1.0.0",
        description="Test NextJS Application",
        author="Test Author",
        project_type=ProjectType.NEXTJS,
        output_path=temp_dir / "output",
        parameters={}  # Empty parameters to test defaults
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # After initialization, parameters should have defaults
    assert project_config.parameters["typescript"] is True
    assert project_config.parameters["styling_solution"] == "css"


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "nextjs" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)

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
        "project_type": "nextjs",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "typescript": True,
            "styling_solution": "tailwind"
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.NEXTJS
    assert config.parameters["typescript"] is True
    assert config.parameters["styling_solution"] == "tailwind"


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "nextjs" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    TypeScript: ${KAVIA_USE_TYPESCRIPT}
    Styling: ${KAVIA_STYLING_SOLUTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.NEXTJS, NextJSTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content
    assert "true" in content  # TypeScript parameter
    assert "tailwind" in content  # Styling solution parameter
