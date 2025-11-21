from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),          
        password=os.getenv("DB_PASSWORD"),  
        database=os.getenv("DB_NAME") 
    )

# CI test: bevidst syntaksfejl
def ci_test_function(
    return "this will break"

# ---------- BASIC ROUTES ----------
@app.route("/ping", methods=["GET"])
def ping():
    return "pong from Intelligent IoT Flask API in Docker"

@app.route("/")
def index():
    return "Mini API med MySQL kører. Prøv /api/devices"

# ---------- DEVICES API (Intelligent IoT Solutions case) ----------

@app.route("/api/devices", methods=["GET"])
def get_devices():
    """
    Hent alle IoT-enheder
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, location, status, customer_name, last_seen FROM devices")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/devices/<int:device_id>", methods=["GET"])
def get_device(device_id):
    """
    Hent én IoT-enhed
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, location, status, customer_name, last_seen FROM devices WHERE id = %s",
        (device_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return jsonify(row)
    else:
        return jsonify({"error": "Device not found"}), 404

@app.route("/api/devices", methods=["POST"])
def create_device():
    """
    Opret ny IoT-enhed
    """
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400

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

    new_device = {
        "id": new_id,
        "name": data["name"],
        "location": data["location"],
        "status": data["status"],
        "customer_name": data["customer_name"],
        "last_seen": None  # eller lad frontend lave et nyt GET-kald
    }
    return jsonify(new_device), 201

@app.route("/api/devices/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    """
    Opdatér eksisterende IoT-enhed
    """
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # tjek om device findes
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Device not found"}), 404

    # opdatér
    cursor.execute(
        """
        UPDATE devices
        SET name = %s,
            location = %s,
            status = %s,
            customer_name = %s,
            last_seen = NOW()
        WHERE id = %s
        """,
        (data["name"], data["location"], data["status"], data["customer_name"], device_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    updated_device = {
        "id": device_id,
        "name": data["name"],
        "location": data["location"],
        "status": data["status"],
        "customer_name": data["customer_name"],
        # last_seen kan evt. hentes med et nyt GET-kald
    }
    return jsonify(updated_device)

@app.route("/api/devices/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    """
    Slet IoT-enhed
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Device not found"}), 404

    cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"Device {device_id} deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

