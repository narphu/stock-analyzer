import React from "react";
import {
  Box,
  VStack,
  Icon,
  Text,
  Flex,
  useColorModeValue,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useBreakpointValue,
  useDisclosure,
} from "@chakra-ui/react";
import { NavLink } from "react-router-dom";
import { FiPieChart, FiSearch, FiBarChart2, FiSettings, FiInfo } from "react-icons/fi";

const navItems = [
  { label: "Dashboard", icon: FiPieChart, to: "/" },
  { label: "Explore", icon: FiSearch, to: "/explore" },
  { label: "Compare", icon: FiBarChart2, to: "/compare" },
  { label: "Settings", icon: FiSettings, to: "/settings" },
  { label: "About", icon: FiInfo, to: "/about" },
];

export default function SideBar({ isMobile = false, isOpen = false, onClose = () => {} }) {
  const bg = useColorModeValue("blue.900", "gray.900");
  const color = useColorModeValue("white", "white");
  const activeBg = useColorModeValue("blue.700", "gray.700");

  const Content = (
    <VStack spacing={3} align="stretch">
      {navItems.map(({ label, icon, to }) => (
        <NavLink key={to} to={to} style={{ textDecoration: "none" }}>
          {({ isActive }) => (
            <Flex
              align="center"
              px={4}
              py={3}
              w="full"
              cursor="pointer"
              rounded="lg"
              transition="all 0.2s"
              bg={isActive ? activeBg : "transparent"}
              color={isActive ? "white" : color}
              _hover={{ bg: useColorModeValue("blue.600", "gray.700"), color: "white" }}
              onClick={isMobile ? onClose : undefined}
            >
              <Icon as={icon} mr={3} boxSize={5} />
              <Text fontSize="md" fontWeight="medium">
                {label}
              </Text>
            </Flex>
          )}
        </NavLink>
      ))}
    </VStack>
  );

  if (isMobile) {
    return (
      <Drawer placement="left" onClose={onClose} isOpen={isOpen}>
        <DrawerOverlay />
        <DrawerContent bg={bg} color={color}>
          <DrawerCloseButton />
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody>{Content}</DrawerBody>
        </DrawerContent>
      </Drawer>
    );
  }

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
      {Content}
    </Box>
  );
}
