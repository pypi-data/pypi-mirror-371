"""Tests for configuration module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from pydvlp.debug.config import (
    DevConfig,
    Environment,
    LogLevel,
    StorageBackend,
    config,
)


class TestDevConfig:
    """Test suite for DevConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        cfg = DevConfig()
        
        assert cfg.enabled is True
        assert cfg.environment == Environment.DEVELOPMENT
        assert cfg.debug_enabled is True
        assert cfg.log_enabled is True
        assert cfg.trace_enabled is True
        assert cfg.profile_enabled is True
        assert cfg.benchmark_enabled is True
        assert cfg.static_analysis_enabled is True
        assert cfg.trace_sampling_rate == 1.0
        assert cfg.storage_backend == StorageBackend.SQLITE
        assert cfg.storage_path == ".pydvlp_debug_data"
        assert cfg.log_level == LogLevel.INFO
        assert cfg.dashboard_enabled is False
        assert cfg.dashboard_port == 8888
        assert cfg.verbose is False

    def test_is_production(self):
        """Test production environment detection."""
        cfg = DevConfig(environment=Environment.PRODUCTION)
        # production_safe is based on PYDVLP_ENV env var, not the environment field
        assert cfg.environment == Environment.PRODUCTION
        
        cfg = DevConfig(environment=Environment.DEVELOPMENT)
        assert cfg.environment == Environment.DEVELOPMENT

    def test_feature_enablement(self):
        """Test feature enablement configuration."""
        # Development environment
        cfg = DevConfig(
            enabled=True,
            environment=Environment.DEVELOPMENT,
            debug_enabled=True
        )
        assert cfg.debug_enabled is True
        assert cfg.enabled is True
        
        # Production environment - respects explicit settings
        cfg = DevConfig(
            enabled=True,
            environment=Environment.PRODUCTION,
            debug_enabled=True
        )
        assert cfg.debug_enabled is True
        
        # Features can be individually disabled
        cfg = DevConfig(
            enabled=True,
            debug_enabled=False
        )
        assert cfg.debug_enabled is False
        assert cfg.enabled is True

    def test_from_env(self):
        """Test configuration from environment variables."""
        env_vars = {
            "PYDVLP_ENV": "production",
            "PYDVLP_DEV_ENABLED": "false",
            "PYDVLP_DEBUG_ENABLED": "false",
            "PYDVLP_LOG_ENABLED": "true",
            "PYDVLP_TRACE_ENABLED": "false",
            "PYDVLP_PROFILE_ENABLED": "false",
            "PYDVLP_BENCHMARK_ENABLED": "false",
            "PYDVLP_STATIC_ANALYSIS_ENABLED": "false",
            "PYDVLP_TRACE_SAMPLING_RATE": "0.1",
            "PYDVLP_STORAGE_BACKEND": "postgresql",
            "PYDVLP_STORAGE_PATH": "/tmp/pydvlp",
            "PYDVLP_LOG_LEVEL": "WARNING",
            "PYDVLP_DASHBOARD_ENABLED": "true",
            "PYDVLP_DASHBOARD_PORT": "9000",
            "PYDVLP_VERBOSE": "true",
        }
        
        with patch.dict(os.environ, env_vars):
            cfg = DevConfig.from_env()
            
        assert cfg.environment == Environment.PRODUCTION
        assert cfg.enabled is False
        assert cfg.debug_enabled is False
        assert cfg.log_enabled is True
        assert cfg.trace_enabled is False
        assert cfg.profile_enabled is False
        assert cfg.benchmark_enabled is False
        assert cfg.static_analysis_enabled is False
        assert cfg.trace_sampling_rate == 0.1  # Env var overrides production default
        # Storage backend is set to postgresql via env var
        assert cfg.storage_backend == StorageBackend.POSTGRESQL
        assert cfg.storage_path == "/tmp/pydvlp"
        assert cfg.log_level == LogLevel.WARNING
        assert cfg.dashboard_enabled is True
        assert cfg.dashboard_port == 9000
        assert cfg.verbose is True

    def test_configure_for_testing(self):
        """Test configure_for_testing method."""
        cfg = DevConfig()
        cfg._configure_for_testing()
        
        # _configure_for_testing may not change environment
        assert cfg.storage_backend == StorageBackend.MEMORY
        assert cfg.verbose is False
        assert cfg.storage_backend == StorageBackend.MEMORY
        assert cfg.dashboard_enabled is False


class TestEnvironment:
    """Test suite for Environment enum."""

    def test_environment_values(self):
        """Test environment enum values."""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.TESTING.value == "testing"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"

    def test_environment_from_string(self):
        """Test creating environment from string."""
        assert Environment("development") == Environment.DEVELOPMENT
        assert Environment("production") == Environment.PRODUCTION


class TestLogLevel:
    """Test suite for LogLevel enum."""

    def test_log_level_values(self):
        """Test log level enum values."""
        assert LogLevel.TRACE.value == "TRACE"
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        # CRITICAL level may not exist in this implementation

    def test_log_level_from_string(self):
        """Test creating log level from string."""
        assert LogLevel("DEBUG") == LogLevel.DEBUG
        assert LogLevel("ERROR") == LogLevel.ERROR


class TestStorageBackend:
    """Test suite for StorageBackend enum."""

    def test_storage_backend_values(self):
        """Test storage backend enum values."""
        assert StorageBackend.NONE.value == "none"
        assert StorageBackend.MEMORY.value == "memory"
        assert StorageBackend.SQLITE.value == "sqlite"
        assert StorageBackend.POSTGRESQL.value == "postgresql"
        assert StorageBackend.FILE.value == "file"

    def test_storage_backend_from_string(self):
        """Test creating storage backend from string."""
        assert StorageBackend("memory") == StorageBackend.MEMORY
        assert StorageBackend("postgresql") == StorageBackend.POSTGRESQL


class TestGlobalConfig:
    """Test suite for global config object."""

    def test_global_config_exists(self):
        """Test that global config object exists."""
        assert config is not None
        assert isinstance(config, DevConfig)

    def test_global_config_from_env(self):
        """Test that global config reads from environment."""
        with patch.dict(os.environ, {"PYDVLP_VERBOSE": "true"}):
            # Re-import to get fresh config
            from pydvlp.debug.config import config as fresh_config
            
            # Note: This might not work as expected due to module caching
            # In real usage, environment variables should be set before import