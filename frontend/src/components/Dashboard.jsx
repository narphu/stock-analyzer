import { useEffect, useState } from "react";
import {
  Grid,
  Box,
  Text,
  SimpleGrid,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  useColorModeValue,
} from "@chakra-ui/react";
import axios from "axios";

export default function Dashboard({ predictions, ticker }) {
  const [metrics, setMetrics] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const cardBg = useColorModeValue("white", "gray.800");
  const tableBg = useColorModeValue("gray.50", "gray.700");
  const tableHeader = useColorModeValue("gray.100", "gray.600");
  const highlight = useColorModeValue("teal.500", "teal.300");

  useEffect(() => {
    if (!ticker) return;

    setLoadingMetrics(true);
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/metrics?ticker=${ticker}`)
      .then((res) => setMetrics(res.data))
      .catch(() => setMetrics(null))
      .finally(() => setLoadingMetrics(false));
  }, [ticker]);

  return (
    <Box>
      <Text fontSize="2xl" fontWeight="bold" color={highlight} mb={6}>
        📊 {ticker} Forecast
      </Text>

      <SimpleGrid columns={{ base: 1, sm: 2, md: 2, lg: 4 }} spacing={6}>
        {predictions.map((item) => (
          <Box
            key={item.days}
            bg={cardBg}
            p={6}
            rounded="2xl"
            shadow="md"
            textAlign="center"
            border="1px solid"
            borderColor={useColorModeValue("gray.100", "gray.700")}
            _hover={{ transform: "scale(1.02)", transition: "0.2s" }}
          >
            <Text fontSize="sm" color="gray.500">
              {item.date}
            </Text>
            <Text fontSize="3xl" fontWeight="bold" color={highlight}>
              ${item.price}
            </Text>
            <Text fontSize="md" mt={2}>
              {item.days}-day prediction
            </Text>
          </Box>
        ))}
      </SimpleGrid>

      <Box mt={10}>
        <Text fontSize="2xl" fontWeight="bold" mb={4} color={highlight}>
          🧾 Key Metrics
        </Text>

        {loadingMetrics ? (
          <Spinner />
        ) : metrics ? (
          <Box
            overflowX="auto"
            borderRadius="lg"
            bg={tableBg}
            p={4}
            shadow="sm"
          >
            <Table variant="simple" size="sm">
              <Thead bg={tableHeader}>
                <Tr>
                  <Th fontSize="sm" color="gray.600">
                    Metric
                  </Th>
                  <Th isNumeric fontSize="sm" color="gray.600">
                    Value
                  </Th>
                </Tr>
              </Thead>
              <Tbody>
                {Object.entries(metrics).map(([key, value]) => (
                  <Tr key={key}>
                    <Td fontWeight="medium">
                      {key
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (l) => l.toUpperCase())}
                    </Td>
                    <Td isNumeric>{value}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        ) : (
          <Text color="gray.500">No metrics available.</Text>
        )}
      </Box>
    </Box>
  );
}
