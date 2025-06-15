# Trafik Yoğunluğu Tahmin Projesi

Bu proje, belirli bir rota üzerindeki trafik yoğunluğunu tahmin eden bir web uygulamasıdır.

## Özellikler

- Başlangıç ve varış noktası seçimi
- Tarih ve saat seçimi
- Trafik parametrelerini ayarlama (hız limitleri, araç sayısı)
- Trafik yoğunluğu tahmini (Az/Orta/Yoğun)
- Harita üzerinde renkli rota gösterimi

## Kurulum

### Backend (Python/Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend (React)

```bash
cd traffic-map
npm install
npm start
```

## Gereksinimler

### Backend
- Python 3.8+
- Flask
- scikit-learn
- pandas
- numpy
- joblib

### Frontend
- Node.js 14+
- React
- @react-google-maps/api
- axios
- react-datepicker

## Kullanım

1. Frontend'i başlatın (http://localhost:3000)
2. Backend'i başlatın (http://localhost:5050)
3. Başlangıç ve varış noktalarını girin
4. Tarih ve saat seçin
5. Trafik parametrelerini ayarlayın
6. "Haritada Göster" butonuna tıklayın

## API Endpoints

- `GET /`: API durumu
- `GET /health`: Sağlık kontrolü
- `GET /model-info`: Model bilgileri
- `POST /predict`: Trafik tahmini

## Lisans

MIT 