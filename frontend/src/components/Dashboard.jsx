import { Box, Text, SimpleGrid, Stat, StatLabel, StatNumber, useColorModeValue, Flex, Badge, Heading } from "@chakra-ui/react";
import { motion } from "framer-motion";
import { useMemo } from "react";

const MotionBox = motion(Box);

export default function Dashboard({ predictions, metrics, ticker, selectedModel, accuracy }) {
  const highlight = useColorModeValue("teal.600", "teal.300");
  const cardBg = useColorModeValue("white", "gray.800");
  const statBg = useColorModeValue("gray.50", "gray.700");
  const borderColor = useColorModeValue("gray.100", "gray.600");

  const accuracyValue = useMemo(() => {
    if (!accuracy) return null;
    return accuracy;
  }, [accuracy]);

  return (
    <Box mt={10}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="lg" color={highlight} fontFamily="Inter">
          {ticker} Forecast
        </Heading>

        {accuracyValue !== undefined && (
          <Badge fontSize="md" colorScheme="green" variant="subtle" px={3} py={1} borderRadius="md">
            Accuracy ({selectedModel.toUpperCase()}): {accuracyValue}
          </Badge>
        )}
      </Flex>

      <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing={6} mt={4}>
        {predictions.map((item) => (
          <MotionBox
            key={item.days}
            bg={cardBg}
            p={6}
            rounded="xl"
            shadow="md"
            border="1px solid"
            borderColor={borderColor}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <Text fontSize="sm" color="gray.500">
              {item.date}
            </Text>
            <Text fontSize="3xl" fontWeight="bold" color={highlight}>
              ${item.price}
            </Text>
            <Text fontSize="md" mt={2} color="gray.600">
              {item.days}-day prediction
            </Text>
          </MotionBox>
        ))}
      </SimpleGrid>

      <Box mt={10}>
        <Text fontSize="xl" fontWeight="semibold" mb={4} color={highlight} fontFamily="Inter">
          Key Stock Metrics
        </Text>

        {metrics ? (
          <SimpleGrid columns={{ base: 1, sm: 2, md: 3 }} spacing={6}>
            {Object.entries(metrics).map(([key, value]) => (
              <Stat
                key={key}
                p={4}
                rounded="xl"
                bg={statBg}
                shadow="sm"
                border="1px solid"
                borderColor={borderColor}
              >
                <StatLabel fontWeight="medium">
                  {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </StatLabel>
                <StatNumber fontSize="lg">
                  {typeof value === "number" ? value.toLocaleString() : value || "—"}
                </StatNumber>
              </Stat>
            ))}
          </SimpleGrid>
        ) : (
          <Text mt={4} color="gray.500">
            No metrics available for this ticker.
          </Text>
        )}
      </Box>
    </Box>
  );
}
