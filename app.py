import psutil
import threading
import time
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Default threshold values (can be set via environment variables)
CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", 80))
MEMORY_THRESHOLD = int(os.getenv("MEMORY_THRESHOLD", 80))

# Shared variables for metrics
system_metrics = {"cpu": 0, "memory": 0}

def collect_metrics():
    """Background thread to update system metrics every 5 seconds."""
    while True:
        system_metrics["cpu"] = psutil.cpu_percent(interval=1)
        system_metrics["memory"] = psutil.virtual_memory().percent
        time.sleep(5)

# Start metrics collection in a separate thread
metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
metrics_thread.start()

@app.route("/")
def index():
    cpu_metric = system_metrics["cpu"]
    mem_metric = system_metrics["memory"]
    message = None

    if cpu_metric > CPU_THRESHOLD or mem_metric > MEMORY_THRESHOLD:
        message = "High CPU or Memory Usage Detected! Consider Scaling Up!"

    return render_template("index.html", cpu_metric=cpu_metric, mem_metric=mem_metric, message=message)

@app.route("/health")
def health():
    """Health check endpoint to monitor system status."""
    return jsonify({"cpu": system_metrics["cpu"], "memory": system_metrics["memory"]}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
