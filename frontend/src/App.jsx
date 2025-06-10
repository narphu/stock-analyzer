import { useState } from "react";
import axios from "axios";
import SideBar from "./components/SideBar";
import SearchBar from "./components/SearchBar";
import Dashboard from "./components/Dashboard";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchPredictions = async (ticker) => {
    setLoading(true);
    setError("");
    setPredictions([]);

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
    <div className="flex min-h-screen bg-gray-100">
      <SideBar />
      <main className="flex-1 p-6">
        <div className="max-w-4xl mx-auto bg-white p-6 rounded-xl shadow space-y-6">
          <h1 className="text-3xl font-bold">📈 Stock Price Forecast</h1>

          <SearchBar onSelect={fetchPredictions} />

          {loading && <p className="text-blue-600">⏳ Loading predictions...</p>}
          {error && <p className="text-red-600">❌ {error}</p>}

          {predictions.length > 0 ? (
            <>
              <Dashboard predictions={predictions} />
              <table className="w-full mt-6 border text-sm">
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
            </>
          ) : (
            <p className="text-gray-500 text-center mt-6">
              Enter a ticker to see predictions.
            </p>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
