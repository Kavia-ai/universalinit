import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, RemixTemplate


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
    remix_path = templates_path / "remix"
    remix_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': 'npm install && npm run build',
            'working_directory': str(remix_path)
        },
        'env': {
            'environment_initialized': True,
            'node_version': '18.19.1',
            'npm_version': '9.2.0'
        },
        'init_files': [],
        'init_minimal': 'Minimal Remix application initialized',
        'run_tool': {
            'command': 'npm run dev',
            'working_directory': str(remix_path)
        },
        'test_tool': {
            'command': 'npm test',
            'working_directory': str(remix_path)
        },
        'init_style': '',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpx eslint --fix "$@"'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nnpm install'
        }
    }

    with open(remix_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create some mock template files
    (remix_path / "app").mkdir()
    (remix_path / "app" / "root.tsx").write_text("// ${KAVIA_TEMPLATE_PROJECT_NAME}")
    (remix_path / "app" / "routes").mkdir()
    (remix_path / "app" / "routes" / "_index.tsx").write_text("export default function Index() { return <h1>${KAVIA_TEMPLATE_PROJECT_NAME}</h1>; }")
    (remix_path / "package.json").write_text('{"name": "${KAVIA_TEMPLATE_PROJECT_NAME}"}')
    (remix_path / "tailwind.config.ts").write_text('// Tailwind config for ${KAVIA_TEMPLATE_PROJECT_NAME}')

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-remix-app",
        version="1.0.0",
        description="Test Remix Application",
        author="Test Author",
        project_type=ProjectType.REMIX,
        output_path=temp_dir / "output",
        parameters={
            "typescript": True,
            "styling_solution": "tailwind"
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REMIX, RemixTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "app" / "root.tsx").exists()
    assert (output_dir / "app" / "routes" / "_index.tsx").exists()
    assert (output_dir / "package.json").exists()
    assert (output_dir / "tailwind.config.ts").exists()

    # Verify content replacement
    root_content = (output_dir / "app" / "root.tsx").read_text()
    assert "test-remix-app" in root_content

    index_content = (output_dir / "app" / "routes" / "_index.tsx").read_text()
    assert "test-remix-app" in index_content

    package_json = (output_dir / "package.json").read_text()
    assert "test-remix-app" in package_json


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "remix" / "config.yml"
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
    initializer.template_factory.register_template(ProjectType.REMIX, RemixTemplate)

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
        "project_type": "remix",
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
    assert config.project_type == ProjectType.REMIX
    assert config.parameters["typescript"] is True
    assert config.parameters["styling_solution"] == "tailwind"


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "remix" / "test.txt"
    test_content = """
    Project: ${KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: ${KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REMIX, RemixTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert project_config.name in content
    assert project_config.author in content
    assert project_config.version in content
    assert project_config.description in content


def test_styling_solution_parameter(template_dir, temp_dir):
    """Test that styling_solution parameter is properly validated."""
    # Test with missing styling_solution parameter
    config = ProjectConfig(
        name="test-remix-app",
        version="1.0.0",
        description="Test Remix Application",
        author="Test Author",
        project_type=ProjectType.REMIX,
        output_path=temp_dir / "output",
        parameters={
            "typescript": True
            # Missing styling_solution
        }
    )

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.REMIX, RemixTemplate)

    success = initializer.initialize_project(config)
    assert not success
