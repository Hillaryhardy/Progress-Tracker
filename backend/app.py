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
            3: "Docker Multi-Stage Builds",
            4: "Why do We need Kubernetes?",
            5: "Kubernetes Architecture",
            6: "Install Kubernetes Cluster locally",
            7: "Pods in Kubernetes",
            8: "Replicasets and Deployments in Kubernetes",
            9: "Services in Kubernetes",
            10: "Namespaces",
            11: "Multi-container Pods",
            12: "Daemonset, Cronjob, and job",
            13: "Static Pods",
            14: "Taints and Tolerations",
            15: "Node Affinity",
            16: "Resource Requests and Limits",
            17: "Autoscaling in Kubernetes",
            18: "Probes in Kubernetes",
            19: "Config maps and Secrets",
            20: "How SSL/TLS works",
            21: "TLS in Kubernetes",
            22: "Authorization in Kubernetes",
            23: "Role-based access control (RBAC)",
            24: "Cluster role and cluster role binding",
            25: "Service Account",
            26: "Network Policies",
            27: "Use Kubeadm to install a Kubernetes cluster",
            28: "Docker storage fundamentals",
            29: "Storage in Kubernetes",
            30: "How does DNS work?",
            31: "DNS in kubernetes",
            32: "Kubernetes Networking",
            33: "Ingress controller and Ingress resources",
            34: "Perform a version upgrade on a Kubernetes cluster using Kubeadm",
            35: "Implement etcd backup and restore",
            36: "Monitoring, Logging and Alerting",
            37: "Troubleshoot application failure",
            38: "Troubleshoot cluster component failure",
            39: "Network Troubleshooting",
            40: "JSONPath, advance kubectl commands",
            41: "Mission CKA",
            42: "Realtime project: Host your own container registry on Kubernetes"
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

# Add a root route that shows the API is running
@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Kubernetes Tracker API is running",
        "endpoints": {
            "GET /api/courses": "Get all courses",
            "PUT /api/courses/<day>": "Update course",
            "POST /api/courses/<day>/complete": "Mark course as complete",
            "POST /api/courses/<day>/notes": "Add notes to course",
            "POST /api/courses/<day>/timer/start": "Start timer",
            "POST /api/courses/<day>/timer/stop": "Stop timer"
        }
    })

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