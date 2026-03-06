import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [predictionForm, setPredictionForm] = useState({
    article_id: "",
    year: "2018",
    week: "38",
  });

  const [recommendationForm, setRecommendationForm] = useState({
    customer_id: "",
    top_k: "5",
  });

  const [prediction, setPrediction] = useState(null);
  const [predictionError, setPredictionError] = useState("");
  const [predictionLoading, setPredictionLoading] = useState(false);

  const [recommendations, setRecommendations] = useState([]);
  const [recommendationError, setRecommendationError] = useState("");
  const [recommendationLoading, setRecommendationLoading] = useState(false);

  const [apiStatus, setApiStatus] = useState("Checking...");
  const [modelInfo, setModelInfo] = useState("");

  useEffect(() => {
    const checkApi = async () => {
      try {
        const healthRes = await axios.get(`${API_BASE_URL}/health`);
        setApiStatus(healthRes.data.status === "ok" ? "Connected" : "Unavailable");

        const modelRes = await axios.get(`${API_BASE_URL}/model-info`);
        setModelInfo(modelRes.data.model_uri || "No model info");
      } catch {
        setApiStatus("Offline");
        setModelInfo("Unable to load model info");
      }
    };

    checkApi();
  }, []);

  const handlePredictionChange = (e) => {
    const { name, value } = e.target;
    setPredictionForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRecommendationChange = (e) => {
    const { name, value } = e.target;
    setRecommendationForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePredictionSubmit = async (e) => {
    e.preventDefault();
    setPredictionLoading(true);
    setPredictionError("");
    setPrediction(null);

    try {
      const payload = {
        article_id: Number(predictionForm.article_id),
        year: Number(predictionForm.year),
        week: Number(predictionForm.week),
      };

      const response = await axios.post(`${API_BASE_URL}/predict`, payload);
      setPrediction(response.data.prediction);
    } catch (err) {
      setPredictionError(
        err.response?.data?.detail ||
          "Prediction failed. Please check the input values."
      );
    } finally {
      setPredictionLoading(false);
    }
  };

  const handleRecommendationSubmit = async (e) => {
    e.preventDefault();
    setRecommendationLoading(true);
    setRecommendationError("");
    setRecommendations([]);

    try {
      const customerId = recommendationForm.customer_id.trim();
      const topK = Number(recommendationForm.top_k) || 5;

      const response = await axios.get(
        `${API_BASE_URL}/recommend/${customerId}?top_k=${topK}`
      );

      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      setRecommendationError(
        err.response?.data?.detail ||
          "Recommendation request failed. Please check the customer ID."
      );
    } finally {
      setRecommendationLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="background-glow background-glow-1"></div>
      <div className="background-glow background-glow-2"></div>

      <div className="container">
        <header className="hero">
          <div>
            <p className="eyebrow">MLOps Fashion Intelligence</p>
            <h1>SheinPulse Dashboard</h1>
            <p className="subtitle">
              Demand prediction and customer recommendation served with FastAPI
              and tracked with MLflow.
            </p>
          </div>

          <div className="status-box">
            <div className="status-row">
              <span>API Status</span>
              <span
                className={`badge ${
                  apiStatus === "Connected"
                    ? "badge-success"
                    : apiStatus === "Checking..."
                    ? "badge-neutral"
                    : "badge-error"
                }`}
              >
                {apiStatus}
              </span>
            </div>

            <div className="status-row status-column">
              <span>Model</span>
              <small>{modelInfo}</small>
            </div>
          </div>
        </header>

        <main className="dashboard-grid">
          <section className="card">
            <h2>Demand Prediction</h2>
            <p className="card-text">
              Predict weekly demand for a selected article.
            </p>

            <form className="form" onSubmit={handlePredictionSubmit}>
              <div className="input-group">
                <label htmlFor="article_id">Article ID</label>
                <input
                  id="article_id"
                  name="article_id"
                  type="number"
                  placeholder="Enter article ID"
                  value={predictionForm.article_id}
                  onChange={handlePredictionChange}
                  required
                />
              </div>

              <div className="row">
                <div className="input-group">
                  <label htmlFor="year">Year</label>
                  <input
                    id="year"
                    name="year"
                    type="number"
                    value={predictionForm.year}
                    onChange={handlePredictionChange}
                    required
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="week">Week</label>
                  <input
                    id="week"
                    name="week"
                    type="number"
                    min="1"
                    max="52"
                    value={predictionForm.week}
                    onChange={handlePredictionChange}
                    required
                  />
                </div>
              </div>

              <button
                className="predict-btn"
                type="submit"
                disabled={predictionLoading}
              >
                {predictionLoading ? "Predicting..." : "Run Prediction"}
              </button>
            </form>

            {predictionError && (
              <div className="message error-message">{predictionError}</div>
            )}

            <div className="result-box compact-result">
              {prediction !== null ? (
                <>
                  <span className="result-label">Predicted Demand</span>
                  <span className="result-value">
                    {Number(prediction).toFixed(2)}
                  </span>
                </>
              ) : (
                <div className="empty-state">
                  <p>No prediction yet</p>
                  <span>Submit the form to view the output</span>
                </div>
              )}
            </div>
          </section>

          <section className="card">
            <h2>Customer Recommendations</h2>
            <p className="card-text">
              Get top product recommendations for a customer.
            </p>

            <form className="form" onSubmit={handleRecommendationSubmit}>
              <div className="input-group">
                <label htmlFor="customer_id">Customer ID</label>
                <input
                  id="customer_id"
                  name="customer_id"
                  type="text"
                  placeholder="Enter customer ID"
                  value={recommendationForm.customer_id}
                  onChange={handleRecommendationChange}
                  required
                />
              </div>

              <div className="input-group">
                <label htmlFor="top_k">Number of recommendations</label>
                <input
                  id="top_k"
                  name="top_k"
                  type="number"
                  min="1"
                  max="20"
                  value={recommendationForm.top_k}
                  onChange={handleRecommendationChange}
                  required
                />
              </div>

              <button
                className="predict-btn"
                type="submit"
                disabled={recommendationLoading}
              >
                {recommendationLoading ? "Loading..." : "Get Recommendations"}
              </button>
            </form>

            {recommendationError && (
              <div className="message error-message">{recommendationError}</div>
            )}

            <div className="recommendation-list">
              {recommendations.length > 0 ? (
                recommendations.map((item) => (
                  <div className="recommendation-card" key={item.article_id}>
                    <div className="recommendation-top">
                      <span className="recommendation-id">
                        #{item.article_id}
                      </span>
                    </div>
                    <h3>{item.prod_name || "Unknown product"}</h3>
                    <p>{item.product_type_name || "Unknown type"}</p>
                    <span className="recommendation-tag">
                      {item.product_group_name || "Unknown group"}
                    </span>
                  </div>
                ))
              ) : (
                <div className="empty-state recommendation-empty">
                  <p>No recommendations yet</p>
                  <span>Enter a customer ID to load recommended products</span>
                </div>
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;