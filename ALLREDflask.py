from flask import Flask, request, jsonify

app = Flask(__name__)

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
        
        # Simpan data ke database atau lakukan proses lainnya
        # Misalnya, cetak data ke konsol untuk debugging
        print(f"Received data - Temperature: {temperature}°C, Humidity: {humidity}%, Timestamp: {timestamp}")
        
        # Respon sukses
        return jsonify({"status": "success", "message": "Data received successfully"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)