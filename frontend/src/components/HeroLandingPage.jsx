import React from "react";
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  useColorModeValue,
  Stack,
} from "@chakra-ui/react";
import { motion } from "framer-motion";
import Features from "./Features";

// Motion-wrapped VStack
const MotionVStack = motion(VStack);
const MotionButton = motion(Button);

export default function HeroLandingPage({ onCTAClick }) {
  const bg = useColorModeValue("gray.50", "gray.900");
  const titleColor = useColorModeValue("teal.600", "teal.300");

  return (
    <Box
      as="section"
      w="100%"
      minH="100vh"
      bgGradient="linear(to-br, teal.100, white)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      px={{ base: 4, md: 8 }}
      py={{ base: 10, md: 20 }}
      flexDirection="column"
      overflowX="hidden"
    >
      <MotionVStack
        spacing={6}
        maxW={{ base: "full", sm: "xl", md: "2xl" }}
        textAlign="center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <Heading
          as="h1"
          fontSize={{ base: "3xl", sm: "4xl", md: "5xl" }}
          color={titleColor}
          lineHeight="short"
        >
          AI-Powered Stock Forecasting
        </Heading>

        <Text fontSize={{ base: "md", sm: "lg" }} color="gray.600">
          Get future stock insights with cutting-edge ML models. Forecast returns,
          compare models, and explore trends in real time.
        </Text>

        <MotionButton
          size="lg"
          colorScheme="teal"
          onClick={onCTAClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Start Forecasting
        </MotionButton>
      </MotionVStack>

      <Box mt={{ base: 10, md: 16 }} w="100%" maxW="6xl" px={{ base: 4, md: 8 }}>
        <Features />
      </Box>
    </Box>
  );
}