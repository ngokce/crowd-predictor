// components/Register.js
import React, { useState } from "react";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = (e) => {
    e.preventDefault();

    if (name && email && password) {
      alert("Kayıt başarılı! Artık giriş yapabilirsiniz.");
      // Normalde burada backend'e kullanıcı gönderilir
    } else {
      alert("Lütfen tüm alanları doldurun.");
    }
  };

  return (
    <form onSubmit={handleRegister} className="form-box">
      <h2>Kayıt Ol</h2>
      <input
        type="text"
        placeholder="Ad Soyad"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
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
      <button type="submit">Kayıt Ol</button>
    </form>
  );
}

export default Register;