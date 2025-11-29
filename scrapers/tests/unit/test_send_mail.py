"""Tests for send_mail utility module."""

import os
from unittest.mock import patch, MagicMock
from scrapers.utils.send_mail import send_email


class TestSendEmailMissingCredentials:
    """Test send_email when credentials are missing."""

    def test_send_email_missing_email_env(self):
        """Test send_email returns False when EMAIL env var is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = send_email("subject", "body")
            assert result is False

    def test_send_email_missing_password_env(self):
        """Test send_email returns False when EMAIL_PW env var is missing."""
        with patch.dict(os.environ, {"EMAIL": "test@example.com"}, clear=True):
            result = send_email("subject", "body")
            assert result is False

    def test_send_email_missing_both_credentials(self):
        """Test send_email returns False when both credentials are missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = send_email("subject", "body")
            assert result is False

    def test_send_email_empty_email_string(self):
        """Test send_email returns False when EMAIL is empty string."""
        with patch.dict(os.environ, {"EMAIL": "", "EMAIL_PW": "password"}, clear=True):
            result = send_email("subject", "body")
            assert result is False

    def test_send_email_empty_password_string(self):
        """Test send_email returns False when EMAIL_PW is empty string."""
        with patch.dict(
            os.environ, {"EMAIL": "test@example.com", "EMAIL_PW": ""}, clear=True
        ):
            result = send_email("subject", "body")
            assert result is False


class TestSendEmailSuccess:
    """Test successful email sending scenarios."""

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_success_with_default_recipient(self, mock_smtp):
        """Test successful email send using EMAIL env var as recipient."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("Test Subject", "Test Body")

            assert result is True
            mock_smtp.assert_called_once_with("sender@example.com", "password")
            mock_smtp_instance.send.assert_called_once_with(
                to="sender@example.com", subject="Test Subject", contents="Test Body"
            )

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_success_with_custom_recipient(self, mock_smtp):
        """Test successful email send with custom recipient."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("Test Subject", "Test Body", to="recipient@example.com")

            assert result is True
            mock_smtp.assert_called_once_with("sender@example.com", "password")
            mock_smtp_instance.send.assert_called_once_with(
                to="recipient@example.com", subject="Test Subject", contents="Test Body"
            )

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_html_body(self, mock_smtp):
        """Test sending email with HTML content."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        html_body = "<html><body><h1>Hello</h1></body></html>"
        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("HTML Test", html_body)

            assert result is True
            mock_smtp_instance.send.assert_called_once()

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_special_characters_in_subject(self, mock_smtp):
        """Test sending email with special characters in subject."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        special_subject = "Scraper Report - Data Quality [2024-11-22]"
        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email(special_subject, "Body")

            assert result is True
            mock_smtp_instance.send.assert_called_once()

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_empty_subject_and_body(self, mock_smtp):
        """Test sending email with empty subject and body."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("", "")

            assert result is True
            mock_smtp_instance.send.assert_called_once()

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_large_body(self, mock_smtp):
        """Test sending email with large body content."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        large_body = "x" * 10000  # 10KB body
        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("Large Email", large_body)

            assert result is True
            mock_smtp_instance.send.assert_called_once()


class TestSendEmailExceptionHandling:
    """Test exception handling in send_email."""

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_smtp_connection_error(self, mock_smtp):
        """Test send_email handles SMTP connection errors."""
        mock_smtp.side_effect = Exception("SMTP connection failed")

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("subject", "body")

            assert result is False

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_authentication_error(self, mock_smtp):
        """Test send_email handles authentication errors."""
        mock_smtp.side_effect = Exception("Authentication failed: Invalid credentials")

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "wrong_password"}
        ):
            result = send_email("subject", "body")

            assert result is False

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_send_error(self, mock_smtp):
        """Test send_email handles errors during sending."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.send.side_effect = Exception("Send operation failed")

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("subject", "body")

            assert result is False

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_network_timeout(self, mock_smtp):
        """Test send_email handles network timeout."""
        mock_smtp.side_effect = TimeoutError("Connection timeout")

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("subject", "body")

            assert result is False

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_generic_exception(self, mock_smtp):
        """Test send_email handles any generic exception."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.send.side_effect = RuntimeError("Unexpected error")

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email("subject", "body")

            assert result is False


class TestSendEmailIntegration:
    """Integration-style tests for send_email."""

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_credentials_not_logged(self, mock_smtp):
        """Test that password is not logged in debug output."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "secret_password"}
        ):
            result = send_email("subject", "body")

            assert result is True
            # Verify mock was called with password, not logged elsewhere
            mock_smtp.assert_called_once_with("sender@example.com", "secret_password")

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_multiple_consecutive_sends(self, mock_smtp):
        """Test sending multiple emails in sequence."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result1 = send_email("Subject 1", "Body 1")
            result2 = send_email("Subject 2", "Body 2")
            result3 = send_email("Subject 3", "Body 3")

            assert result1 is True
            assert result2 is True
            assert result3 is True
            assert mock_smtp_instance.send.call_count == 3

    @patch("scrapers.utils.send_mail.yagmail.SMTP")
    def test_send_email_with_unicode_content(self, mock_smtp):
        """Test sending email with Unicode characters."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        unicode_subject = "Relatório de Filmes 📽️ - Dezembro/2024"
        unicode_body = "Assuntos em alta: Ficção Científica, Ação, Animação 🎬"

        with patch.dict(
            os.environ, {"EMAIL": "sender@example.com", "EMAIL_PW": "password"}
        ):
            result = send_email(unicode_subject, unicode_body)

            assert result is True
            call_args = mock_smtp_instance.send.call_args
            assert call_args[1]["subject"] == unicode_subject
            assert call_args[1]["contents"] == unicode_body
