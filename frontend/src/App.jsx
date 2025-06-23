import { useState } from "react";
import axios from "axios";
import {
  Box,
  Flex,
  Heading,
  Spinner,
  Text,
  useColorModeValue,
  VStack,
} from "@chakra-ui/react";

import TickerSearch from "./components/TickerSearch";
import Dashboard from "./components/Dashboard";
import Navbar from "./components/NavBar";
import Sidebar from "./components/SideBar";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchPredictions = async (ticker) => {
    setLoading(true);
    setError("");
    setPredictions([]);
    setMetrics([]);
    setSelectedTicker(ticker);

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/predict`, { ticker });
      setPredictions(res.data.predictions);

      const metricsRes = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/metrics?ticker=${ticker}`);
      setMetrics(metricsRes.data.metrics);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex direction="column" minH="100vh">
      <Navbar />
      <Flex flex="1" bg={useColorModeValue("gray.50", "gray.900")}>
        <Sidebar />

        <Box flex="1" p={{ base: 4, md: 8 }}>
          <Box bg="white" p={8} rounded="2xl" shadow="xl">
            <VStack spacing={6} align="stretch">
              <Heading size="xl" color="teal.500">
                📈 Stock Price Forecast
              </Heading>

              <Box p={4} bg="gray.50" borderRadius="xl">
                <TickerSearch onSelect={fetchPredictions} />
              </Box>

              {loading && (
                <Flex justify="center" align="center" minH="100px">
                  <Spinner size="lg" color="teal.500" />
                </Flex>
              )}

              {error && (
                <Text color="red.500" fontWeight="medium">
                  ❌ {error}
                </Text>
              )}

              {predictions.length > 0 ? (
                <Dashboard predictions={predictions} metrics={metrics} ticker={selectedTicker} />
              ) : (
                <Text color="gray.500" textAlign="center" mt={4}>
                  Enter a ticker to see predictions.
                </Text>
              )}
            </VStack>
          </Box>
        </Box>
      </Flex>
    </Flex>
  );
}

export default App;
