import { useRef, useState } from "react";
import axios from "axios";
import {
  Box,
  Flex,
  Heading,
  Spinner,
  Text,
  useColorModeValue,
  VStack,
  Select,
} from "@chakra-ui/react";
import { motion } from "framer-motion";
import TickerSearch from "./components/TickerSearch";
import Dashboard from "./components/Dashboard";
import Navbar from "./components/NavBar";
import Sidebar from "./components/SideBar";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [accuracy, setAccuracy] = useState("")
  const [selectedTicker, setSelectedTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedModel, setSelectedModel] = useState("prophet");
  const dashboardRef = useRef(null);

  const modelOptions = ["prophet", "arima", "xgboost", "lstm"];

  const fetchPredictions = async (ticker) => {
    setLoading(true);
    setError("");
    setPredictions([]);
    setMetrics([]);
    setSelectedTicker(ticker);
    setAccuracy();
    

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/predict`, {
        ticker,
        model: selectedModel,
      });
      setPredictions(res.data.predictions);
      setAccuracy(res.data.accuracy);

      const metricsRes = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/metrics?ticker=${ticker}`
      );
      setMetrics(metricsRes.data);

      setTimeout(() => {
        dashboardRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex direction="column" minH="100vh" position="relative" fontFamily="Inter, sans-serif">
      <Navbar />

      {/* 💫 Gradient Animated Background */}
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        h="400px"
        zIndex={-1}
        bgGradient="linear(to-br, teal.100, teal.300, blue.100)"
        opacity={0.3}
        filter="blur(80px)"
        rounded="full"
      />

      <Flex flex="1">
        <Sidebar />

        {/* 💡 Animated main card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{ flex: 1 }}
        >
          <Box p={{ base: 4, md: 8 }}>
            <Box bg="white" p={8} rounded="2xl" shadow="2xl">
              <VStack spacing={6} align="stretch">
                <Heading
                  size="2xl"
                  textAlign="center"
                  color="teal.600"
                  fontWeight="bold"
                  fontFamily="Inter, sans-serif"
                >
                  Stock Analyzer Dashboard
                </Heading>

                <Flex
                  direction={{ base: "column", md: "row" }}
                  justify="space-between"
                  align="center"
                  gap={4}
                  p={4}
                  bg="gray.50"
                  borderRadius="xl"
                >
                  <TickerSearch onSelect={fetchPredictions} />
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    maxW="200px"
                    placeholder="Select Model"
                    bg="white"
                    borderColor="gray.300"
                  >
                    {modelOptions.map((m) => (
                      <option key={m} value={m}>
                        {m.toUpperCase()}
                      </option>
                    ))}
                  </Select>
                </Flex>

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

                <Box ref={dashboardRef}>
                  {predictions.length > 0 ? (
                    <Dashboard
                      predictions={predictions}
                      metrics={metrics}
                      ticker={selectedTicker}
                      selectedModel={selectedModel}
                      accuracy={accuracy}
                    />
                  ) : (
                    <Text color="gray.500" textAlign="center" mt={4}>
                      Enter a ticker to see predictions.
                    </Text>
                  )}
                </Box>
              </VStack>
            </Box>
          </Box>
        </motion.div>
      </Flex>
    </Flex>
  );
}

export default App;
