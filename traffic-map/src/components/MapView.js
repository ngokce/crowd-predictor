import React, { useRef } from 'react';
import { GoogleMap, LoadScript, Autocomplete } from '@react-google-maps/api';

const containerStyle = {
  width: '100vw',
  height: '100vh'
};

const center = {
  lat: 41.015137,
  lng: 28.979530
};

const MapView = () => {
  const originRef = useRef(null);
  const destRef = useRef(null);

  const handlePlaceSelect = () => {
    const origin = originRef.current.getPlace();
    const destination = destRef.current.getPlace();
    // Seçilen yerlerin koordinatlarını veya adreslerini burada kullanabilirsin
    console.log('Başlangıç:', origin);
    console.log('Varış:', destination);
  };

  return (
    <LoadScript
      googleMapsApiKey="AIzaSyBde68On8mSOpk3HPNtkDhBIyUJkau1bww"
      libraries={['places']}
    >
      
      <div style={{ position: 'absolute', zIndex: 10, top: 80, left: 10, background: '#fff', padding: 5, borderRadius: 10 }}>

        <Autocomplete onPlaceChanged={handlePlaceSelect} ref={originRef}>
          <input type="text" placeholder="Başlangıç Noktası" style={{ width: 250, marginBottom: 8 }} />
        </Autocomplete>
        <br />
        <Autocomplete onPlaceChanged={handlePlaceSelect} ref={destRef}>
          <input type="text" placeholder="Varış Noktası" style={{ width: 250 }} />
        </Autocomplete>
      </div>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={12}
      >
        {/* Harita üstünde başka şeyler de gösterebilirsin */}
      </GoogleMap>
    </LoadScript>
  );
};

export default MapView;