from flask import Flask, request, jsonify
import joblib
import pandas as pd
from datetime import datetime
from flask_cors import CORS
import requests
import geohash  # pip install geohash

app = Flask(__name__)
CORS(app)

# Google Geocoding API anahtarınızı buraya ekleyin
GOOGLE_API_KEY = "AIzaSyDOQepkRGNzynm4fxu9u9MN-qfPQcvOVu8"

# Global değişkenler
model = None


def load_model():
    global model
    try:
        model = joblib.load("trafik_model_sonRF.pkl")
        print("✅ Model başarıyla yüklendi")
        return True
    except FileNotFoundError:
        print("❌ Model dosyası bulunamadı! Önce modeli eğitin.")
        return False
    except Exception as e:
        print(f"❌ Model yükleme hatası: {str(e)}")
        return False


def get_lat_lng_from_address(address, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None


def extract_features_from_request(data):
    dt = pd.to_datetime(data.get("datetime"))
    hour = dt.hour
    day_of_week = dt.dayofweek
    is_weekend = int(day_of_week >= 5)
    month = dt.month

    min_speed = data.get("min_speed")
    max_speed = data.get("max_speed")
    num_vehicles = data.get("num_vehicles")

    # Adresten koordinat al (Google Geocoding API)
    address = data.get("origin", "Kadıköy, İstanbul")
    lat, lng = get_lat_lng_from_address(address, GOOGLE_API_KEY)
    if lat is None or lng is None:
        # fallback: Kadıköy (sadece API başarısız olursa)
        lat, lng = 40.9917, 29.0270

    # location_id üret (geohash stringini int'e çevir)
    location_id_str = geohash.encode(lat, lng, precision=6)
    location_id = hash(location_id_str) % 1000000  # 6 haneli pozitif bir sayı

    features = [
        hour, day_of_week, is_weekend, month,
        min_speed, max_speed, num_vehicles,
        location_id, lat, lng
    ]
    return features, {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": bool(is_weekend),
        "month": month,
        "min_speed": min_speed,
        "max_speed": max_speed,
        "num_vehicles": num_vehicles,
        "location_id": location_id,
        "location_id_str": location_id_str,
        "latitude": lat,
        "longitude": lng
    }


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "active",
        "message": "İstanbul Trafik Tahmin API'si",
        "model_loaded": model is not None,
        "endpoints": {
            "/predict": "POST - Trafik tahmini yap",
            "/health": "GET - API sağlık kontrolü",
            "/model-info": "GET - Model bilgileri"
        }
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_available": model is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş"}), 400

    return jsonify({
        "model_type": type(model).__name__,
        "feature_count": 10,
        "traffic_levels": {
            0: {"name": "Az", "color": "green", "description": "Trafik akışı normal"},
            1: {"name": "Orta", "color": "yellow", "description": "Trafik yavaşlaması var"},
            2: {"name": "Yoğun", "color": "red", "description": "Trafik çok yoğun"}
        },
        "required_fields": ["origin", "datetime", "min_speed", "max_speed", "num_vehicles"]
    })


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş. Lütfen önce modeli eğitin."}), 500

    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Veri tipi dict değil"}), 400

        required_fields = ["origin", "datetime", "min_speed", "max_speed", "num_vehicles"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400

        features, feature_info = extract_features_from_request(data)

        feature_names = [
            "hour", "day_of_week", "is_weekend", "month",
            "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
            "location_id", "LATITUDE", "LONGITUDE"
        ]
        features_df = pd.DataFrame([features], columns=feature_names)

        prediction = model.predict(features_df)[0]

        traffic_mapping = {
            0: {"level": "az", "color": "green", "description": "Trafik akışı normal"},
            1: {"level": "orta", "color": "yellow", "description": "Trafik yavaşlaması var"},
            2: {"level": "yogun", "color": "red", "description": "Trafik çok yoğun"}
        }

        print("Tahmin edilen trafik seviyesi:", prediction)
        print("Trafik info:", traffic_mapping[int(prediction)])
        print("Input features:", features_df)

        result = {
            "traffic_level": int(prediction),
            "traffic_info": traffic_mapping[int(prediction)],
            "input_features": feature_info,
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Hata detayını terminale yazdırır
        return jsonify({"error": f"Tahmin yapılırken hata oluştu: {str(e)}"}), 500


if __name__ == "__main__":
    if load_model():
        print("🚀 API başlatılıyor...")
        app.run(host="0.0.0.0", port=5050, debug=True)
    else:
        print("❌ Model yüklenemedi. Önce modeli eğitin.")