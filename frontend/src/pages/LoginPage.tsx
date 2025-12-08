/**
 * Login page - Redirects to Cognito Hosted UI
 *
 * This page automatically redirects unauthenticated users to Cognito Hosted UI.
 * Cognito handles all authentication (social login + email/password signup).
 */

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Box, CircularProgress, Typography } from "@mui/material";
import { useAuth } from "../contexts/AuthContext";

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      // Already logged in, redirect to profiles
      navigate("/profiles", { replace: true });
    } else {
      // Not logged in, redirect to Cognito Hosted UI
      login().catch((error) => {
        console.error("Failed to redirect to login:", error);
      });
    }
  }, [isAuthenticated, navigate, login]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      gap={2}
    >
      <CircularProgress size={48} />
      <Typography variant="body1" color="text.secondary">
        Redirecting to login...
      </Typography>
    </Box>
  );
};
