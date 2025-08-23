import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

# Helper to run CLI commands
CLI = sys.executable + " -m fastapi_start_project.cli"

@pytest.fixture(scope="module")
def temp_project_dir():
    d = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(d)
    yield d
    os.chdir(cwd)
    shutil.rmtree(d)

def test_create_app_simple(temp_project_dir):
    # Test: create-app
    result = subprocess.run([sys.executable, '-m', 'fastapi_start_project.cli', 'create-app', 'MyApp'], capture_output=True, text=True)
    assert result.returncode == 0
    assert Path('MyApp').exists()
    assert (Path('MyApp') / 'main.py').exists()
    assert (Path('MyApp') / 'models.py').exists() or (Path('MyApp') / 'models' / '__init__.py').exists()
    assert 'Project MyApp created successfully!' in result.stdout

def test_add_entity(temp_project_dir):
    # Setup: create simple app
    subprocess.run([sys.executable, '-m', 'fastapi_start_project.cli', 'create-app', 'TestApp'], check=True)
    # Test: add-entity
    result = subprocess.run([sys.executable, '-m', 'fastapi_start_project.cli', 'add-entity', 'TestApp', 'User'], capture_output=True, text=True)
    assert result.returncode == 0
    models = (Path('TestApp') / 'models.py').read_text(encoding='utf-8')
    schemas = (Path('TestApp') / 'schemas.py').read_text(encoding='utf-8')
    assert 'class User(Base):' in models
    assert 'class UserSchema(BaseModel):' in schemas
    assert 'Entity User added to TestApp!' in result.stdout

# Note: Interactive create-project is not tested here due to CLI prompt complexity.
# For full coverage, use a CLI automation tool like pexpect or Typer's test runner.
