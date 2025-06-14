from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import traceback

from flask_cors import CORS
app = Flask(__name__)
CORS(app)


# Global değişkenler
model = None
scaler = None


def load_model_and_scaler():
    """Model ve scaler'ı yükle"""
    global model, scaler
    try:
        model = joblib.load("trafik_model.pkl")
        # Scaler'ı da kaydetmek gerekecek, şimdilik yeniden oluşturalım
        scaler = StandardScaler()
        print("✅ Model başarıyla yüklendi")
        return True
    except FileNotFoundError:
        print("❌ Model dosyası bulunamadı! Önce modeli eğitin.")
        return False
    except Exception as e:
        print(f"❌ Model yükleme hatası: {str(e)}")
        return False


def extract_features_from_request(data):
    print("✅ extract_features_from_request döndü")
    """Request'ten gelişmiş özellikler çıkar"""
    try:
        # Yeni: Başlangıç ve varış noktalarını terminale yazdır
        origin = data.get("origin", "")
        destination = data.get("destination", "")
        print("🟢 Origin:", origin)
        print("🔵 Destination:", destination)

        # Temel zaman bilgileri
        if "datetime" in data:
            dt = datetime.fromisoformat(data["datetime"].replace("Z", "+00:00"))
            hour = dt.hour
            day_of_week = dt.weekday()
            month = dt.month
            day = dt.day
        else:
            hour = data.get("hour", 12)
            day_of_week = data.get("day_of_week", 1)
            month = data.get("month", 1)
            day = data.get("day", 1)

        is_weekend = int(day_of_week >= 5)
        rush_hour_morning = int(7 <= hour <= 9)
        rush_hour_evening = int(17 <= hour <= 19)
        night_time = int(hour >= 22 or hour <= 6)

        min_speed = data.get("min_speed", 20)
        max_speed = data.get("max_speed", 60)
        num_vehicles = data.get("num_vehicles", 300)

        speed_range = max_speed - min_speed
        avg_speed_estimate = (min_speed + max_speed) / 2
        speed_variance = speed_range / (avg_speed_estimate + 1)
        congestion_ratio = num_vehicles / (avg_speed_estimate + 1)

        features = [
            hour, day_of_week, is_weekend, month, day,
            rush_hour_morning, rush_hour_evening, night_time,
            min_speed, max_speed, num_vehicles,
            speed_range, speed_variance, congestion_ratio
        ]

        return features, {
            "origin": origin,
            "destination": destination,
            "hour": hour,
            "day_of_week": day_of_week,
            "is_weekend": bool(is_weekend),
            "rush_hour_morning": bool(rush_hour_morning),
            "rush_hour_evening": bool(rush_hour_evening),
            "night_time": bool(night_time),
            "estimated_avg_speed": avg_speed_estimate,
            "congestion_ratio": congestion_ratio
        }

    except Exception as e:
        raise ValueError(f"Özellik çıkarma hatası: {str(e)}")


