// src/App.jsx
import React, { useRef, useState } from "react";
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
  IconButton,
  useDisclosure,
  useBreakpointValue,
} from "@chakra-ui/react";
import { AnimatePresence, motion } from "framer-motion";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { FiMenu } from "react-icons/fi";

import HeroLandingPage from "./components/HeroLandingPage";
import Navbar from "./components/NavBar";
import Sidebar from "./components/SideBar";
import TickerSearch from "./components/TickerSearch";
import Dashboard from "./components/Dashboard";
import CompareModels from "./components/CompareModels";
import Explore from "./components/Explore";
import About from "./components/About";


function MainLayout() {
  const location = useLocation();
  const [heroVisible, setHeroVisible] = useState(true);
  const isHome = location.pathname === "/";

  const dashboardRef = useRef(null);
  const [predictions, setPredictions] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [accuracy, setAccuracy] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedModel, setSelectedModel] = useState("prophet");
  const modelOptions = ["prophet", "arima", "xgboost", "lstm"];

  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleCTAClick = () => {
    setHeroVisible(false);
    setTimeout(() => {
      dashboardRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 600);
  };

  const fetchPredictions = async (ticker) => {
    setLoading(true);
    setError("");
    setPredictions([]);
    setMetrics([]);
    setSelectedTicker(ticker);
    setAccuracy("");

    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/predict`,
        { ticker, model: selectedModel }
      );
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
    <Flex direction="column" minH="100vh" position="relative">
      {isHome && (
        <AnimatePresence>
          {heroVisible && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.6, ease: "easeInOut" }}
              style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: "100vw",
                height: "100vh",
                zIndex: 9999,
              }}
            >
              <HeroLandingPage onCTAClick={handleCTAClick} />
            </motion.div>
          )}
        </AnimatePresence>
      )}

      {!isHome || !heroVisible ? (
        <>
          <Navbar />
          {isMobile && (
            <IconButton
              icon={<FiMenu />}
              onClick={onOpen}
              aria-label="Open menu"
              m={4}
              position="fixed"
              top={4}
              left={4}
              zIndex={1000}
            />
          )}
        </>
      ) : null}

      <Flex flex="1">
        {!isHome || !heroVisible ? (
          isMobile && isOpen ? (
            <Sidebar isMobile onClose={onClose} />
          ) : (
            <Sidebar />
          )
        ) : null}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: heroVisible && isHome ? 0.6 : 0 }}
          style={{ flex: 1 }}
        >
          <Box p={{ base: 4, md: 8 }}>
            <Routes location={location} key={location.pathname}>
              <Route
                path="/"
                element={
                  <VStack spacing={6} align="stretch">
                    <Heading
                      size="2xl"
                      textAlign="center"
                      color="teal.600"
                      fontWeight="bold"
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
                }
              />
              <Route path="/compare" element={<CompareModels />} />
              <Route path="/explore" element={<Explore />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </Box>
        </motion.div>
      </Flex>
    </Flex>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );
}
