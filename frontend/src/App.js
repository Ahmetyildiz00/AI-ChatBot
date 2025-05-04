import { useState } from "react";
import chatbotIcon from "./images/icon.png";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { sender: "ChatBot", text: "Sisteme Hoşgeldiniz" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: "Kullanıcı", text: input };
    setMessages([...messages, userMsg]);
    setLoading(true);

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();
    const botMsg = { sender: "ChatBot", text: data.reply };
    setMessages((prev) => [...prev, botMsg]);
    setInput("");
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="header">
        <img src={chatbotIcon} alt="ChatBot" />
        <h2>ChatBot</h2>
      </div>
      <div className="messages-container">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender === "Kullanıcı" ? "user-message" : "bot-message"}`}
          >
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div>Yanıt bekleniyor...</div>}
      </div>
      <form onSubmit={sendMessage} className="input-container">
        <input
          type="text"
          value={input}
          placeholder="Sorunuzu yazın..."
          onChange={(e) => setInput(e.target.value)}
          className="message-input"
        />
        <button type="submit" className="send-button">Gönder</button>
      </form>
    </div>
  );
}

export default App;
