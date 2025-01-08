from flask import Flask, request, jsonify
from threading import Timer, Event
import time

app = Flask(__name__)

# Store timers in a dictionary
timers = {}

class CustomTimer:
    def __init__(self, duration, label):
        self.duration = duration
        self.label = label
        self.start_time = None
        self.end_time = None
        self.remaining = duration
        self.event = Event()
        self.thread = Timer(self.remaining, self.complete)

    def start(self):
        self.start_time = time.time()
        self.end_time = self.start_time + self.remaining
        self.thread.start()

    def pause(self):
        self.thread.cancel()
        self.remaining = self.end_time - time.time()

    def resume(self):
        self.thread = Timer(self.remaining, self.complete)
        self.start()

    def cancel(self):
        self.thread.cancel()

    def complete(self):
        print(f"Timer '{self.label}' has expired!")
        self.event.set()

@app.route("/timers", methods=["POST"])
def create_timer():
    data = request.json
    label = data.get("label", "Timer")
    duration = data.get("duration", 60)  # Default duration is 60 seconds
    timer_id = len(timers) + 1
    new_timer = CustomTimer(duration, label)
    timers[timer_id] = new_timer
    new_timer.start()
    return jsonify({"timer_id": timer_id, "message": f"Timer '{label}' started for {duration} seconds"}), 201

@app.route("/timers/<int:timer_id>/pause", methods=["POST"])
def pause_timer(timer_id):
    if timer_id in timers:
        timers[timer_id].pause()
        return jsonify({"message": f"Timer {timer_id} paused"}), 200
    return jsonify({"error": "Timer not found"}), 404

@app.route("/timers/<int:timer_id>/resume", methods=["POST"])
def resume_timer(timer_id):
    if timer_id in timers:
        timers[timer_id].resume()
        return jsonify({"message": f"Timer {timer_id} resumed"}), 200
    return jsonify({"error": "Timer not found"}), 404

@app.route("/timers/<int:timer_id>/cancel", methods=["DELETE"])
def cancel_timer(timer_id):
    if timer_id in timers:
        timers[timer_id].cancel()
        del timers[timer_id]
        return jsonify({"message": f"Timer {timer_id} canceled"}), 200
    return jsonify({"error": "Timer not found"}), 404

@app.route("/timers", methods=["GET"])
def list_timers():
    active_timers = {
        timer_id: {
            "label": timer.label,
            "remaining": timer.remaining,
            "expired": timer.event.is_set(),
        }
        for timer_id, timer in timers.items()
    }
    return jsonify(active_timers), 200

if __name__ == "__main__":
    app.run(debug=True)