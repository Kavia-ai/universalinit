"""
Test file for MySQL template functionality.

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
from universalinit.universalinit import ProjectInitializer, TemplateProvider, MySQLTemplate


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
    mysql_path = templates_path / "mysql"
    mysql_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'build_cmd': {
            'command': 'docker compose up -d || docker-compose up -d',
            'working_directory': str(mysql_path)
        },
        'env': {
            'environment_initialized': True,
            'docker_version': '20.10.0'
        },
        'init_files': [],
        'init_minimal': 'MySQL database initialized',
        'run_tool': {
            'command': 'docker compose up || docker-compose up',
            'working_directory': str(mysql_path)
        },
        'test_tool': {
            'command': 'docker compose exec -T mysql mysql -u{KAVIA_DB_USER} -p{KAVIA_DB_PASSWORD} -e "SHOW DATABASES;"',
            'working_directory': str(mysql_path)
        },
        'init_style': 'database',
        'entry_point_url': 'mysql://{KAVIA_DB_USER}:{KAVIA_DB_PASSWORD}@localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}',
        'linter': {
            'script_content': '#!/bin/bash\necho "No linting required for database configuration"'
        },
        'pre_processing': {
            'script': ''
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\necho "MySQL ready to start with: docker compose up -d"'
        }
    }

    with open(mysql_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create docker-compose.yml template
    docker_compose_content = '''version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: {KAVIA_TEMPLATE_PROJECT_NAME}_mysql
    environment:
      MYSQL_ROOT_PASSWORD: {KAVIA_DB_PASSWORD}
      MYSQL_DATABASE: {KAVIA_DB_NAME}
    ports:
      - "{KAVIA_DB_PORT}:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
'''
    (mysql_path / "docker-compose.yml").write_text(docker_compose_content)

    # Create README.md template
    readme_content = '''# {KAVIA_TEMPLATE_PROJECT_NAME} MySQL Database

## Overview
This is a MySQL database project created by {KAVIA_PROJECT_AUTHOR}.

## Quick Start
```bash
# Start the database
docker compose up -d

# Connect to the database
docker compose exec mysql mysql -u{KAVIA_DB_USER} -p{KAVIA_DB_PASSWORD} {KAVIA_DB_NAME}

# Stop the database
docker compose down
```

## Connection Details
- Host: localhost
- Port: {KAVIA_DB_PORT}
- Database: {KAVIA_DB_NAME}
- Username: {KAVIA_DB_USER}
- Password: {KAVIA_DB_PASSWORD}

## Connection String
```
mysql://{KAVIA_DB_USER}:{KAVIA_DB_PASSWORD}@localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}
```
'''
    (mysql_path / "README.md").write_text(readme_content)

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-mysql-db",
        version="1.0.0",
        description="Test MySQL Database",
        author="Test Author",
        project_type=ProjectType.MYSQL,
        output_path=temp_dir / "output",
        parameters={
            'database_name': 'test_db',
            'database_user': 'root',
            'database_password': 'testpass',
            'database_port': 13306
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

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
    assert 'testpass' in docker_compose_content
    assert '13306' in docker_compose_content
    assert 'test-mysql-db' in docker_compose_content

    # Verify README content
    readme_content = (output_dir / "README.md").read_text()
    assert 'test-mysql-db' in readme_content
    assert 'Test Author' in readme_content
    assert 'root' in readme_content


def test_default_parameters(template_dir, temp_dir):
    """Test that default parameters are applied correctly."""
    config = ProjectConfig(
        name="default-mysql",
        version="1.0.0",
        description="Test default parameters",
        author="Test Author",
        project_type=ProjectType.MYSQL,
        output_path=temp_dir / "output",
        parameters={}  # No custom parameters
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    success = initializer.initialize_project(config)
    assert success
    
    # Check docker-compose.yml for default values
    docker_compose_content = (config.output_path / "docker-compose.yml").read_text()
    
    # Defaults should be: dbname=default_mysql, user=root, password=dbpass, port=3306
    assert 'default_mysql' in docker_compose_content
    assert '3306' in docker_compose_content


def test_mysql_root_user(template_dir, project_config):
    """Test that MySQL uses root user by default."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    template = initializer.template_factory.create_template(project_config)
    replacements = project_config.get_replaceable_parameters()
    
    # MySQL should use root user
    assert replacements['KAVIA_DB_USER'] == 'root'
    assert replacements['KAVIA_DB_PASSWORD'] == 'testpass'


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "mysql",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "database_name": "json_db",
            "database_user": "jsonuser",
            "database_password": "jsonpass",
            "database_port": 13307
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.MYSQL
    assert config.parameters["database_name"] == "json_db"
    assert config.parameters["database_port"] == 13307


def test_entry_point_url(template_dir, project_config):
    """Test that the entry point URL is correctly generated."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    template = initializer.template_factory.create_template(project_config)
    init_info = template.get_init_info()
    
    # Check if URL contains the expected values
    assert 'mysql://' in init_info.entry_point_url
    assert 'root' in init_info.entry_point_url
    assert '13306' in init_info.entry_point_url
    assert 'test_db' in init_info.entry_point_url


def test_docker_compose_yaml_structure(template_dir, project_config):
    """Test that docker-compose.yml has valid YAML structure."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # Load and parse the docker-compose.yml
    docker_compose_path = project_config.output_path / "docker-compose.yml"
    with open(docker_compose_path, 'r') as f:
        docker_config = yaml.safe_load(f)
    
    # Verify structure
    assert 'services' in docker_config
    assert 'mysql' in docker_config['services']
    assert 'environment' in docker_config['services']['mysql']
    assert 'MYSQL_ROOT_PASSWORD' in docker_config['services']['mysql']['environment']
    assert 'MYSQL_DATABASE' in docker_config['services']['mysql']['environment']
    assert 'ports' in docker_config['services']['mysql']
    assert 'volumes' in docker_config


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "mysql" / "test.txt"
    test_content = """
    Project: {KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: {KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    Database: {KAVIA_DB_NAME}
    User: {KAVIA_DB_USER}
    Password: {KAVIA_DB_PASSWORD}
    Port: {KAVIA_DB_PORT}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    assert 'test-mysql-db' in content
    assert 'Test Author' in content
    assert '1.0.0' in content
    assert 'test_db' in content
    assert 'root' in content
    assert 'testpass' in content
    assert '13306' in content


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed."""
    # Create a test post-processing script that creates a marker file
    config_path = template_dir / "mysql" / "config.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    marker_path = temp_dir / "post_processing_executed"
    config['post_processing']['script'] = f"""#!/bin/bash
    touch {marker_path}
    echo "test-mysql-db" > {marker_path}
    """

    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # Wait for post-processing
    assert initializer.wait_for_post_process_completed(timeout=10)
    
    # Check marker file
    assert marker_path.exists()
    assert marker_path.read_text().strip() == "test-mysql-db"


def test_mysql_specific_features(template_dir, project_config):
    """Test MySQL-specific features."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.MYSQL, MySQLTemplate)

    # Test that MySQL template handles root password properly
    docker_compose_path = project_config.output_path / "docker-compose.yml"
    success = initializer.initialize_project(project_config)
    assert success
    
    docker_compose_content = docker_compose_path.read_text()
    # MySQL uses the same password for root as specified in parameters
    assert 'MYSQL_ROOT_PASSWORD' in docker_compose_content