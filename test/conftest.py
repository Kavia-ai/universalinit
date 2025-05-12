import pytest
from pathlib import Path
import shutil
import tempfile
import os

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs.
    
    This is a shared fixture that handles cleanup more robustly,
    particularly for GitHub Actions environments where permissions
    or file locking might cause issues.
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    try:
        # First attempt: standard cleanup
        shutil.rmtree(temp_path, ignore_errors=True)
    except OSError as e:
        # Second attempt: if standard cleanup fails, try to force remove files
        print(f"Warning: Error cleaning up directory {temp_path}: {str(e)}")
        try:
            # Make all files writable first
            for root, dirs, files in os.walk(temp_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.chmod(file_path, 0o666)
                    except:
                        pass
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        os.chmod(dir_path, 0o777)
                    except:
                        pass
            
            # Try rmtree again
            shutil.rmtree(temp_path, ignore_errors=True)
        except:
            print(f"Warning: Failed to remove temporary directory {temp_path}, continuing anyway")
