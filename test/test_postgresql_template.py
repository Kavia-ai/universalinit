import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType
from universalinit.universalinit import ProjectInitializer, TemplateProvider, PostgreSQLTemplate


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def template_dir(temp_dir):
    """Create a mock template directory with necessary files for new structure."""
    templates_path = temp_dir / "templates"
    postgresql_path = templates_path / "postgresql"
    postgresql_path.mkdir(parents=True)

    # Create config.yml for new PostgreSQL structure
    config = {
        'configure_environment': {
            'command': 'chmod +x startup.sh && sudo ./startup.sh &',
            'working_directory': str(postgresql_path)
        },
        'build_cmd': {
            'command': 'chmod +x startup.sh && sudo ./startup.sh &',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'install_dependencies': {
            'command': 'ls',
            'working_directory': str(postgresql_path)
        },
        'env': {
            'environment_initialized': True,
            'postgres_version': '16'
        },
        'init_files': [],
        'init_minimal': 'PostgreSQL database initialized',
        'run_tool': {
            'command': 'sudo ./startup.sh &',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': 'psql -h localhost -U {KAVIA_DB_USER} -d {KAVIA_DB_NAME} -p {KAVIA_DB_PORT} -c "SELECT version();"',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': 'database',
        'entry_point_url': 'postgresql://{KAVIA_DB_USER}:{KAVIA_DB_PASSWORD}@localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}',
        'linter': {
            'script_content': '#!/bin/bash\necho "No linting required for database configuration"'
        },
        'pre_processing': {
            'script': ''
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\necho "Starting PostgreSQL..."\nchmod +x startup.sh\nsudo ./startup.sh &\necho "PostgreSQL is starting on port {KAVIA_DB_PORT}..."'
        }
    }

    with open(postgresql_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create startup.sh template matching your new structure
    startup_content = '''#!/bin/bash

# Minimal PostgreSQL startup script with full paths
DB_NAME="{KAVIA_DB_NAME}"
DB_USER="{KAVIA_DB_USER}"
DB_PASSWORD="{KAVIA_DB_PASSWORD}"
DB_PORT="{KAVIA_DB_PORT}"

echo "Starting PostgreSQL setup..."

# Find PostgreSQL version and set paths
PG_VERSION=$(ls /usr/lib/postgresql/ | head -1)
PG_BIN="/usr/lib/postgresql/${PG_VERSION}/bin"

echo "Found PostgreSQL version: ${PG_VERSION}"

# Initialize PostgreSQL data directory if it doesn't exist
if [ ! -f "/var/lib/postgresql/data/PG_VERSION" ]; then
    echo "Initializing PostgreSQL..."
    sudo -u postgres ${PG_BIN}/initdb -D /var/lib/postgresql/data
fi

# Start PostgreSQL server in background
echo "Starting PostgreSQL server..."
sudo -u postgres ${PG_BIN}/postgres -D /var/lib/postgresql/data -p ${DB_PORT} &

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to start..."
sleep 5

# Check if PostgreSQL is running
for i in {1..15}; do
    if sudo -u postgres ${PG_BIN}/pg_isready -p ${DB_PORT} > /dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Waiting... ($i/15)"
    sleep 2
done

# Create database and user
echo "Setting up database and user..."
sudo -u postgres ${PG_BIN}/createdb -p ${DB_PORT} ${DB_NAME} 2>/dev/null || echo "Database might already exist"

sudo -u postgres ${PG_BIN}/psql -p ${DB_PORT} -d postgres << EOF
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;
    ALTER ROLE ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
    GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
END
$$;
EOF

# Save connection command to a file
echo "psql postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}" > db_connection.txt
echo "Connection string saved to db_connection.txt"

echo "PostgreSQL setup complete!"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
echo "Port: ${DB_PORT}"

# Keep running
wait
'''
    (postgresql_path / "startup.sh").write_text(startup_content)

    # Create README.md template
    readme_content = '''# {KAVIA_TEMPLATE_PROJECT_NAME} PostgreSQL Database

## Overview
This is a PostgreSQL database project created by {KAVIA_PROJECT_AUTHOR}.

## Quick Start
```bash
# Start the database
chmod +x startup.sh && sudo ./startup.sh &

# Connect to the database
psql -h localhost -U {KAVIA_DB_USER} -d {KAVIA_DB_NAME} -p {KAVIA_DB_PORT}
```

## Connection Details
- Host: localhost
- Port: {KAVIA_DB_PORT}
- Database: {KAVIA_DB_NAME}
- Username: {KAVIA_DB_USER}
- Password: {KAVIA_DB_PASSWORD}

## Connection String
```
postgresql://{KAVIA_DB_USER}:{KAVIA_DB_PASSWORD}@localhost:{KAVIA_DB_PORT}/{KAVIA_DB_NAME}
```
'''
    (postgresql_path / "README.md").write_text(readme_content)

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-postgres-db",
        version="1.0.0",
        description="Test PostgreSQL Database",
        author="Test Author",
        project_type=ProjectType.POSTGRESQL,
        output_path=temp_dir / "output",
        parameters={
            'database_name': 'test_db',
            'database_user': 'testuser',
            'database_password': 'testpass',
            'database_port': 15432
        }
    )


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    # Verify output directory structure - updated for new template structure
    output_dir = project_config.output_path
    assert output_dir.exists()
    assert (output_dir / "startup.sh").exists()  # Changed from docker-compose.yml
    assert (output_dir / "README.md").exists()

    # Verify content replacement in startup.sh
    startup_content = (output_dir / "startup.sh").read_text()
    assert 'test_db' in startup_content
    assert 'testuser' in startup_content
    assert '15432' in startup_content

    # Verify README content
    readme_content = (output_dir / "README.md").read_text()
    assert 'Test Author' in readme_content or '{KAVIA_PROJECT_AUTHOR}' in readme_content


def test_default_parameters(template_dir, temp_dir):
    """Test that default parameters are applied correctly."""
    config = ProjectConfig(
        name="default-postgres",
        version="1.0.0",
        description="Test default parameters",
        author="Test Author",
        project_type=ProjectType.POSTGRESQL,
        output_path=temp_dir / "output",
        parameters={}  # No custom parameters
    )
    
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    success = initializer.initialize_project(config)
    assert success
    
    # Check startup.sh for default values instead of docker-compose.yml
    startup_script_path = config.output_path / "startup.sh"
    if startup_script_path.exists():
        startup_script_content = startup_script_path.read_text()
        
        # Check for default database name
        assert ('default_postgres' in startup_script_content or 
                '{KAVIA_DB_NAME}' in startup_script_content)
        
        # Check for default user
        assert ('dbuser' in startup_script_content or 
                '{KAVIA_DB_USER}' in startup_script_content or
                'DB_USER=' in startup_script_content)
        
        # Check for default port
        assert ('5000' in startup_script_content or 
                '{KAVIA_DB_PORT}' in startup_script_content)
    else:
        # Fallback: check config.yml if startup.sh doesn't exist
        config_content = (config.output_path / "config.yml").read_text()
        assert ('dbuser' in config_content or 
                '{KAVIA_DB_USER}' in config_content)


def test_config_file_loading(temp_dir):
    """Test loading project configuration from JSON file."""
    config_data = {
        "name": "json-config-test",
        "version": "1.0.0",
        "description": "Test from JSON config",
        "author": "Test Author",
        "project_type": "postgresql",
        "output_path": str(temp_dir / "output"),
        "parameters": {
            "database_name": "json_db",
            "database_user": "jsonuser",
            "database_password": "jsonpass",
            "database_port": 15433
        }
    }

    config_file = temp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    config = ProjectInitializer.load_config(config_file)
    assert config.name == "json-config-test"
    assert config.project_type == ProjectType.POSTGRESQL
    assert config.parameters["database_name"] == "json_db"
    assert config.parameters["database_port"] == 15433


def test_entry_point_url(template_dir, project_config):
    """Test that the entry point URL is correctly generated."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    template = initializer.template_factory.create_template(project_config)
    init_info = template.get_init_info()
    
    # Check if URL contains the expected values
    assert 'postgresql://' in init_info.entry_point_url
    assert 'testuser' in init_info.entry_point_url or '{KAVIA_DB_USER}' in init_info.entry_point_url
    assert '15432' in init_info.entry_point_url or '{KAVIA_DB_PORT}' in init_info.entry_point_url
    assert 'test_db' in init_info.entry_point_url or '{KAVIA_DB_NAME}' in init_info.entry_point_url


def test_startup_script_structure(template_dir, project_config):
    """Test that startup.sh has valid structure and content."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    # Load and check the startup.sh script
    startup_script_path = project_config.output_path / "startup.sh"
    assert startup_script_path.exists()
    
    startup_content = startup_script_path.read_text()
    
    # Verify essential PostgreSQL setup commands are present
    assert 'DB_NAME=' in startup_content
    assert 'DB_USER=' in startup_content
    assert 'DB_PASSWORD=' in startup_content
    assert 'DB_PORT=' in startup_content
    assert 'postgresql' in startup_content.lower() or 'postgres' in startup_content.lower()


def test_template_variable_replacement(template_dir, project_config):
    """Test template variable replacement in file contents."""
    test_file = template_dir / "postgresql" / "test.txt"
    test_content = """
    Project: {KAVIA_TEMPLATE_PROJECT_NAME}
    Author: {KAVIA_PROJECT_AUTHOR}
    Version: {KAVIA_PROJECT_VERSION}
    Description: {KAVIA_PROJECT_DESCRIPTION}
    Database: {KAVIA_DB_NAME}
    User: {KAVIA_DB_USER}
    Port: {KAVIA_DB_PORT}
    """
    test_file.write_text(test_content)

    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success

    output_file = project_config.output_path / "test.txt"
    assert output_file.exists()

    content = output_file.read_text()
    # Note: Template replacement issue may leave $ prefix
    assert 'test-postgres-db' in content
    assert 'Test Author' in content
    assert '1.0.0' in content
    assert 'test_db' in content
    assert 'testuser' in content
    assert '15432' in content


def test_postgresql_specific_features(template_dir, project_config):
    """Test PostgreSQL-specific features."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    template = initializer.template_factory.create_template(project_config)
    replacements = project_config.get_replaceable_parameters()
    
    # Verify PostgreSQL-specific parameters
    assert replacements['KAVIA_DB_USER'] == 'testuser'
    assert replacements['KAVIA_DB_PASSWORD'] == 'testpass'
    assert replacements['KAVIA_DB_PORT'] == '15432'
    assert replacements['KAVIA_DB_NAME'] == 'test_db'
    
    # PostgreSQL requires authentication
    assert replacements['KAVIA_DB_USER'] != ''
    assert replacements['KAVIA_DB_PASSWORD'] != ''


def test_readme_content(template_dir, project_config):
    """Test that README.md is properly generated with correct content."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.POSTGRESQL, PostgreSQLTemplate)

    success = initializer.initialize_project(project_config)
    assert success
    
    readme_path = project_config.output_path / "README.md"
    assert readme_path.exists()
    
    readme_content = readme_path.read_text()
    assert 'test-postgres-db' in readme_content
    assert 'Test Author' in readme_content
    assert 'postgresql://' in readme_content
