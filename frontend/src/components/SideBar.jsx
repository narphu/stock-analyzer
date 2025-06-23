import { Box, VStack, Text } from "@chakra-ui/react";

export default function Sidebar() {
  return (
    <Box w="250px" bg="white" p={6} boxShadow="md">
      <VStack align="start" spacing={4}>
        <Text fontWeight="bold">Dashboard</Text>
        <Text color="gray.600">Watchlist</Text>
        <Text color="gray.600">Settings</Text>
        {/* Add more dummy menu items */}
      </VStack>
    </Box>
  );
}

