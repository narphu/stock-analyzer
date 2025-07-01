import React from "react";
import { Box, Heading, Text, VStack, useColorModeValue } from "@chakra-ui/react";

export default function About() {
  const headingColor = useColorModeValue("teal.600", "teal.300");
  const textColor = useColorModeValue("gray.700", "gray.300");

  return (
    <Box px={{ base: 4, md: 10 }} py={10} maxW="6xl" mx="auto">
      <VStack spacing={6} align="start">
        <Heading size="xl" color={headingColor}>About Stock Analyzer</Heading>

        <Text fontSize="md" color={textColor}>
          Stock Analyzer is an AI-powered web application that forecasts future stock prices using a combination of machine learning models. It provides detailed projections, sector-based analysis, and performance comparisons to help users gain actionable investment insights.
        </Text>

        <Heading size="lg" color={headingColor}>How Forecasting Works</Heading>
        <Text fontSize="md" color={textColor}>
          The system pre-trains and stores models for each S&P 500 stock. When a user selects a ticker, the backend loads the relevant model and generates predictions for time horizons like 1, 2, 7, 10, and 30 days. The forecasts are based on historical price data and enriched features.
        </Text>

        <Heading size="lg" color={headingColor}>Explore Page</Heading>
        <Text fontSize="md" color={textColor}>
          On the Explore page, we surface top gainers and losers over a user-selected period (e.g., 30 days). These insights are calculated by averaging predictions from all four models per stock and computing the expected percent change. We rank the results to identify top performers (gainers) and underperformers (losers).
        </Text>

        <Heading size="lg" color={headingColor}>Why Four Models?</Heading>
        <Text fontSize="md" color={textColor}>
          We use four distinct models to improve robustness:
        </Text>
        <Text fontSize="md" color={textColor}>
          • <strong>Prophet</strong>: Developed by Meta, good for capturing trend + seasonality in time series.<br/>
          • <strong>ARIMA</strong>: Classic statistical model suitable for linear trends.<br/>
          • <strong>XGBoost</strong>: Gradient boosted trees that work well on engineered features.<br/>
          • <strong>LSTM</strong>: A deep learning model designed for sequential data like stock prices.
        </Text>
        <Text fontSize="md" color={textColor}>
          This ensemble approach ensures better accuracy across different stock behaviors and market regimes.
        </Text>

        <Heading size="lg" color={headingColor}>Tech Stack</Heading>
        <Text fontSize="md" color={textColor}>
          • <strong>Frontend</strong>: React with Vite, Chakra UI for responsive design, Framer Motion for animations.<br/>
          • <strong>Backend</strong>: FastAPI for APIs, TorchServe for model serving, AWS S3 for storage.<br/>
          • <strong>ML</strong>: Models trained using Prophet, ARIMA (statsmodels), XGBoost, LSTM (PyTorch) — orchestrated with SageMaker and stored in S3.<br/>
          • <strong>Infrastructure</strong>: Deployed using AWS ECS with ALB, Route53, and CloudFront.
        </Text>
      </VStack>
    </Box>
  );
}