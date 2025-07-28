import pytest
from pathlib import Path
import shutil
import tempfile
import yaml
import json

from universalinit.templateconfig import ProjectConfig, ProjectType, TemplateInitInfo
from universalinit.universalinit import ProjectInitializer, TemplateProvider, SpringBootTemplate


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
    springboot_path = templates_path / "springboot"
    springboot_path.mkdir(parents=True)

    # Create mock config.yml
    config = {
        'configure_environment': {
            'command': './gradlew build',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'build_cmd': {
            'command': './gradlew build',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'install_dependencies': {
            'command': './gradlew dependencies',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'env': {
            'environment_initialized': True,
            'java_version': '17',
            'gradle_version': '8.14.3'
        },
        'init_files': [],
        'init_minimal': 'Minimal Spring Boot application initialized',
        'openapi_generation': {
            'command': './gradlew bootRun',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'run_tool': {
            'command': './gradlew bootRun',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': './gradlew test',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'init_style': 'springboot',
        'entry_point_url': 'http://localhost:3000/docs',
        'linter': {
            'script_content': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\n./gradlew checkstyleMain'
        },
        'post_processing': {
            'script': '#!/bin/bash\ncd {KAVIA_PROJECT_DIRECTORY}\nchmod +x ./gradlew\n./gradlew build'
        }
    }

    with open(springboot_path / "config.yml", 'w') as f:
        yaml.dump(config, f)

    # Create mock template files
    (springboot_path / "src").mkdir()
    (springboot_path / "src" / "main").mkdir()
    (springboot_path / "src" / "main" / "java").mkdir()
    (springboot_path / "src" / "main" / "java" / "com").mkdir()
    (springboot_path / "src" / "main" / "java" / "com" / "example").mkdir()
    (springboot_path / "src" / "main" / "java" / "com" / "example" / "demo").mkdir()
    
    # Create main application file
    (springboot_path / "src" / "main" / "java" / "com" / "example" / "demo" / "DemoApplication.java").write_text(
        "package com.example.{KAVIA_TEMPLATE_PROJECT_NAME};\n\n"
        "import org.springframework.boot.SpringApplication;\n"
        "import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
        "@SpringBootApplication\n"
        "public class {KAVIA_TEMPLATE_PROJECT_NAME}Application {\n\n"
        "    public static void main(String[] args) {\n"
        "        SpringApplication.run({KAVIA_TEMPLATE_PROJECT_NAME}Application.class, args);\n"
        "    }\n\n"
        "}"
    )
    
    # Create build.gradle
    (springboot_path / "build.gradle").write_text(
        "plugins {\n"
        "    id 'java'\n"
        "    id 'org.springframework.boot' version '3.4.8'\n"
        "    id 'io.spring.dependency-management' version '1.1.7'\n"
        "}\n\n"
        "group = 'com.example'\n"
        "version = '{KAVIA_PROJECT_VERSION}'\n\n"
        "java {\n"
        "    toolchain {\n"
        "        languageVersion = JavaLanguageVersion.of(17)\n"
        "    }\n"
        "}\n\n"
        "repositories {\n"
        "    mavenCentral()\n"
        "}\n\n"
        "dependencies {\n"
        "    implementation 'org.springframework.boot:spring-boot-starter-actuator'\n"
        "    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'\n"
        "    implementation 'org.springframework.boot:spring-boot-starter-web'\n"
        "    implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0'\n"
        "    developmentOnly 'org.springframework.boot:spring-boot-devtools'\n"
        "    runtimeOnly 'com.h2database:h2'\n"
        "    testImplementation 'org.springframework.boot:spring-boot-starter-test'\n"
        "    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'\n"
        "}\n\n"
        "tasks.named('test') {\n"
        "    useJUnitPlatform()\n"
        "}"
    )
    
    # Create settings.gradle
    (springboot_path / "settings.gradle").write_text("rootProject.name = '{KAVIA_TEMPLATE_PROJECT_NAME}'")
    
    # Create application.properties
    (springboot_path / "src" / "main" / "resources").mkdir(parents=True)
    (springboot_path / "src" / "main" / "resources" / "application.properties").write_text(
        "spring.application.name={KAVIA_TEMPLATE_PROJECT_NAME}\n"
        "server.port=3000\n\n"
        "# H2 Database Configuration\n"
        "spring.datasource.url=jdbc:h2:mem:testdb\n"
        "spring.datasource.driverClassName=org.h2.Driver\n"
        "spring.datasource.username=sa\n"
        "spring.datasource.password=\n"
        "spring.h2.console.enabled=true\n\n"
        "# JPA Configuration\n"
        "spring.jpa.database-platform=org.hibernate.dialect.H2Dialect\n"
        "spring.jpa.hibernate.ddl-auto=create-drop\n"
        "spring.jpa.show-sql=true\n\n"
        "# Actuator Configuration\n"
        "management.endpoints.web.exposure.include=health,info,metrics\n\n"
        "# Swagger/OpenAPI Configuration\n"
        "springdoc.api-docs.path=/api-docs\n"
        "springdoc.swagger-ui.path=/swagger-ui.html\n"
        "springdoc.swagger-ui.operationsSorter=method\n"
        "springdoc.swagger-ui.tagsSorter=alpha"
    )

    return templates_path


@pytest.fixture
def project_config(temp_dir):
    """Create a test project configuration."""
    return ProjectConfig(
        name="test-springboot-app",
        version="1.0.0",
        description="Test Spring Boot Application",
        author="Test Author",
        project_type=ProjectType.SPRINGBOOT,
        output_path=temp_dir / "output",
        parameters={}
    )


def test_springboot_init_info(template_dir, project_config):
    """Test that getting template init info works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    init_info = template.get_init_info()

    # Check that init_info has all required components
    assert isinstance(init_info, TemplateInitInfo)
    assert init_info.build_cmd.command == './gradlew build'
    assert init_info.run_tool.command == './gradlew bootRun'
    assert init_info.test_tool.command == './gradlew test'
    assert init_info.entry_point_url == 'http://localhost:3000/docs'
    assert init_info.env_config.java_version == '17'
    assert init_info.env_config.gradle_version == '8.14.3'


def test_project_initialization(template_dir, project_config):
    """Test basic project initialization."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
    
    # Mock the template to avoid actual file operations
    template = initializer.template_factory.create_template(project_config)
    
    # Test validation
    assert template.validate_parameters() is True


def test_post_processing_execution(template_dir, project_config, temp_dir):
    """Test that post-processing script is executed correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
    
    # Create output directory
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    
    # Mock the template
    template = initializer.template_factory.create_template(project_config)
    
    # Test that post-processing script exists in config
    init_info = template.get_init_info()
    assert init_info.post_processing.script is not None
    assert 'chmod +x ./gradlew' in init_info.post_processing.script
    assert './gradlew build' in init_info.post_processing.script


def test_config_file_loading(temp_dir):
    """Test that config.yml can be loaded correctly."""
    templates_path = temp_dir / "templates"
    springboot_path = templates_path / "springboot"
    springboot_path.mkdir(parents=True)
    
    config = {
        'build_cmd': {
            'command': './gradlew build',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'run_tool': {
            'command': './gradlew bootRun',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'test_tool': {
            'command': './gradlew test',
            'working_directory': '{KAVIA_PROJECT_DIRECTORY}'
        },
        'env': {
            'environment_initialized': True,
            'java_version': '17',
            'gradle_version': '8.14.3'
        },
        'entry_point_url': 'http://localhost:3000/docs'
    }
    
    with open(springboot_path / "config.yml", 'w') as f:
        yaml.dump(config, f)
    
    # Test that config can be loaded
    with open(springboot_path / "config.yml", 'r') as f:
        loaded_config = yaml.safe_load(f)
    
    assert loaded_config['build_cmd']['command'] == './gradlew build'
    assert loaded_config['run_tool']['command'] == './gradlew bootRun'
    assert loaded_config['test_tool']['command'] == './gradlew test'
    assert loaded_config['env']['java_version'] == '17'
    assert loaded_config['entry_point_url'] == 'http://localhost:3000/docs'


def test_template_variable_replacement(template_dir, project_config):
    """Test that template variables are replaced correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    # Test variable replacement
    replacements = project_config.get_replaceable_parameters()
    
    assert replacements['KAVIA_TEMPLATE_PROJECT_NAME'] == 'testspringbootapp'
    assert replacements['KAVIA_PROJECT_VERSION'] == '1.0.0'
    assert replacements['KAVIA_PROJECT_AUTHOR'] == 'Test Author'
    assert replacements['KAVIA_PROJECT_DESCRIPTION'] == 'Test Spring Boot Application'


def test_springboot_template_structure(template_dir, project_config):
    """Test that Spring Boot template has correct structure."""
    springboot_path = template_dir / "springboot"
    
    # Check essential files exist
    assert (springboot_path / "config.yml").exists()
    assert (springboot_path / "build.gradle").exists()
    assert (springboot_path / "settings.gradle").exists()
    assert (springboot_path / "src" / "main" / "resources" / "application.properties").exists()
    assert (springboot_path / "src" / "main" / "java" / "com" / "example" / "demo" / "DemoApplication.java").exists()


def test_springboot_template_content(template_dir, project_config):
    """Test that template files contain expected content."""
    springboot_path = template_dir / "springboot"
    
    # Check build.gradle content
    build_gradle_content = (springboot_path / "build.gradle").read_text()
    assert 'org.springframework.boot' in build_gradle_content
    assert 'spring-boot-starter-web' in build_gradle_content
    assert 'spring-boot-starter-data-jpa' in build_gradle_content
    assert 'springdoc-openapi-starter-webmvc-ui' in build_gradle_content
    
    # Check application.properties content
    app_props_content = (springboot_path / "src" / "main" / "resources" / "application.properties").read_text()
    assert 'spring.application.name={KAVIA_TEMPLATE_PROJECT_NAME}' in app_props_content
    assert 'server.port=3000' in app_props_content
    assert 'spring.h2.console.enabled=true' in app_props_content
    
    # Check main application class
    app_class_content = (springboot_path / "src" / "main" / "java" / "com" / "example" / "demo" / "DemoApplication.java").read_text()
    assert '@SpringBootApplication' in app_class_content
    assert '{KAVIA_TEMPLATE_PROJECT_NAME}Application' in app_class_content


def test_springboot_template_validation(template_dir, project_config):
    """Test that Spring Boot template validation works correctly."""
    initializer = ProjectInitializer()
    initializer.template_factory.template_provider = TemplateProvider(template_dir)
    initializer.template_factory.register_template(ProjectType.SPRINGBOOT, SpringBootTemplate)
    template = initializer.template_factory.create_template(project_config)
    
    # Test validation - Spring Boot doesn't require specific parameters
    assert template.validate_parameters() is True
    
    # Test with different parameters
    project_config.parameters = {'java_version': '21', 'gradle_version': '8.5'}
    template = initializer.template_factory.create_template(project_config)
    assert template.validate_parameters() is True 