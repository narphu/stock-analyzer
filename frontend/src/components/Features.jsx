// components/Features.jsx
import { SimpleGrid, Box, Heading, Text } from "@chakra-ui/react";
import { FaBolt, FaChartLine, FaShieldAlt } from "react-icons/fa";

const feats = [
  { icon: <FaBolt size={32} />, title: "Real-Time Forecasts", body: "Instant predictions for any ticker." },
  { icon: <FaChartLine size={32} />, title: "Multi-Model Support", body: "Prophet, ARIMA, XGBoost & more." },
  { icon: <FaShieldAlt size={32} />, title: "Secure & Scalable", body: "Enterprise-grade infrastructure." },
];

export default function Features() {
  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} px={8} py={16}>
      {feats.map((f) => (
        <Box key={f.title} textAlign="center" p={6} bg="white" rounded="xl" shadow="md" _hover={{ shadow: "lg" }} transition="0.2s">
          <Box mb={4} color="brand.500">{f.icon}</Box>
          <Heading size="md" mb={2}>{f.title}</Heading>
          <Text color="gray.600">{f.body}</Text>
        </Box>
      ))}
    </SimpleGrid>
  );
}
