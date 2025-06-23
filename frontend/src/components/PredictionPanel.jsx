// src/components/PredictionPanel.jsx
import { Box, SimpleGrid, Text, Stat, StatLabel, StatNumber, VStack } from "@chakra-ui/react";

export default function PredictionPanel({ predictions }) {
  const daysToShow = [1, 2, 7, 10, 30];

  return (
    <VStack spacing={6} align="stretch" w="full">
      <Text fontSize="xl" fontWeight="bold" color="gray.700">
        Price Forecast
      </Text>
      <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={4}>
        {predictions
          .filter((p) => daysToShow.includes(p.days))
          .map((p) => (
            <Stat
              key={p.days}
              p={4}
              borderRadius="xl"
              bg="blue.50"
              boxShadow="md"
              border="1px solid"
              borderColor="blue.100"
            >
              <StatLabel fontSize="sm" color="gray.600">
                {p.days} Day{p.days > 1 ? "s" : ""} Ahead ({p.date})
              </StatLabel>
              <StatNumber fontSize="2xl" color="blue.600">
                ${p.price.toFixed(2)}
              </StatNumber>
            </Stat>
          ))}
      </SimpleGrid>
    </VStack>
  );
}