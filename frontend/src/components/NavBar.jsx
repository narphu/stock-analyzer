// components/NavBar.jsx
import {
  Flex,
  Text,
  IconButton,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import { MoonIcon, SunIcon } from "@chakra-ui/icons";

export default function NavBar() {
  const { colorMode, toggleColorMode } = useColorMode();
  const bg = useColorModeValue("blue.800", "gray.900");
  const color = useColorModeValue("white", "white");

  return (
    <Flex
      as="header"
      align="center"
      justify="space-between"
      px={6}
      py={4}
      bg={bg}
      color={color}
      shadow="md"
    >
      <Text fontSize="xl" fontWeight="bold" fontFamily="Inter">
        Shrubb.ai Stock Analyzer
      </Text>
      <IconButton
        aria-label="Toggle color mode"
        icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
        onClick={toggleColorMode}
        variant="ghost"
        color={color}
        _hover={{ bg: useColorModeValue("blue.700", "gray.700") }}
      />
    </Flex>
  );
}

