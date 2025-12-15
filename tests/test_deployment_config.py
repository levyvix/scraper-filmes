"""Integration tests for Prefect deployment configuration.

Tests that the deployment configuration loads environment variables correctly
and that credential methods work as expected.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from scrapers.gratis_torrent.bigquery_client import get_gcp_credentials, get_client
from scrapers.gratis_torrent.config import GratisTorrentConfig


class TestDeploymentConfig:
    """Tests for deployment environment variable loading."""

    def test_config_loads_from_env_vars(self):
        """Test that config loads GCP_PROJECT_ID from environment variables."""
        original_project = os.environ.get("GCP_PROJECT_ID")
        try:
            os.environ["GCP_PROJECT_ID"] = "test-project-123"
            config = GratisTorrentConfig()
            assert config.GCP_PROJECT_ID == "test-project-123"
        finally:
            if original_project:
                os.environ["GCP_PROJECT_ID"] = original_project
            else:
                os.environ.pop("GCP_PROJECT_ID", None)

    def test_config_loads_credentials_method_from_env(self):
        """Test that config loads GCP_CREDENTIALS_METHOD from environment."""
        original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
        try:
            os.environ["GCP_CREDENTIALS_METHOD"] = "FILE"
            config = GratisTorrentConfig()
            assert config.GCP_CREDENTIALS_METHOD == "FILE"
        finally:
            if original_method:
                os.environ["GCP_CREDENTIALS_METHOD"] = original_method
            else:
                os.environ.pop("GCP_CREDENTIALS_METHOD", None)

    def test_config_credentials_path_from_env(self):
        """Test that config loads GCP_CREDENTIALS_PATH from environment."""
        original_path = os.environ.get("GCP_CREDENTIALS_PATH")
        try:
            os.environ["GCP_CREDENTIALS_PATH"] = "/tmp/test-creds.json"
            config = GratisTorrentConfig()
            assert config.GCP_CREDENTIALS_PATH == "/tmp/test-creds.json"
        finally:
            if original_path:
                os.environ["GCP_CREDENTIALS_PATH"] = original_path
            else:
                os.environ.pop("GCP_CREDENTIALS_PATH", None)


class TestCredentialDiscovery:
    """Tests for credential discovery mechanism."""

    def test_get_credentials_with_adc_method(self):
        """Test that ADC method uses Application Default Credentials."""
        original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
        try:
            os.environ["GCP_CREDENTIALS_METHOD"] = "ADC"
            with patch("scrapers.gratis_torrent.bigquery_client.google.auth.default") as mock_adc:
                # Mock ADC to return test credentials
                mock_creds = MagicMock()
                mock_adc.return_value = (mock_creds, "test-project")

                credentials = get_gcp_credentials()

                # Verify ADC was called
                mock_adc.assert_called_once()
                assert credentials == mock_creds

        finally:
            if original_method:
                os.environ["GCP_CREDENTIALS_METHOD"] = original_method
            else:
                os.environ.pop("GCP_CREDENTIALS_METHOD", None)

    def test_get_credentials_with_file_method_missing_path(self):
        """Test that FILE method without path raises ValueError."""
        original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
        original_path = os.environ.get("GCP_CREDENTIALS_PATH")
        try:
            os.environ["GCP_CREDENTIALS_METHOD"] = "FILE"
            os.environ.pop("GCP_CREDENTIALS_PATH", None)

            # Create fresh config with new env vars
            config = GratisTorrentConfig()
            with patch("scrapers.gratis_torrent.bigquery_client.Config", config):
                with pytest.raises(ValueError, match="GCP_CREDENTIALS_PATH is not set"):
                    get_gcp_credentials()

        finally:
            if original_method:
                os.environ["GCP_CREDENTIALS_METHOD"] = original_method
            else:
                os.environ.pop("GCP_CREDENTIALS_METHOD", None)
            if original_path:
                os.environ["GCP_CREDENTIALS_PATH"] = original_path
            else:
                os.environ.pop("GCP_CREDENTIALS_PATH", None)

    def test_get_credentials_with_file_method_missing_file(self):
        """Test that FILE method with missing file raises FileNotFoundError."""
        original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
        original_path = os.environ.get("GCP_CREDENTIALS_PATH")
        try:
            os.environ["GCP_CREDENTIALS_METHOD"] = "FILE"
            os.environ["GCP_CREDENTIALS_PATH"] = "/nonexistent/path/to/creds.json"

            # Create fresh config with new env vars
            config = GratisTorrentConfig()
            with patch("scrapers.gratis_torrent.bigquery_client.Config", config):
                with pytest.raises(FileNotFoundError, match="Credential file not found"):
                    get_gcp_credentials()

        finally:
            if original_method:
                os.environ["GCP_CREDENTIALS_METHOD"] = original_method
            else:
                os.environ.pop("GCP_CREDENTIALS_METHOD", None)
            if original_path:
                os.environ["GCP_CREDENTIALS_PATH"] = original_path
            else:
                os.environ.pop("GCP_CREDENTIALS_PATH", None)

    def test_get_credentials_with_file_method_valid_file(self):
        """Test that FILE method with valid file loads credentials."""
        import tempfile
        import json

        original_method = os.environ.get("GCP_CREDENTIALS_METHOD")
        original_path = os.environ.get("GCP_CREDENTIALS_PATH")
        temp_file = None
        try:
            # Create a temporary service account JSON file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                service_account = {
                    "type": "service_account",
                    "project_id": "test-project",
                    "private_key_id": "key123",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDU8HJ7x3VzW5Tw\ntest\n-----END PRIVATE KEY-----\n",
                    "client_email": "test@test-project.iam.gserviceaccount.com",
                    "client_id": "123456789",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                json.dump(service_account, f)
                temp_file = f.name

            os.environ["GCP_CREDENTIALS_METHOD"] = "FILE"
            os.environ["GCP_CREDENTIALS_PATH"] = temp_file

            # Create fresh config with new env vars
            config = GratisTorrentConfig()
            with (
                patch(
                    "scrapers.gratis_torrent.bigquery_client.google.oauth2.service_account.Credentials.from_service_account_file"
                ) as mock_from_file,
                patch("scrapers.gratis_torrent.bigquery_client.Config", config),
            ):
                mock_creds = MagicMock()
                mock_from_file.return_value = mock_creds

                credentials = get_gcp_credentials()

                # Verify file was used
                mock_from_file.assert_called_once_with(temp_file)
                assert credentials == mock_creds

        finally:
            # Cleanup temp file
            if temp_file:
                os.unlink(temp_file)

            if original_method:
                os.environ["GCP_CREDENTIALS_METHOD"] = original_method
            else:
                os.environ.pop("GCP_CREDENTIALS_METHOD", None)
            if original_path:
                os.environ["GCP_CREDENTIALS_PATH"] = original_path
            else:
                os.environ.pop("GCP_CREDENTIALS_PATH", None)


class TestBigQueryClientIntegration:
    """Tests for BigQuery client with credential integration."""

    def test_get_client_with_credentials(self):
        """Test that BigQuery client is created with discovered credentials."""
        with (
            patch("scrapers.gratis_torrent.bigquery_client.get_gcp_credentials") as mock_get_creds,
            patch("scrapers.gratis_torrent.bigquery_client.bigquery.Client") as mock_client,
        ):
            mock_creds = MagicMock()
            mock_get_creds.return_value = mock_creds

            get_client()

            # Verify credentials were loaded
            mock_get_creds.assert_called_once()

            # Verify BigQuery client was created with credentials
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert "credentials" in call_kwargs
            assert call_kwargs["credentials"] == mock_creds


class TestPrefectFlowCredentialValidation:
    """Tests for Prefect flow credential validation task."""

    def test_flow_can_import_and_execute(self):
        """Test that the flow imports and has credential validation task."""
        from scrapers.gratis_torrent.flow import validate_credentials_task, gratis_torrent_flow

        # Verify the task exists and is callable
        assert callable(validate_credentials_task)
        assert callable(gratis_torrent_flow)

    @patch("scrapers.gratis_torrent.bigquery_client.get_gcp_credentials")
    def test_credential_validation_task_success(self, mock_get_creds):
        """Test that credential validation task succeeds with valid credentials."""
        from scrapers.gratis_torrent.flow import validate_credentials_task

        mock_get_creds.return_value = MagicMock()

        # Task should not raise an exception
        result = validate_credentials_task()
        assert result is True

    @patch("scrapers.gratis_torrent.flow.get_gcp_credentials")
    def test_credential_validation_task_failure(self, mock_get_creds):
        """Test that credential validation task fails when credentials cannot load."""
        from scrapers.gratis_torrent.flow import validate_credentials_task

        mock_get_creds.side_effect = ValueError("Test credential error")

        # Task should raise ValueError
        with pytest.raises(ValueError, match="Credential validation failed"):
            validate_credentials_task()
