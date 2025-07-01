import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  VStack,
  Heading,
  Flex,
  Select,
  SimpleGrid,
  Badge,
  Text,
  Spinner,
  useColorModeValue,
} from "@chakra-ui/react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";

const MotionBox = motion(Box);
const MotionHeading = motion(Heading);

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

export default function Explore() {
  const [days, setDays] = useState(30);
  const [gainers, setGainers] = useState([]);
  const [losers, setLosers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const bg = useColorModeValue("whiteAlpha.800", "blackAlpha.600");
  const cardBg = useColorModeValue("white", "gray.700");
  const headingColor = useColorModeValue("teal.600", "teal.300");

  const navigate = useNavigate();

  const fetchExplore = async () => {
    setLoading(true);
    setError("");
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const params = new URLSearchParams({ days });
      const [gainRes, loseRes] = await Promise.all([
        axios.get(`${baseUrl}/explore/top-gainers?${params}`),
        axios.get(`${baseUrl}/explore/top-losers?${params}`),
      ]);

      setGainers(gainRes.data || []);
      setLosers(loseRes.data || []);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load explore data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExplore();
  }, [days]);

  const renderCard = (item, isGainer = true) => (
    <MotionBox
      key={item.ticker}
      bg={cardBg}
      p={4}
      rounded="xl"
      shadow="md"
      variants={cardVariants}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.2 }}
      cursor="pointer"
      onClick={() => navigate(`/Dashboard.jsx`)}
    >
      <Flex justify="space-between" align="center" mb={1}>
        <Text fontSize="lg" fontWeight="bold">
          {item.ticker}
        </Text>
        <Badge colorScheme={isGainer ? "green" : "red"}>
          {item.percent_change > 0 ? "+" : ""}
          {item.percent_change}%
        </Badge>
      </Flex>
      <Text fontSize="sm" color="gray.500">
        Now: ${item.current_price} → ${item.predicted_price}
      </Text>
    </MotionBox>
  );

  return (
    <Box position="relative" overflow="hidden">
      {/* Background Gradient */}
      <Box
        position="absolute"
        top={0}
        left={0}
        width="100%"
        height="40vh"
        bgGradient="linear(to-br, teal.100, purple.100)"
        filter="blur(80px)"
        zIndex={-1}
      />

      <VStack spacing={6} align="stretch" p={6}>
        <AnimatePresence>
          <MotionHeading
            size="lg"
            color={headingColor}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0, transition: { duration: 0.6 } }}
          >
            Explore Top Forecasts
          </MotionHeading>
        </AnimatePresence>

        {loading ? (
          <Flex justify="center" py={10}>
            <Spinner size="lg" color="teal.500" />
          </Flex>
        ) : error ? (
          <Text color="red.500" textAlign="center">
            {error}
          </Text>
        ) : (
          <Box
            as={motion.div}
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Gainers Section */}
            <Box my={8}>
              <Heading size="md" mb={4} color="green.500">
                📈 Top Gainers
              </Heading>
              <SimpleGrid columns={{ base: 1, sm: 2, md: 2, lg: 3 }} spacing={6}>
                {gainers.map((item) => renderCard(item, true))}
              </SimpleGrid>
            </Box>

            {/* Losers Section */}
            <Box my={8}>
              <Heading size="md" mb={4} color="red.500">
                📉 Top Losers
              </Heading>
              <SimpleGrid columns={{ base: 1, sm: 2, md: 2, lg: 3 }} spacing={6}>
                {losers.map((item) => renderCard(item, false))}
              </SimpleGrid>
            </Box>
          </Box>
        )}
      </VStack>
    </Box>
  );
}