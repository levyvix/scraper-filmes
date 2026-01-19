import os

import yagmail
from loguru import logger


def send_email(subject: str, body: str, to: str | None = None) -> bool:
    """
    Send email notification.

    Args:
        subject: Email subject
        body: Email body
        to: Recipient email (uses EMAIL env var if not provided)

    Returns:
        True if email sent successfully
    """
    email = os.getenv("EMAIL")
    email_pw = os.getenv("EMAIL_PW")

    if not email or not email_pw:
        logger.warning("Email credentials not configured, skipping email")
        return False

    recipient = to or email

    try:
        yag = yagmail.SMTP(email, email_pw)
        yag.send(to=recipient, subject=subject, contents=body)
        logger.info(f"Email sent successfully to {recipient}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # Example usage:
    # Make sure to have EMAIL and EMAIL_PW set in your .env file
    from dotenv import load_dotenv

    load_dotenv()

    test_subject = "Test Email from Scraper"
    test_body = "This is a test email to confirm the send_email function is working."

    success = send_email(test_subject, test_body)
    if success:
        print("Test email sent successfully.")
    else:
        print("Failed to send test email. Check logs and .env configuration.")