@app.route("/", methods=["GET"])
def home():
    """Ana sayfa - API durumu"""
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
    """Sağlık kontrolü"""
    return jsonify({
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_available": model is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    """Model bilgileri"""
    if model is None:
        return jsonify({"error": "Model yüklenmemiş"}), 400

    return jsonify({
        "model_type": type(model).__name__,
        "feature_count": 14,
        "traffic_levels": {
            0: {"name": "Az", "color": "green", "description": "Trafik akışı normal"},
            1: {"name": "Orta", "color": "yellow", "description": "Trafik yavaşlaması var"},
            2: {"name": "Yoğun", "color": "red", "description": "Trafik çok yoğun"}
        },
        "required_fields": ["datetime", "min_speed", "max_speed", "num_vehicles"],
        "optional_fields": ["hour", "day_of_week", "month", "day"]
    })


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş. Lütfen önce modeli eğitin."}), 500

    try:
        data = request.get_json()
        print("🔥 Gelen veri:", data)  # geçici

        if not isinstance(data, dict):
            return jsonify({"error": "Veri tipi dict değil"}), 400

        if not all(key in data for key in ["datetime", "min_speed", "max_speed", "num_vehicles"]):
            return jsonify({"error": "Zorunlu alanlar eksik"}), 400

        # geçici: Eksik alan kontrolü
        required_fields = ["datetime", "min_speed", "max_speed", "num_vehicles"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400

        # Özellikleri çıkar
        features, feature_info = extract_features_from_request(data)

        # DataFrame oluştur
        feature_names = [
            "hour", "day_of_week", "is_weekend", "month", "day",
            "rush_hour_morning", "rush_hour_evening", "night_time",
            "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
            "speed_range", "speed_variance", "congestion_ratio"
        ]
        features_df = pd.DataFrame([features], columns=feature_names)

        # Geçici log – özellikleri yazdır
        print("📊 Özellikler DF:")
        print(features_df.head())  # geçici

        if hasattr(model, 'kernel') or 'Logistic' in str(type(model)):
            features_scaled = scaler.fit_transform(features_df)
            prediction = model.predict(features_scaled)[0]
            try:
                probabilities = model.predict_proba(features_scaled)[0]
                prob_dict = {
                    "az": float(probabilities[0]),
                    "orta": float(probabilities[1]),
                    "yogun": float(probabilities[2])
                }
            except:
                prob_dict = None
        else:
            prediction = model.predict(features_df)[0]
            try:
                probabilities = model.predict_proba(features_df)[0]
                prob_dict = {
                    "az": float(probabilities[0]),
                    "orta": float(probabilities[1]),
                    "yogun": float(probabilities[2])
                }
            except:
                prob_dict = None

        traffic_mapping = {
            0: {"level": "az", "color": "green", "description": "Trafik akışı normal"},
            1: {"level": "orta", "color": "yellow", "description": "Trafik yavaşlaması var"},
            2: {"level": "yogun", "color": "red", "description": "Trafik çok yoğun"}
        }

        result = {
            "traffic_level": int(prediction),
            "traffic_info": traffic_mapping[int(prediction)],
            "probabilities": prob_dict,
            "input_features": feature_info,
            "timestamp": datetime.now().isoformat(),
            "model_confidence": "high" if prob_dict and max(prob_dict.values()) > 0.7 else "medium"
        }

        return jsonify(result)


    except ValueError as ve:
        print(f"ValueError: {ve}")
        return jsonify({"error": f"Veri hatası: {str(ve)}"}), 400
    except Exception as e:
        print(f"Tahmin hatası: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Tahmin yapılırken hata oluştu: {str(e)}"}), 500

@app.route("/predict-batch", methods=["POST"])
def predict_batch():
    """Toplu tahmin yapma"""
    if model is None:
        return jsonify({"error": "Model yüklenmemiş"}), 500

    try:
        data = request.get_json()

        if not data or "predictions" not in data:
            return jsonify({"error": "Toplu tahmin için 'predictions' listesi gerekli"}), 400

        results = []

        for i, item in enumerate(data["predictions"]):
            try:
                features, feature_info = extract_features_from_request(item)
                feature_names = [
                    "hour", "day_of_week", "is_weekend", "month", "day",
                    "rush_hour_morning", "rush_hour_evening", "night_time",
                    "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
                    "speed_range", "speed_variance", "congestion_ratio"
                ]

                features_df = pd.DataFrame([features], columns=feature_names)
                prediction = model.predict(features_df)[0]

                traffic_mapping = {
                    0: {"level": "az", "color": "green"},
                    1: {"level": "orta", "color": "yellow"},
                    2: {"level": "yogun", "color": "red"}
                }

                results.append({
                    "index": i,
                    "traffic_level": int(prediction),
                    "traffic_info": traffic_mapping[int(prediction)],
                    "input_features": feature_info
                })

            except Exception as e:
                results.append({
                    "index": i,
                    "error": f"Bu öğe için tahmin yapılamadı: {str(e)}"
                })

        return jsonify({
            "batch_results": results,
            "total_processed": len(data["predictions"]),
            "successful_predictions": len([r for r in results if "error" not in r]),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Toplu tahmin hatası: {str(e)}"}), 500


if __name__ == "__main__":
    # Model yükle
    if load_model_and_scaler():
        print("🚀 API başlatılıyor...")
        app.run(host="0.0.0.0", port=5050, debug=True)
    else:
        print("❌ Model yüklenemedi. Önce improved_model.py'ı çalıştırın.")