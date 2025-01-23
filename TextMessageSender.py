import smtplib
from providers import PROVIDERS
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from os.path import basename
from datetime import datetime
import time
import threading


class TextMessageSender:

    def __init__(self, from_email="dalitextbot@gmail.com", from_password="cuhp xvns fgpp btle"):
        self.email = from_email
        self.password = from_password
        self.scheduled_messages = []
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def send_text(self, number, message, subject=""):
        for carrier in PROVIDERS.keys():
            if PROVIDERS.get(carrier).get("sms") != "":
                try:
                    msg = self.format_mime_message(number, carrier, subject, "sms", message)

                    self._send_message(msg)

                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                    return None

    def send_text_with_attachments(self, number, message, attachments=None, subject=""):
        for carrier in PROVIDERS.keys():
            if PROVIDERS.get(carrier).get("mms_support"):

                try:
                    msg = self.format_mime_message(number, carrier, subject, "mms", message)
                    if attachments:
                        for file in attachments:
                            try:
                                with open(file, "rb") as attachment:
                                    part = MIMEApplication(
                                        attachment.read(),
                                        Name=basename(file)
                                    )
                                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
                                msg.attach(part)

                            except Exception as e:
                                print(f"Error adding attachment {file}: {str(e)}")

                    self._send_message(msg)

                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                    return None

    def format_mime_message(self, number, carrier, subject, protocol, message):
        msg = MIMEMultipart()
        msg['From'] = self.email
        to_email = f'{number}@{PROVIDERS.get(carrier).get(protocol)}'
        msg['To'] = to_email
        msg['Subject'] = subject
        msg_id = make_msgid()
        msg['Message-ID'] = msg_id
        msg['Return-Receipt-To'] = self.email
        msg['Disposition-Notification-To'] = self.email

        msg.attach(MIMEText(message, "plain"))

        return msg

    def schedule_text(self, number, message, send_time, attachments=False):
        scheduled_text = {
            'number': number,
            'message': message,
            'send_time': send_time,
            'scheduled_at': datetime.now()
        }
        if attachments:
            scheduled_text['attachments'] = attachments
        self.scheduled_messages.append(scheduled_text)
        print(f"scheduled message for {send_time}")

    def _run_scheduler(self):
        while self.running:
            now = datetime.now()
            for msg in self.scheduled_messages:
                if now >= msg['send_time']:
                    if msg.get('attachments') is not None:
                        self.send_text_with_attachments(msg['number'], msg['message'], msg['attachments'])
                    else:
                        self.send_text(msg['number'], msg['message'])
                    self.scheduled_messages.remove(msg)
            time.sleep(5)


    def _send_message(self, msg):
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
    def stop_scheduler(self):
        self.running = False
