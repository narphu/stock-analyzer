// src/theme.js
import { extendTheme } from "@chakra-ui/react";

export const theme = extendTheme({
  fonts: {
    heading: `"Inter", sans-serif`,
    body: `"Inter", sans-serif`,
  },
  colors: {
    brand: {
      50:  "#e3f9f7",
      100: "#c1eae8",
      200: "#9ddbd9",
      300: "#78ccc9",
      400: "#54bdba",
      500: "#3a9f9b",
      600: "#2e7d7b",
      700: "#225a5a",
      800: "#163838",
      900: "#091616",
    },
  },
  components: {
    Button: {
      defaultProps: { colorScheme: "brand" },
      baseStyle: { rounded: "2xl" },
    },
  },
});

export default theme