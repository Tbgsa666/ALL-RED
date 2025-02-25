from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Konfigurasi MongoDB Atlas
MONGO_URI = "mongodb+srv://allreddb:<allred507>@cluster0.3gn1v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "sensor_data"
COLLECTION_NAME = "dht11"

# Inisialisasi koneksi MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Endpoint untuk menerima data dari ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        # Membaca data JSON dari permintaan
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # Ekstrak nilai suhu dan kelembaban
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        timestamp = data.get('timestamp')
        
        if temperature is None or humidity is None or timestamp is None:
            return jsonify({"status": "error", "message": "Incomplete data"}), 400
        
        # Simpan data ke MongoDB Atlas
        document = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": timestamp
        }
        collection.insert_one(document)
        
        # Respon sukses
        return jsonify({"status": "success", "message": "Data received and stored successfully"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)