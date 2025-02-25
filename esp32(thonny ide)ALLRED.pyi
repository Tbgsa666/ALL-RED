from machine import Pin
import dht
import urequests
import network
import time
import usocket
import ujson
from utime import ticks_ms, ticks_diff
import ustruct

# Konfigurasi Wi-Fi
WIFI_SSID = 'Guru-Tu-SMKN13BDG'  
WIFI_PASSWORD = 'Semangat2025*'  

# Konfigurasi sensor DHT11
DHT_PIN = 4 
sensor = dht.DHT11(Pin(DHT_PIN))

# Konfigurasi Ubidots
UBIDOTS_TOKEN = 'BBUS-bRvnaUTlt8tW70NwkxW30uwwM59R7h'  
DEVICE_LABEL = 'esp32allred'  
TEMPERATURE_VARIABLE_LABEL = 'temperature'
HUMIDITY_VARIABLE_LABEL = 'humidity'

# URL Flask Server
FLASK_SERVER_URL = "http://10.200.19.201:5000/data"  

def connect_wifi(ssid, password):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f'Menghubungkan ke jaringan Wi-Fi: {ssid}...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(f'Terkoneksi ke jaringan Wi-Fi. IP Address: {wlan.ifconfig()[0]}')

def read_dht_sensor():
    try:
        sensor.measure()  
        temperature = sensor.temperature()  
        humidity = sensor.humidity() 
        return temperature, humidity
    except OSError as e:
        print(f"Gagal membaca sensor, sensor mungkin rusak, coba lagi dalam 10 detik: {e}")
        return None, None

def send_to_ubidots(temperature, humidity):
    url = f'https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}'
    headers = {
        'X-Auth-Token': UBIDOTS_TOKEN,
        'Content-Type': 'application/json'
    }
    payload = {
        TEMPERATURE_VARIABLE_LABEL: temperature,
        HUMIDITY_VARIABLE_LABEL: humidity
    }
    
    try:
        response = urequests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print('Data berhasil dikirim ke Ubidots.')
        else:
            print(f"Gagal mengirim data ke Ubidots. Kode status: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim data ke Ubidots: {e}")

def send_to_flask(temperature, humidity, timestamp):
    data = {
        'temperature': temperature,
        'humidity': humidity,
        'timestamp': timestamp
    }
    
    try:
        response = urequests.post(FLASK_SERVER_URL, json=data)
        if response.status_code == 200:
            print('Data berhasil dikirim ke Flask Server.')
        else:
            print(f"Gagal mengirim data ke Flask Server. Kode status: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim data ke Flask Server: {e}")

def get_timestamp():
    ntp_server = "pool.ntp.org"
    timezone_offset = 7 * 3600  # WIB (UTC+7)
    
    def set_time():
        ntp = usocket.getaddrinfo(ntp_server, 123)[0][-1]
        s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            msg = bytearray(48)
            msg[0] = 0x1b
            s.sendto(msg, ntp)
            msg = s.recv(48)
            val = ustruct.unpack("!I", msg[40:44])[0]
            return val - 2208988800 + timezone_offset
        finally:
            s.close()
    
    try:
        ntp_time = set_time()
        return ntp_time
    except OSError:
        return ticks_ms() // 1000

def main():
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    
    while True:
        temperature, humidity = read_dht_sensor()
        if temperature is not None and humidity is not None:
            print(f"Suhu: {temperature}°C, Kelembaban: {humidity}%")
            
            # Mendapatkan timestamp
            timestamp = get_timestamp()
            
            # Mengirim data ke Ubidots
            send_to_ubidots(temperature, humidity)
            
            # Mengirim data ke Flask Server
            send_to_flask(temperature, humidity, timestamp)
        time.sleep(10)  # Menunggu 10 detik sebelum membaca kembali

if __name__ == '__main__':
    main()
