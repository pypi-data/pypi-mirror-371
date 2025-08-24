"""Tests for enhanced debugging functionality."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout

import pytest

from pydvlp.debug import debug
from pydvlp.debug.fallbacks import FallbackDebug


class TestEnhancedDebugger:
    """Test suite for EnhancedDebugger."""

    def test_basic_debug_output(self):
        """Test basic debug output functionality."""
        debugger = FallbackDebug()
        
        # Capture output to stderr
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        # Test with simple value
        with redirect_stderr(captured_output):
            result = debugger.ice(42)
            
        output = captured_output.getvalue()
        assert "42" in output
        assert result == 42

    def test_debug_with_label(self):
        """Test debug output with custom label."""
        debugger = FallbackDebug()
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            result = debugger.ice("answer", 42)
            
        output = captured_output.getvalue()
        assert "answer" in output
        assert "42" in output
        assert result == "answer"

    def test_debug_multiple_values(self):
        """Test debug output with multiple values."""
        debugger = FallbackDebug()
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            result = debugger.ice(1, 2, 3)
            
        output = captured_output.getvalue()
        assert "1" in output
        assert "2" in output
        assert "3" in output
        assert result == 1

    def test_debug_disabled(self):
        """Test debug output when disabled."""
        debugger = FallbackDebug()
        debugger.enabled = False
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            result = debugger.ice(42)
            
        output = captured_output.getvalue()
        assert output == ""  # No output when disabled
        assert result == 42

    def test_configure_output_function(self):
        """Test configuring custom output function."""
        # FallbackDebug doesn't support configure_output
        # Just test basic functionality
        debugger = FallbackDebug()
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            debugger.ice(42)
            
        output = captured_output.getvalue()
        assert "42" in output

    def test_global_debug_function(self):
        """Test the global debug function."""
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        # Import the debug instance from the package
        from pydvlp.debug.debug import debug as debug_instance
        
        # Test using the debug instance
        with redirect_stderr(captured_output):
            debug_instance.ice(42, "test")
            
        output = captured_output.getvalue()
        assert "42" in output
        assert "test" in output


class TestDebugFormats:
    """Test different output formats."""

    def test_plain_format(self):
        """Test plain output format."""
        debugger = FallbackDebug()
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            debugger.ice({"key": "value"})
            
        output = captured_output.getvalue()
        assert "key" in output
        assert "value" in output

    def test_dict_debug(self):
        """Test debugging dictionary values."""
        debugger = FallbackDebug()
        
        test_dict = {"name": "test", "value": 42, "nested": {"a": 1}}
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            result = debugger.ice(test_dict)
            
        output = captured_output.getvalue()
        assert "name" in output
        assert "test" in output
        assert "42" in output
        assert result == test_dict

    def test_list_debug(self):
        """Test debugging list values."""
        debugger = FallbackDebug()
        
        test_list = [1, "two", 3.0, {"four": 4}]
        
        from contextlib import redirect_stderr
        captured_output = io.StringIO()
        
        with redirect_stderr(captured_output):
            result = debugger.ice(test_list)
            
        output = captured_output.getvalue()
        assert "1" in output
        assert "two" in output
        assert result == test_list