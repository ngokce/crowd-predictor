// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import axios from "axios";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />   {/* Açılış ekranı */}
        <Route path="/home" element={<HomePage />} /> {/* Giriş sonrası ekran */}
      </Routes>
    </Router>
  );
}

export default App;