import { useState, useEffect, useRef } from "react";
import chatbotIcon from "./images/icon.png";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { sender: "Lunera", text: "Merhaba! Ben Lunera'nın dijital asistanıyım. Size nasıl yardımcı olabilirim?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: "Siz", text: input };
    setMessages([...messages, userMsg]);
    setLoading(true);

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();
    const botMsg = {
  sender: "Lunera",
  text:
    typeof data.reply === "string"
      ? data.reply
      : data.reply?.output || "Bir yanıt alınamadı."
};
    setMessages((prev) => [...prev, botMsg]);
    setInput("");
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="header">
        <img src={chatbotIcon} alt="ChatBot" />
      </div>
      <div className="messages-container">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender === "Siz" ? "user-message" : "bot-message"}`}
          >
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div className="loading">Yanıt bekleniyor...</div>}
        <div ref={messagesEndRef} />
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
