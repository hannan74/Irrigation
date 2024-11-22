from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('irrigation.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS SensorData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        soilMoisture INTEGER,
        lightIntensity INTEGER,
        solarPower BOOLEAN,
        daylight BOOLEAN,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.close()

# Function to simulate irrigation control (triggering the water pump based on conditions)
def control_irrigation(soil_moisture, daylight, solar_power):
    if soil_moisture < 40 and daylight and solar_power:  # Soil is dry, it's day, and solar power is available
        return "Irrigation started"
    else:
        return "Irrigation stopped"

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    soil_moisture = data.get('soilMoisture')
    light_intensity = data.get('lightIntensity')
    solar_power = data.get('solarPower')
    daylight = data.get('daylight')

    # Save data to the database
    conn = sqlite3.connect('irrigation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SensorData (soilMoisture, lightIntensity, solarPower, daylight) VALUES (?, ?, ?, ?)",
                   (soil_moisture, light_intensity, solar_power, daylight))
    conn.commit()
    conn.close()

    # Control irrigation based on received data
    irrigation_status = control_irrigation(soil_moisture, daylight, solar_power)

    return jsonify({
        "message": "Data received successfully",
        "irrigationStatus": irrigation_status
    }), 201

@app.route('/api/status', methods=['GET'])
def get_status():
    conn = sqlite3.connect('irrigation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorData ORDER BY timestamp DESC LIMIT 1")
    data = cursor.fetchone()
    conn.close()

    if data:
        return jsonify({
            "soilMoisture": data[1],
            "lightIntensity": data[2],
            "solarPower": data[3],
            "daylight": data[4],
            "timestamp": data[5]
        })
    else:
        return jsonify({"message": "No data available"}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
