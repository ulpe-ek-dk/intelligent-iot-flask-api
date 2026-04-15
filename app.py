from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge

load_dotenv()

app = Flask(__name__)

# ---------- PROMETHEUS METRICS ----------
metrics = PrometheusMetrics(app)

# Custom metrics der giver mening i en IoT-kontekst
device_status_gauge = Gauge(
    "iot_devices_online_total",
    "Antal IoT-enheder med status online"
)

db_errors_counter = Counter(
    "iot_db_errors_total",
    "Antal fejlede databasekald",
    ["operation"]  # label: get, post, put, delete
)

device_not_found_counter = Counter(
    "iot_device_not_found_total",
    "Antal kald hvor device_id ikke blev fundet"
)

# Static app info (vises i Grafana som info-panel)
metrics.info("iot_api_info", "Intelligent IoT Flask API", version="1.0")

# ---------- HELPERS ----------
def add(a, b):
    return a + b

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def update_online_gauge():
    """Opdatér gauge med antal online devices — kaldes ved GET /api/devices"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'online'")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        device_status_gauge.set(count)
    except Exception:
        db_errors_counter.labels(operation="gauge_update").inc()

# ---------- BASIC ROUTES ----------
@app.route("/ping", methods=["GET"])
def ping():
    return "pong from Intelligent IoT Flask API in Docker"

@app.route("/")
def index():
    return "Mini API med MySQL kører. Prøv /api/devices"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# ---------- DEVICES API ----------
@app.route("/api/devices", methods=["GET"])
def get_devices():
    """Hent alle IoT-enheder"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, location, status, customer_name, last_seen FROM devices")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        update_online_gauge()
        return jsonify(rows)
    except Exception as e:
        db_errors_counter.labels(operation="get").inc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/devices/<int:device_id>", methods=["GET"])
def get_device(device_id):
    """Hent én IoT-enhed"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, location, status, customer_name, last_seen FROM devices WHERE id = %s",
            (device_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        db_errors_counter.labels(operation="get").inc()
        return jsonify({"error": str(e)}), 500

    if row:
        return jsonify(row)
    else:
        device_not_found_counter.inc()
        return jsonify({"error": "Device not found"}), 404

@app.route("/api/devices", methods=["POST"])
def create_device():
    """Opret ny IoT-enhed"""
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO devices (name, location, status, customer_name, last_seen)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (data["name"], data["location"], data["status"], data["customer_name"])
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
    except Exception as e:
        db_errors_counter.labels(operation="post").inc()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": new_id,
        "name": data["name"],
        "location": data["location"],
        "status": data["status"],
        "customer_name": data["customer_name"],
        "last_seen": None
    }), 201

@app.route("/api/devices/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    """Opdatér eksisterende IoT-enhed"""
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            device_not_found_counter.inc()
            return jsonify({"error": "Device not found"}), 404

        cursor.execute(
            """
            UPDATE devices
            SET name = %s, location = %s, status = %s,
                customer_name = %s, last_seen = NOW()
            WHERE id = %s
            """,
            (data["name"], data["location"], data["status"], data["customer_name"], device_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        db_errors_counter.labels(operation="put").inc()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "id": device_id,
        "name": data["name"],
        "location": data["location"],
        "status": data["status"],
        "customer_name": data["customer_name"],
    })

@app.route("/api/devices/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    """Slet IoT-enhed"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            device_not_found_counter.inc()
            return jsonify({"error": "Device not found"}), 404

        cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        db_errors_counter.labels(operation="delete").inc()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": f"Device {device_id} deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)