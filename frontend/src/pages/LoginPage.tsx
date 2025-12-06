/**
 * Login page with Cognito Hosted UI integration
 * 
 * Displays COPPA warning and login options.
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Typography,
  Alert,
  Stack,
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/profiles', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        py={4}
      >
        <Card sx={{ width: '100%', maxWidth: 500 }}>
          <CardContent>
            <Stack spacing={3}>
              {/* App Title */}
              <Box textAlign="center">
                <Typography variant="h4" component="h1" gutterBottom>
                  Popcorn Sales Manager
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Manage your fundraising sales with ease
                </Typography>
              </Box>

              {/* COPPA Warning */}
              <Alert severity="warning" sx={{ textAlign: 'left' }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Age Requirement (COPPA Compliance)
                </Typography>
                <Typography variant="body2">
                  You must be at least 13 years old to create an account and use this service.
                  By signing in, you confirm that you meet this age requirement.
                </Typography>
              </Alert>

              {/* Privacy Notice */}
              <Alert severity="info" sx={{ textAlign: 'left' }}>
                <Typography variant="body2">
                  This application is designed for parents and guardians to manage their Scout's
                  fundraising activities. We do not collect personal information from children
                  under 13.
                </Typography>
              </Alert>

              {/* Login Button */}
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<GoogleIcon />}
                onClick={handleLogin}
                sx={{ py: 1.5 }}
              >
                Sign in with Google
              </Button>

              {/* Additional Login Options Info */}
              <Typography variant="caption" color="text.secondary" textAlign="center">
                After signing in, additional social login options (Facebook, Apple) will be available
                through your Cognito user pool settings.
              </Typography>

              {/* Terms Notice */}
              <Typography variant="caption" color="text.secondary" textAlign="center">
                By signing in, you agree to our Terms of Service and Privacy Policy.
                This is a volunteer-run service provided as-is for Scouting America fundraising activities.
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};
