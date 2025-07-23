
import smtplib
from email.message import EmailMessage
import imaplib
import email

def send_email(subject, body, to_email, from_email, app_password):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)

def check_reply(from_email, app_password, expected_subject=None, mailbox="INBOX"):
    with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
        mail.login(from_email, app_password)
        mail.select(mailbox)
        typ, data = mail.search(None, 'UNSEEN')

        for num in reversed(data[0].split()):
            typ, msg_data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg["subject"]
            body = msg.get_payload(decode=True).decode(errors="ignore")

            if expected_subject and expected_subject not in subject:
                continue

            if "YES" in body.upper():
                return True
            elif "NO" in body.upper():
                return False

        return None  # no relevant response
