"""
Test file for MongoDB template functionality.

Minimal tests focusing on template generation and variable replacement.
No Docker execution required.
"""
import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, MongoDBTemplate


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
    mongodb_path = templates_path / "mongodb"
    mongodb_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': 'docker compose up -d || docker-compose up -d',
            'working_directory': str(mongodb_path)
        },
        'env': {
            'environment_initialized': True,
            'docker_version': '20.10.0'
        },
        'init_files': [],
        'init_minimal': 'MongoDB database initialized',
        'run_tool': {
            'command': 'docker compose up || docker-compose up',
            'working_directory': str(mongodb_path)
        },
        'test_tool': {
            'command': 'docker compose exec -T mongo mongosh --eval "db.version()"',
            'working_directory': str(mongodb_path)
        },
        'init_style': 'database',
        'entry_point_url': 'mongodb://localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}',
        'linter': {
            'script_content': '#!/bin/bash\necho "No linting required for database configuration"'
        },
        'pre_processing': {
            'script': ''
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\necho "MongoDB ready to start with: docker compose up -d"'
        }
    }

    with open(mongodb_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create docker-compose.yml template
    docker_compose_content = '''version: '3.8'
services:
  mongo:
    image: mongo:6-jammy
    container_name: {KAVIA_TEMPLATE_PROJECT_NAME}_mongo
    ports:
      - "{KAVIA_DB_PORT}:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: {KAVIA_DB_NAME}

volumes:
  mongo_data:
'''
    (mongodb_path / "docker-compose.yml").write_text(docker_compose_content)

    # Create README.md template
    readme_content = '''# {KAVIA_TEMPLATE_PROJECT_NAME} MongoDB Database

## Overview
This is a MongoDB database project created by {KAVIA_PROJECT_AUTHOR}.

## Quick Start
```bash
# Start the database
docker compose up -d

# Connect to MongoDB shell
docker compose exec mongo mongosh {KAVIA_DB_NAME}

# Stop the database
docker compose down
```

## Connection Details
- Host: localhost
- Port: {KAVIA_DB_PORT}
- Database: {KAVIA_DB_NAME}

## Connection String
```
mongodb://localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}
```
'''
    (mongodb_path / "README.md").write_text(readme_content)

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-mongo-db",
        version="1.0.0",
        description="Test MongoDB Database",
        author="Test Author",
        project_type=ProjectType.MONGODB,
        output_path=temp_dir / "output",
        parameters={
            'database_name': 'test_db',
            'database_port': 27018
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "docker-compose.yml").exists()
    assert (output_dir / "README.md").exists()

    # Verify content replacement in docker-compose.yml
    docker_compose_content = (output_dir / "docker-compose.yml").read_text()
    assert 'test_db' in docker_compose_content
    assert '27018' in docker_compose_content
    assert 'test-mongo-db' in docker_compose_content

    # Verify README content
    readme_content = (output_dir / "README.md").read_text()
    assert 'test-mongo-db' in readme_content
    assert 'Test Author' in readme_content


def test_default_parameters(template_dir, temp_dir):
    """Test that default parameters are applied correctly."""
    config = ProjectConfig(
        name="default-mongo",
        version="1.0.0",
        description="Test default parameters",
        author="Test Author",
        project_type=ProjectType.MONGODB,
        output_path=temp_dir / "output",
        parameters={}  # No custom parameters
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    success = initializer.initialize_project(config)
    assert success
    
    # Check docker-compose.yml for default values
    docker_compose_content = (config.output_path / "docker-compose.yml").read_text()
    
    # Defaults should be: dbname=default_mongo, port=27017
    assert 'default_mongo' in docker_compose_content
    assert '27017' in docker_compose_content


def test_mongodb_without_auth(template_dir, project_config):
    """Test that MongoDB template works without authentication by default."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    template = initializer.template_factory.create_template(project_config)
    replacements = project_config.get_replaceable_parameters()
    
    # MongoDB can run without authentication
    # The current implementation uses default 'dbuser' which should be ignored for MongoDB
    assert 'KAVIA_DB_USER' in replacements
    assert 'KAVIA_DB_PASSWORD' in replacements


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "mongodb",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "database_name": "json_db",
            "database_port": 27019
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.MONGODB
    assert config.parameters["database_name"] == "json_db"
    assert config.parameters["database_port"] == 27019


def test_entry_point_url(template_dir, project_config):
    """Test that the entry point URL is correctly generated."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    template = initializer.template_factory.create_template(project_config)
    init_info = template.get_init_info()
    
    # Check if URL contains the expected values
    assert 'mongodb://' in init_info.entry_point_url
    assert '27018' in init_info.entry_point_url
    assert 'test_db' in init_info.entry_point_url


def test_docker_compose_yaml_structure(template_dir, project_config):
    """Test that docker-compose.yml has valid YAML structure."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # Load and parse the docker-compose.yml
    docker_compose_path = project_config.output_path / "docker-compose.yml"
    with open(docker_compose_path, 'r') as f:
        docker_config = yaml.safe_load(f)
    
    # Verify structure
    assert 'services' in docker_config
    assert 'mongo' in docker_config['services']
    assert 'ports' in docker_config['services']['mongo']
    assert 'environment' in docker_config['services']['mongo']
    assert 'MONGO_INITDB_DATABASE' in docker_config['services']['mongo']['environment']
    assert 'volumes' in docker_config


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "mongodb" / "test.txt"
    test_content = """
    Project: {KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: {KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    Database: {KAVIA_DB_NAME}
    Port: {KAVIA_DB_PORT}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert 'test-mongo-db' in content
    assert 'Test Author' in content
    assert '1.0.0' in content
    assert 'test_db' in content
    assert '27018' in content


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "mongodb" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    marker_path = temp_dir / "post_processing_executed"
    config['post_processing']['script'] = f"""#!/bin/bash
    touch {marker_path}
    echo "test-mongo-db" > {marker_path}
    """

    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MONGODB, MongoDBTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # Wait for post-processing
    assert initializer.wait_for_post_process_completed(timeout=10)
    
    # Check marker file
    assert marker_path.exists()
    assert marker_path.read_text().strip() == "test-mongo-db"