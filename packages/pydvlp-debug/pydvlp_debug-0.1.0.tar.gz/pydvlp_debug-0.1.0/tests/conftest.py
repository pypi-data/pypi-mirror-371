"""Pytest configuration and fixtures for pydvlp-debug tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clear pydvlp-related environment variables
    for key in list(os.environ.keys()):
        if key.startswith("PYDVLP_"):
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_python_file(tmp_path):
    """Create a temporary Python file for testing."""
    def _create_file(content: str, name: str = "test_file.py") -> Path:
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path
    
    return _create_file


@pytest.fixture
def sample_code():
    """Provide sample Python code for testing."""
    return {
        "simple_function": '''
def simple_function(x):
    """A simple function."""
    return x + 1
''',
        "complex_function": '''
def complex_function(x, y, z):
    """A complex function with branches."""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        for i in range(z):
            y += i
        return y
    else:
        return 0
''',
        "class_with_methods": '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        self.result = x + y
        return self.result
    
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        self.result = x * y
        return self.result
''',
        "typed_function": '''
from typing import List, Optional

def process_data(
    items: List[str],
    prefix: Optional[str] = None
) -> List[str]:
    """Process a list of items with optional prefix."""
    if prefix:
        return [f"{prefix}_{item}" for item in items]
    return items
''',
    }


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    from pydvlp.debug.config import DevConfig, Environment
    
    return DevConfig(
        enabled=True,
        environment=Environment.TESTING,
        debug_enabled=True,
        log_enabled=True,
        trace_enabled=True,
        profile_enabled=True,
        benchmark_enabled=True,
        static_analysis_enabled=True,
        verbose=False,
    )


@pytest.fixture
def capture_rich_output():
    """Capture Rich console output."""
    from io import StringIO
    from rich.console import Console
    
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    
    return console, output


@pytest.fixture
def disable_rich_output(monkeypatch):
    """Disable Rich output for cleaner test output."""
    monkeypatch.setenv("PYDVLP_DEBUG_FORMAT", "plain")
    

@pytest.fixture
def isolated_imports():
    """Ensure imports are isolated between tests."""
    # Store original modules
    original_modules = sys.modules.copy()
    
    yield
    
    # Remove any modules imported during the test
    for module_name in list(sys.modules.keys()):
        if module_name.startswith("pydvlp.debug") and module_name not in original_modules:
            del sys.modules[module_name]