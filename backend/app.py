from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

class KubernetesTracker:
    def __init__(self):
        self.progress_file = "kubernetes_progress.json"
        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                self.courses = json.load(f)
        else:
            self.courses = self.initialize_courses()
            self.save_progress()

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.courses, f, indent=4)

    def initialize_courses(self):
        courses = {}
        course_titles = {
            1: "Docker Fundamentals",
            2: "Dockerize an application",
            # ... (add all 42 course titles)
        }
        
        for day in range(1, 43):
            courses[str(day)] = {
                "title": course_titles.get(day, f"Day {day}"),
                "completed": False,
                "date_completed": None,
                "notes": "",
                "time_spent": 0,
                "start_time": None
            }
        return courses

tracker = KubernetesTracker()

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify(tracker.courses)

@app.route('/api/courses/<day>', methods=['PUT'])
def update_course(day):
    data = request.json
    if day in tracker.courses:
        tracker.courses[day].update(data)
        tracker.save_progress()
        return jsonify({"message": "Course updated successfully"})
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/courses/<day>/complete', methods=['POST'])
def mark_complete(day):
    if day in tracker.courses:
        tracker.courses[day]["completed"] = True
        tracker.courses[day]["date_completed"] = datetime.now().strftime("%Y-%m-%d")
        tracker.save_progress()
        return jsonify({"message": "Course marked as complete"})
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/courses/<day>/notes', methods=['POST'])
def add_notes(day):
    if day in tracker.courses:
        notes = request.json.get("notes", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        if tracker.courses[day]["notes"]:
            tracker.courses[day]["notes"] += f"\n\n{timestamp}:\n{notes}"
        else:
            tracker.courses[day]["notes"] = f"{timestamp}:\n{notes}"
        tracker.save_progress()
        return jsonify({"message": "Notes added successfully"})
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/courses/<day>/timer/start', methods=['POST'])
def start_timer(day):
    if day in tracker.courses:
        tracker.courses[day]["start_time"] = datetime.now().isoformat()
        tracker.save_progress()
        return jsonify({"message": "Timer started"})
    return jsonify({"error": "Course not found"}), 404

@app.route('/api/courses/<day>/timer/stop', methods=['POST'])
def stop_timer(day):
    if day in tracker.courses:
        if tracker.courses[day]["start_time"]:
            start_time = datetime.fromisoformat(tracker.courses[day]["start_time"])
            duration = (datetime.now() - start_time).total_seconds() / 60
            tracker.courses[day]["time_spent"] += duration
            tracker.courses[day]["start_time"] = None
            tracker.save_progress()
            return jsonify({"message": "Timer stopped", "duration": duration})
    return jsonify({"error": "Course not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)