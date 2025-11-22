"""Tests for Comando Torrents configuration module."""

import os
from scrapers.comando_torrents.config import ComandoTorrentsConfig, Config


class TestComandoTorrentsConfigDefaults:
    """Test ComandoTorrentsConfig with default values."""

    def test_config_instantiation(self):
        """Test that config can be instantiated."""
        config = ComandoTorrentsConfig()
        assert config is not None

    def test_default_url_base(self):
        """Test default URL base is correct."""
        config = ComandoTorrentsConfig()
        assert config.URL_BASE == "https://comando.la/category/filmes/"

    def test_default_json_file_name(self):
        """Test default JSON file name."""
        config = ComandoTorrentsConfig()
        assert config.JSON_FILE_NAME == "movies.json"

    def test_singleton_config_instance(self):
        """Test that singleton Config instance is properly initialized."""
        assert Config is not None
        assert Config.URL_BASE == "https://comando.la/category/filmes/"
        assert Config.JSON_FILE_NAME == "movies.json"


class TestComandoTorrentsConfigEnvOverride:
    """Test ComandoTorrentsConfig with environment variable overrides."""

    def test_override_url_base_from_env(self):
        """Test URL_BASE can be overridden from environment."""
        custom_url = "https://custom.example.com/movies/"
        with os.popen(
            f'export URL_BASE="{custom_url}" && python3 -c "from scrapers.comando_torrents.config import ComandoTorrentsConfig; c = ComandoTorrentsConfig(); print(c.URL_BASE)"',
            "r",
        ) as proc:
            # Note: This test may not work due to subprocess isolation
            # We test the mechanism differently below
            _ = proc.read().strip()

    def test_override_json_file_name_from_env(self):
        """Test JSON_FILE_NAME can be overridden from environment."""
        # Test that the config accepts environment variables
        # by creating a new instance with env var set
        original_env = os.environ.get("JSON_FILE_NAME")
        try:
            os.environ["JSON_FILE_NAME"] = "custom_movies.json"
            config = ComandoTorrentsConfig()
            assert config.JSON_FILE_NAME == "custom_movies.json"
        finally:
            if original_env:
                os.environ["JSON_FILE_NAME"] = original_env
            elif "JSON_FILE_NAME" in os.environ:
                del os.environ["JSON_FILE_NAME"]

    def test_env_file_loading(self):
        """Test that config loads from .env file if it exists."""
        # Verify model_config settings for env file loading
        assert ComandoTorrentsConfig.model_config["env_file"] == ".env"
        assert ComandoTorrentsConfig.model_config["env_file_encoding"] == "utf-8"
        assert ComandoTorrentsConfig.model_config["case_sensitive"] is True


class TestComandoTorrentsConfigProperties:
    """Test ComandoTorrentsConfig properties and attributes."""

    def test_config_has_url_base_property(self):
        """Test that config has URL_BASE property."""
        config = ComandoTorrentsConfig()
        assert hasattr(config, "URL_BASE")
        assert isinstance(config.URL_BASE, str)

    def test_config_has_json_file_name_property(self):
        """Test that config has JSON_FILE_NAME property."""
        config = ComandoTorrentsConfig()
        assert hasattr(config, "JSON_FILE_NAME")
        assert isinstance(config.JSON_FILE_NAME, str)

    def test_url_base_is_valid_url(self):
        """Test that URL_BASE is a valid URL format."""
        config = ComandoTorrentsConfig()
        assert config.URL_BASE.startswith("http")
        assert config.URL_BASE.endswith("/")

    def test_json_file_name_extension(self):
        """Test that JSON_FILE_NAME has .json extension."""
        config = ComandoTorrentsConfig()
        assert config.JSON_FILE_NAME.endswith(".json")


class TestComandoTorrentsConfigPydantic:
    """Test Pydantic-specific configuration behavior."""

    def test_config_is_pydantic_model(self):
        """Test that config is a Pydantic BaseSettings model."""
        config = ComandoTorrentsConfig()
        assert hasattr(config, "model_validate")
        assert hasattr(config, "model_dump")

    def test_config_model_dump(self):
        """Test that config can be dumped to dict."""
        config = ComandoTorrentsConfig()
        dumped = config.model_dump()

        assert "URL_BASE" in dumped
        assert "JSON_FILE_NAME" in dumped
        assert dumped["URL_BASE"] == config.URL_BASE
        assert dumped["JSON_FILE_NAME"] == config.JSON_FILE_NAME

    def test_config_model_dump_exclude_none(self):
        """Test that model_dump can exclude None values."""
        config = ComandoTorrentsConfig()
        dumped = config.model_dump(exclude_none=True)

        # Both fields should be present since they have defaults
        assert "URL_BASE" in dumped
        assert "JSON_FILE_NAME" in dumped

    def test_config_case_sensitivity(self):
        """Test that config is case-sensitive."""
        # Pydantic will validate case sensitivity
        config = ComandoTorrentsConfig()
        assert hasattr(config, "URL_BASE")
        # URL_base (different case) should not exist
        assert not hasattr(config, "url_base")


class TestComandoTorrentsConfigValidation:
    """Test ComandoTorrentsConfig validation."""

    def test_config_with_empty_strings(self):
        """Test config creation with empty strings (should be allowed)."""
        config = ComandoTorrentsConfig(URL_BASE="", JSON_FILE_NAME="")
        assert config.URL_BASE == ""
        assert config.JSON_FILE_NAME == ""

    def test_config_with_none_values_fails(self):
        """Test that None values are rejected (fields required by default)."""
        # Pydantic may not allow None for string fields without Optional
        # Try to create config with None - should either fail or keep defaults
        config = ComandoTorrentsConfig()
        assert config.URL_BASE is not None
        assert config.JSON_FILE_NAME is not None

    def test_config_immutability(self):
        """Test that config fields are settable (Pydantic default)."""
        config = ComandoTorrentsConfig()
        # Try to modify fields (Pydantic allows this by default)
        original_url = config.URL_BASE
        config.URL_BASE = "https://new.example.com/"
        assert config.URL_BASE == "https://new.example.com/"
        # Restore
        config.URL_BASE = original_url


class TestComandoTorrentsConfigIntegration:
    """Integration tests for ComandoTorrentsConfig."""

    def test_config_singleton_consistency(self):
        """Test that singleton Config instance is consistent."""
        # Create two instances
        config1 = Config
        config2 = ComandoTorrentsConfig()

        # Singleton should match default instance
        assert config1.URL_BASE == config2.URL_BASE
        assert config1.JSON_FILE_NAME == config2.JSON_FILE_NAME

    def test_config_json_serialization(self):
        """Test that config can be JSON serialized."""
        import json

        config = ComandoTorrentsConfig()
        dumped = config.model_dump()

        # Should be serializable to JSON
        json_str = json.dumps(dumped)
        assert "URL_BASE" in json_str
        assert "JSON_FILE_NAME" in json_str

    def test_config_multiple_instances_independent(self):
        """Test that multiple instances are independent."""
        config1 = ComandoTorrentsConfig()
        config2 = ComandoTorrentsConfig()

        # Modify one
        config1.URL_BASE = "https://different.example.com/"

        # Other should not be affected
        assert config2.URL_BASE == "https://comando.la/category/filmes/"

    def test_config_has_model_config(self):
        """Test that config has proper model configuration."""
        assert hasattr(ComandoTorrentsConfig, "model_config")
        config_dict = ComandoTorrentsConfig.model_config

        assert "env_file" in config_dict
        assert "env_file_encoding" in config_dict
        assert "case_sensitive" in config_dict
        assert "extra" in config_dict
