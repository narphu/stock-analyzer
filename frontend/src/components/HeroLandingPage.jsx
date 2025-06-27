import React from "react";
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  useColorModeValue,
} from "@chakra-ui/react";
import { motion } from "framer-motion";

// Wrap Chakra’s VStack with motion to animate its children
const MotionVStack = motion(VStack);

export default function HeroLandingPage({ onCTAClick }) {
  // Color tokens that adapt to light/dark mode
  const bg = useColorModeValue("gray.50", "gray.900");
  const titleColor = useColorModeValue("teal.600", "teal.300");

  return (
    <Box
      as="section"
      w="100%"
      minH="70vh"
      bgGradient="linear(to-br, teal.50, white)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      px={6}
    >
      <MotionVStack
        spacing={6}
        maxW="lg"
        textAlign="center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <Heading as="h1" size="2xl" color={titleColor} lineHeight="short">
          AI-Powered Stock Forecasting
        </Heading>
        <Text fontSize="lg" color="gray.600">
          Get future stock insights with cutting-edge ML models. Forecast returns,
          compare models, and explore trends in real time.
        </Text>
        <Button
          size="lg"
          colorScheme="teal"
          onClick={onCTAClick}
          whilehover={{ scale: 1.05 }}
          whiletap={{ scale: 0.95 }}
        >
          Start Forecasting
        </Button>
      </MotionVStack>
    </Box>
  );
}
