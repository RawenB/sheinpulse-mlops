import { useState } from "react";
import api from "../api";

export default function Chatbot({ prediction, predictionForm, recommendations }) {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi, I’m your SheinPulse assistant. I can explain predictions and recommendations.",
    },
  ]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = {
      role: "user",
      content: message,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      const payload = {
        message,
        prediction,
        article_id: predictionForm?.article_id
          ? Number(predictionForm.article_id)
          : null,
        year: predictionForm?.year ? Number(predictionForm.year) : null,
        week: predictionForm?.week ? Number(predictionForm.week) : null,
        recommendations: recommendations?.length ? recommendations : null,
      };

      const res = await api.post("/chat/explain", payload);

      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: res.data.reply,
        },
      ]);
      setMessage("");
    } catch (err) {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content:
            err.response?.data?.detail ||
            "Sorry, I couldn’t generate an explanation right now.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button className="chatbot-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? "×" : "AI"}
      </button>

      {isOpen && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <div>
              <h3>SheinPulse AI</h3>
              <span>Prediction & recommendation helper</span>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`chatbot-message ${
                  msg.role === "user" ? "user-message" : "assistant-message"
                }`}
              >
                {msg.content}
              </div>
            ))}

            {loading && (
              <div className="chatbot-message assistant-message">
                Thinking...
              </div>
            )}
          </div>

          <div className="chatbot-suggestions">
            <button
              onClick={() =>
                setMessage("What does this prediction mean?")
              }
            >
              Explain prediction
            </button>
            <button
              onClick={() =>
                setMessage("Explain these recommendations simply.")
              }
            >
              Explain recommendations
            </button>
          </div>

          <div className="chatbot-input-row">
            <input
              type="text"
              placeholder="Ask about the results..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button onClick={sendMessage} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}