// LoginPage.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import background from "./background.jpg";
import Login from "../components/Login";
import Register from "../components/Register";
import "../App.css";

function LoginPage() {
  const [showLogin, setShowLogin] = useState(true);
  const navigate = useNavigate();

  const handleLogin = () => {
    // token veya giriş doğrulaması yapılabilir
    localStorage.setItem("token", "dummy");
    navigate("/home");
  };

  return (
    <div
      className="App"
      style={{
        minHeight: "100vh",
        background: `url(${background}) no-repeat center center fixed`,
        backgroundSize: "cover",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
      <div className="auth-container">
        <div className="tab-buttons">
          <button
            className={`tab-btn${showLogin ? " active" : ""}`}
            onClick={() => setShowLogin(true)}
          >
            Giriş Yap
          </button>
          <button
            className={`tab-btn${!showLogin ? " active" : ""}`}
            onClick={() => setShowLogin(false)}
          >
            Kayıt Ol
          </button>
        </div>
        {showLogin ? <Login onLogin={handleLogin} /> : <Register />}
      </div>
    </div>
  );
}

export default LoginPage;