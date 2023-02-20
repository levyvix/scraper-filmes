import yagmail


def send_email(message, subject):
    yag = yagmail.SMTP("levy.m.nunes@gmail.com", "lkcakiycoengtbps")
    # contents = ['This is the body, and here is just text http://somedomain/image.png',
    #             'You can find an audio file attached.', '/local/path/song.mp3']
    yag.send("levy.vix@gmail.com", f"Daily dose of movies from {subject}", contents=message)


if __name__ == "__main__":
    send_email("ola")
