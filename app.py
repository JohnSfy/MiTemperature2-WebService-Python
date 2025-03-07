from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "https://mi-temperature2-monitor-fronmt-end-inky.vercel.app", 
                             "methods": ["GET", "POST"],
                             "allow_headers": ["Content-Type", "Authorization"]}})

# Configure database
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models (equivalent to sensor.entity.ts)
class SensorMeasurement(db.Model):
    __tablename__ = 'sensor_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_name = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Numeric(5, 2), nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    calibrated_humidity = db.Column(db.Integer, nullable=False)
    battery_voltage = db.Column(db.Numeric(4, 3), nullable=True)
    battery_percent = db.Column(db.Integer, nullable=True)
    rssi = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    raspberry_pi_temperature = db.Column(db.Numeric(5, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_name': self.sensor_name,
            'temperature': float(self.temperature),
            'humidity': self.humidity,
            'calibrated_humidity': self.calibrated_humidity,
            'battery_voltage': float(self.battery_voltage) if self.battery_voltage else None,
            'battery_percent': self.battery_percent,
            'rssi': self.rssi,
            'timestamp': self.timestamp.isoformat(),
            'raspberry_pi_temperature': float(self.raspberry_pi_temperature)
        }

# Service functions (equivalent to sensor.service.ts)
def get_all_measurements():
    return SensorMeasurement.query.all()

def get_by_room(room):
    return SensorMeasurement.query.filter_by(sensor_name=room).all()

# Routes (equivalent to sensor.controller.ts)
@app.route('/sensors', methods=['GET'])
def get_all():
    measurements = get_all_measurements()
    return jsonify([m.to_dict() for m in measurements])

@app.route('/sensors/<room>', methods=['GET'])
def get_by_room_route(room):
    measurements = get_by_room(room)
    return jsonify([m.to_dict() for m in measurements])

# Root route (equivalent to app.controller.ts)
@app.route('/', methods=['GET'])
def get_hello():
    return "Hello World!"

# Create tables if they don't exist
@app.before_first_request
def create_tables():
    db.create_all()

# Main entry point
if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Start the server
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)