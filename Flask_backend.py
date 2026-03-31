import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Timer, Event, Lock
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# SMTP configuration
smtp_server = "smtp.sendgrid.net"
smtp_port = 587
smtp_user = "apikey"
smtp_password = os.getenv("SENDGRID_API_KEY")

if smtp_password is None:
    raise ValueError("SENDGRID_API_KEY not set in environment")

# Store timers
timers = {}
lock = Lock()

class CustomTimer:
    def __init__(self, duration, label, user_info):
        self.duration = duration
        self.label = label
        self.user_info = user_info
        self.start_time = None
        self.end_time = None
        self.remaining = duration
        self.event = Event()
        self.thread = None

    def start(self):
        self.start_time = time.time()
        self.end_time = self.start_time + self.remaining
        self.thread = Timer(self.remaining, self.complete)
        self.thread.start()

    def complete(self):
        print(f"Timer '{self.label}' has expired!")
        self.send_email()
        with lock:
            timers.pop(self.label, None)

    def send_email(self):
        from_email = self.user_info["userEmail"]
        to_email = self.user_info["recipientEmail"]
        subject = "Last Message - Timer Expired"
        body = self.user_info["messageBody"]

        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Start TLS encryption
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, to_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

# Start a new timer
@app.route('/start', methods=['POST'])
def start_timer():
    data = request.get_json()
    label = data.get("username")
    duration = int(data.get("checkInPeriod", 0)) # currently passed directly to timer
    user_info = {
        "userEmail": data.get("userEmail"),
        "recipientEmail": data.get("recipientEmail"),
        "messageBody": data.get("messageBody")
    }

    with lock:
        if label in timers:
            return jsonify({"error": f"Timer with label '{label}' already exists"}), 400

        # Create and start the timer
        new_timer = CustomTimer(duration, label, user_info)
        timers[label] = new_timer
        new_timer.start()

    return jsonify({
        "message": f"Timer '{label}' started for {duration} seconds",
        "status": "running"
    })

if __name__ == "__main__":
    app.run(debug=True)
