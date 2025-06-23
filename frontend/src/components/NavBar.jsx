import { Box, Flex, Text } from "@chakra-ui/react";

export default function Navbar() {
  return (
    <Box bg="white" px={6} py={4} boxShadow="sm">
      <Text fontSize="2xl" fontWeight="bold" fontFamily="system-ui">Stock Analyzer</Text>
    </Box>
  );
}
