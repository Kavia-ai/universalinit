import pytest
import json
from unittest.mock import MagicMock, patch

from universalinit.templateconfig import TemplateInitInfo, RunTool
from universalinit.universalinit import ProjectInitializer
from universalinit.cli import handle_get_run_command, create_minimal_project_config


@pytest.mark.parametrize("project_type,expected_run_command", [
    ("android", "./gradlew installDebug"),
    ("angular", "npm start -- --port <port> --host <host>"),
    ("astro", "npm run dev -- --port <port> --host <host>"),
    ("django", "source venv/bin/activate && python manage.py migrate && python manage.py runserver <host>:<port>"),
    ("dotnet", "dotnet run --urls \"http://<host>:<port>\""),
    ("express", "CI=true PORT=<port> HOST=<host> npm run dev"),
    ("fastapi", "source venv/bin/activate && uvicorn src.api.main:app --host <host> --port <port>"),
    ("flask", "source venv/bin/activate && flask run --host <host> --port <port>"),
    ("springboot", "./gradlew bootRun --args='--server.port=<port> --server.address=<host>'"),
    ("flutter", "flutter run"),
    ("kotlin", "./gradlew installDebug"),
    ("lightningjs", "npm run dev -- --port <port> --host <host>"),
    ("nativescript", "ns run"),
    ("nextjs", "npm run dev -- -p <port> -H <host>"),
    ("nuxt", "npm run dev -- --port <port> --host <host>"),
    ("qwik", "npm run dev -- --port <port> --host <host>"),
    ("react", "PORT=<port> HOST=<host> BROWSER=none npm start"),
    ("remix", "npm run dev -- --port <port> --host <host>"),
    ("remotion", "BROWSER=none npm run dev -- --port <port> --host <host>"),
    ("slidev", "npm run dev -- --force --port <port> --bind <host>"),
    ("svelte", "npm run dev -- --port <port> --host <host>"),
    ("typescript", "npm run dev -- --port <port> --host <host>"),
    ("vite", "npm run dev -- --port <port> --host <host>"),
    ("vue", "npm run dev -- --port <port> --host <host>"),
    ("postgresql", "sudo ./startup.sh && cd db_visualizer && PORT=<port> HOST=<host> BROWSER=none npm start"),
    ("mongodb", "sudo ./startup.sh && cd db_visualizer && PORT=<port> HOST=<host> BROWSER=none npm start"),
    ("mysql", "sudo ./startup.sh && cd db_visualizer && PORT=<port> HOST=<host> BROWSER=none npm start"),
    ("sqlite", "python init_db.py && cd db_visualizer && PORT=<port> HOST=<host> BROWSER=none npm start")
])
def test_get_run_command(project_type, expected_run_command):
    """Test retrieving run commands for different project types."""

    # Test setup
    mock_init_info = MagicMock(spec=TemplateInitInfo)
    mock_init_info.run_tool = RunTool(
        command=expected_run_command,
        working_directory="."
    )
    
    mock_template = MagicMock()
    mock_template.get_init_info.return_value = mock_init_info
    
    mock_factory = MagicMock()
    mock_factory.create_template.return_value = mock_template

    mock_initializer = MagicMock(spec=ProjectInitializer)
    mock_initializer.template_factory = mock_factory
    
    mock_args = MagicMock()
    mock_args.type = project_type
    mock_args.parameters = None

    # Test execution
    with patch('universalinit.cli.ProjectInitializer', return_value=mock_initializer):
        with patch('builtins.print') as mock_print:
            result = handle_get_run_command(mock_args)
            
            # Asserts
            assert result == 0
            
            config = create_minimal_project_config(project_type)
            mock_initializer.template_factory.create_template.assert_called_once()
            mock_template.get_init_info.assert_called_once()
            mock_print.assert_called()
            
            json_output = mock_print.call_args_list[0][0][0]
            try:
                parsed_output = json.loads(json_output)
                assert parsed_output["project_type"] == project_type
                assert parsed_output["run_command"] == expected_run_command
            except json.JSONDecodeError:
                calls = [str(call) for call in mock_print.call_args_list]
                output = ' '.join(calls)
                assert project_type in output
                assert expected_run_command.replace('"', '\\"').replace("'", "\\'") in output
