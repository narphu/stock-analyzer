import React, { useState } from "react";
import axios from "axios";
import {
  Box,
  VStack,
  Heading,
  Button,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Text,
  Input,
  Select,
  Spinner,
  useColorModeValue,
} from "@chakra-ui/react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import TickerSearch from "./TickerSearch";

export default function CompareModels() {
  const [ticker, setTicker] = useState("");
  const [days, setDays] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bg = useColorModeValue("white", "gray.700");

  const handleCompare = async () => {
    if (!ticker) return;
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/compare/${ticker.toUpperCase()}?days=${days}`
      );
      // transform results into array
      const arr = Object.entries(res.data).map(([model, vals]) => ({
        model,
        ...vals,
      }));
      setData(arr);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to compare models.");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={{ base: 4, md: 8 }}>
      <VStack spacing={6} align="stretch">
        <Heading size="xl" textAlign="center" color="teal.500">
          Compare Models
        </Heading>

        <Box bg={bg} p={4} rounded="xl" shadow="md">
          <VStack spacing={4} align="stretch">
            <TickerSearch onSelect={setTicker} variant="fullWidth" />
            <Select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              maxW="120px"
            >
              {[1, 2, 7, 10, 30].map((d) => (
                <option key={d} value={d}>
                  {d}d
                </option>
              ))}
            </Select>
            <Button
              colorScheme="teal"
              onClick={handleCompare}
              isDisabled={!ticker || loading}
            >
              Compare
            </Button>
          </VStack>
        </Box>

        {loading && (
          <Spinner size="lg" color="teal.500" alignSelf="center" />
        )}

        {error && (
          <Text color="red.500" textAlign="center">
            {error}
          </Text>
        )}

        {data && (
          <>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              {data.map(({ model, next_prediction, accuracy, error }) => (
                <Box key={model} bg={bg} p={4} rounded="lg" shadow="sm">
                  {error ? (
                    <Text color="red.500">Error: {error}</Text>
                  ) : (
                    <>
                      <Stat>
                        <StatLabel textTransform="capitalize">
                          {model}
                        </StatLabel>
                        <StatNumber>${next_prediction}</StatNumber>
                        <Text fontSize="sm" color="gray.500">
                          Accuracy: {(accuracy * 100).toFixed(2)}%
                        </Text>
                      </Stat>
                    </>
                  )}
                </Box>
              ))}
            </SimpleGrid>

            <Box h="300px" mt={8} bg={bg} p={4} rounded="lg" shadow="sm">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 5 }}>
                  <XAxis dataKey="model" />
                  <YAxis domain={["dataMin", "dataMax"]} />
                  <Tooltip />
                  <Bar dataKey="next_prediction" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </>
        )}
      </VStack>
    </Box>
  );
}
