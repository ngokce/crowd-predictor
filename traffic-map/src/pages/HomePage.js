// HomePage.js
import React, { useState } from "react";
import { GoogleMap, LoadScript, DirectionsRenderer } from "@react-google-maps/api";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useNavigate } from "react-router-dom";

const center = { lat: 41.0082, lng: 28.9784 };

const HomePage = () => {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [directions, setDirections] = useState(null);
  const [routeColor, setRouteColor] = useState("gray");
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!origin || !destination) return alert("Başlangıç ve varış noktası girin!");

    const directionsService = new window.google.maps.DirectionsService();

    directionsService.route(
      {
        origin,
        destination,
        travelMode: window.google.maps.TravelMode.DRIVING,
      },
      async (result, status) => {
        if (status === "OK") {
          setDirections(result);

          const response = await axios.post("http://localhost:5050/predict", {
            origin,
            destination,
            datetime: selectedDate.toISOString(),
            min_speed: 20,
            max_speed: 60,
            num_vehicles: 300
          }, {
            headers: {
              "Content-Type": "application/json"
            }
          });

          setRouteColor(response.data.color || "gray");
        } else {
          alert("Rota bulunamadı.");
        }
      }
    );
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div style={{ padding: 20 }}>
      <button onClick={handleLogout}>Çıkış Yap</button>
      <h2>🚦 Trafik Yoğunluğu Tahmin Haritası</h2>
      <input placeholder="Başlangıç noktası" value={origin} onChange={(e) => setOrigin(e.target.value)} />
      <input placeholder="Varış noktası" value={destination} onChange={(e) => setDestination(e.target.value)} />
      <DatePicker
        selected={selectedDate}
        onChange={(date) => setSelectedDate(date)}
        showTimeSelect
        dateFormat="Pp"
      />
      <button onClick={handleSubmit}>Haritada Göster</button>

      <div style={{ height: "500px", marginTop: 20 }}>
        <LoadScript googleMapsApiKey="AIzaSyCuqqRGTv_LHtkNzvPSLvVwLJhOg5uLxmo">
          <GoogleMap mapContainerStyle={{ height: "100%", width: "100%" }} center={center} zoom={12}>
            {directions && (
              <DirectionsRenderer
                directions={directions}
                options={{
                  polylineOptions: {
                    strokeColor: routeColor,
                    strokeWeight: 6
                  }
                }}
              />
            )}
          </GoogleMap>
        </LoadScript>
      </div>
    </div>
  );
};

export default HomePage;