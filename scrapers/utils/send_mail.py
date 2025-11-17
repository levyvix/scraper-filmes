import yagmail
from dotenv import load_dotenv
import os


class MailSender:
    def __init__(self, receiver, contents, subject) -> None:
        self.receiver = receiver
        self.contents = contents
        self.subject = subject
        load_dotenv()

    def send(self):
        yag = yagmail.SMTP(user=os.getenv("EMAIL"), password=os.getenv("EMAIL_PW"))
        yag.send(self.receiver, self.subject, self.contents)
        yag.close()


if __name__ == "__main__":
    subject = "test email"
    contents = "this is a test email"
    receiver = "levy.m.nunes@gmail.com"
    MailSender(receiver, contents, subject).send()
