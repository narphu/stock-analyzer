import { useState } from "react";
import axios from "axios";

function App() {
  const [ticker, setTicker] = useState("");
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPredictions(null);
    setError("");

    try {
      const res = await axios.post("http://localhost:8000/predict", { ticker });
      setPredictions(res.data.predictions);
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-xl mx-auto bg-white p-6 rounded-xl shadow space-y-6">
        <h1 className="text-2xl font-bold">📈 Stock Price Forecast</h1>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter ticker (e.g., AAPL)"
            className="w-full border p-2 rounded mb-4"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Predict
          </button>
        </form>

        {loading && <p className="text-blue-600">⏳ Loading...</p>}
        {error && <p className="text-red-600">❌ {error}</p>}

        {predictions && (
          <table className="w-full mt-4 border">
            <thead className="bg-gray-200">
              <tr>
                <th className="p-2">Days Ahead</th>
                <th className="p-2">Date</th>
                <th className="p-2">Predicted Price ($)</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => (
                <tr key={p.days}>
                  <td className="p-2 text-center">{p.days}</td>
                  <td className="p-2 text-center">{p.date}</td>
                  <td className="p-2 text-center font-semibold">{p.price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;
