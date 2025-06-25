// components/SideBar.jsx
import {
  Box,
  VStack,
  Icon,
  Text,
  useColorModeValue,
  Flex
} from "@chakra-ui/react";
import { FiPieChart, FiSearch, FiSettings } from "react-icons/fi";

const SidebarItem = ({ icon, label }) => (
  <Flex
    align="center"
    px={4}
    py={3}
    w="full"
    cursor="pointer"
    rounded="lg"
    transition="all 0.2s"
    _hover={{ bg: useColorModeValue("blue.600", "gray.700"), color: "white" }}
  >
    <Icon as={icon} mr={3} boxSize={5} />
    <Text fontSize="md" fontWeight="medium">
      {label}
    </Text>
  </Flex>
);

export default function SideBar() {
  const bg = useColorModeValue("blue.900", "gray.900");
  const color = useColorModeValue("white", "white");

  return (
    <Box
      as="nav"
      w={{ base: "full", md: "240px" }}
      minH="100vh"
      bg={bg}
      color={color}
      px={3}
      py={6}
      shadow="md"
    >
      <VStack spacing={3} align="stretch">
        <SidebarItem icon={FiPieChart} label="Dashboard" />
        <SidebarItem icon={FiSearch} label="Explore" />
        <SidebarItem icon={FiSettings} label="Settings" />
      </VStack>
    </Box>
  );
}