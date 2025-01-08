from flask import Flask, request, jsonify
from threading import Timer, Event, Lock, Thread
import time

app = Flask(__name__)

# Store timers in a dictionary
timers = {}
lock = Lock()  # Lock for thread-safe access to the timers dictionary

class CustomTimer:
    def __init__(self, duration, label):
        self.duration = duration
        self.label = label
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

    def pause(self):
        if self.thread:
            self.thread.cancel()
            self.remaining = self.end_time - time.time()

    def resume(self):
        self.start()

    def cancel(self):
        if self.thread:
            self.thread.cancel()
        self.remaining = 0

    def complete(self):
        print(f"Timer '{self.label}' has expired!")
        self.event.set()
        with lock:
            timers.pop(self.label, None)  # Remove timer when it completes

    def get_remaining_time(self):
        # Calculate remaining time by checking how much time has passed
        if self.thread:
            return max(0, self.end_time - time.time())
        return 0

# Background thread function to update the remaining time of all active timers
def update_timers():
    while True:
        with lock:
            for timer in timers.values():
                remaining_time = timer.get_remaining_time()
                # This could be used to update clients, logs, etc.
                print(f"Timer '{timer.label}' remaining time: {int(remaining_time)} seconds")
        time.sleep(1)  # Wait for 1 second before checking again

# POST /start - Start a new timer
@app.route('/start', methods=['POST'])
def start_timer():
    data = request.get_json()
    label = data.get("label")
    duration = data.get("duration", 0)
    unit = data.get("unit", "seconds")

    if not label:
        return jsonify({"error": "Timer label is required"}), 400

    if unit == "minutes":
        duration *= 60  # Convert to seconds

    with lock:
        if label in timers:
            return jsonify({"error": f"Timer with label '{label}' already exists"}), 400

        # Create and start the timer
        new_timer = CustomTimer(duration, label)
        timers[label] = new_timer
        new_timer.start()

    return jsonify({
        "message": f"Timer '{label}' started for {duration} seconds",
        "status": "running"
    })

# GET /status - Check the status of a timer
@app.route('/status', methods=['GET'])
def get_status():
    label = request.args.get("label")
    if not label:
        return jsonify({"error": "Timer label is required"}), 400

    with lock:
        timer = timers.get(label)
        if not timer:
            return jsonify({"error": f"No timer found with label '{label}'"}), 404

        remaining_time = timer.get_remaining_time()  # Get the remaining time
        status = "running" if remaining_time > 0 else "stopped"

        return jsonify({
            "label": label,
            "remaining_time": int(remaining_time),
            "status": status
        })

# POST /pause - Pause a timer
@app.route('/pause', methods=['POST'])
def pause_timer():
    data = request.get_json()
    label = data.get("label")

    if not label:
        return jsonify({"error": "Timer label is required"}), 400

    with lock:
        timer = timers.get(label)
        if not timer:
            return jsonify({"error": f"No timer found with label '{label}'"}), 404

        timer.pause()

    return jsonify({"message": f"Timer '{label}' paused"})

# POST /resume - Resume a paused timer
@app.route('/resume', methods=['POST'])
def resume_timer():
    data = request.get_json()
    label = data.get("label")

    if not label:
        return jsonify({"error": "Timer label is required"}), 400

    with lock:
        timer = timers.get(label)
        if not timer:
            return jsonify({"error": f"No timer found with label '{label}'"}), 404

        timer.resume()

    return jsonify({"message": f"Timer '{label}' resumed"})

# POST /reset - Reset a timer
@app.route('/reset', methods=['POST'])
def reset_timer():
    data = request.get_json()
    label = data.get("label")

    if not label:
        return jsonify({"error": "Timer label is required"}), 400

    with lock:
        timer = timers.pop(label, None)
        if not timer:
            return jsonify({"error": f"No timer found with label '{label}'"}), 404

        timer.cancel()

    return jsonify({"message": f"Timer '{label}' reset"})

# Start the background thread to update timers every second
if __name__ == "__main__":
    thread = Thread(target=update_timers, daemon=True)
    thread.start()

    app.run(debug=True)
