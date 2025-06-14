// components/Login.js
import React, { useState } from "react";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    // Basit örnek doğrulama – backend bağlantısı buraya eklenebilir
    if (email && password) {
      onLogin(); // App.js içinde navigate("/home")'e yönlendiriyor
    } else {
      alert("Lütfen e-posta ve şifre girin.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-box">
      <h2>Giriş Yap</h2>
      <input
        type="email"
        placeholder="E-posta"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Şifre"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Giriş</button>
    </form>
  );
}

export default Login;