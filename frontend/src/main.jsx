// src/main.jsx
import App from "./App";
import theme from "./theme";
import './index.css';
import ReactDOM from "react-dom/client";

import { ChakraProvider } from "@chakra-ui/react";

ReactDOM.createRoot(document.getElementById("root")).render(
  <ChakraProvider theme={theme}>
    <App />
  </ChakraProvider>
);
