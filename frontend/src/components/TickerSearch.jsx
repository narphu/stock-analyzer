import { useState } from "react";
import {
  Box,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  List,
  ListItem,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import sp500 from "../data/sp500.json";

export default function TickerSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const [inputValue, setInputValue] = useState("");

  const filtered =
    query === ""
      ? []
      : sp500.filter((ticker) =>
          ticker.toLowerCase().includes(query.toLowerCase())
        );

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setInputValue(value);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && sp500.includes(inputValue.toUpperCase())) {
      handleSelect(inputValue.toUpperCase());
    }
  };

  const handleSelect = (value) => {
    onSelect(value);
    setInputValue(value);  // Update the input field
    setQuery("");          // Hide dropdown
  };

  const handleButtonClick = () => {
    if (sp500.includes(inputValue.toUpperCase())) {
      handleSelect(inputValue.toUpperCase());
    }
  };

  const bgColor = useColorModeValue("white", "gray.700");
  const borderColor = useColorModeValue("gray.300", "gray.600");

  return (
    <Box w="100%" maxW="md" mx="auto" mt={6}>
      <InputGroup size="lg" borderRadius="full">
        <Input
          placeholder="Search ticker (e.g. AAPL)..."
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          bg={bgColor}
          border="1px solid"
          borderColor={borderColor}
          borderRadius="full"
          pr="3rem"
          fontWeight="medium"
        />
        <InputRightElement width="3rem">
          <IconButton
            aria-label="Search"
            icon={<ArrowForwardIcon />}
            onClick={handleButtonClick}
            size="sm"
            colorScheme="teal"
            variant="ghost"
          />
        </InputRightElement>
      </InputGroup>

      {filtered.length > 0 && (
        <Box
          mt={2}
          border="1px solid"
          borderColor={borderColor}
          borderRadius="md"
          maxH="200px"
          overflowY="auto"
          bg={bgColor}
          shadow="md"
        >
          <List spacing={1}>
            {filtered.map((ticker) => (
              <ListItem
                key={ticker}
                px={4}
                py={2}
                _hover={{
                  bg: useColorModeValue("gray.100", "gray.600"),
                  cursor: "pointer",
                }}
                onClick={() => handleSelect(ticker)}
              >
                <Text fontWeight="medium">{ticker}</Text>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
}
