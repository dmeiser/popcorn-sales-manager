/**
 * Profiles page - List of owned and shared seller profiles
 * 
 * Placeholder for Phase 2 Step 4 (Pages & Components)
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';

export const ProfilesPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Profiles
        </Typography>
        <Typography variant="body1" color="text.secondary">
          This page will display your seller profiles (owned and shared).
          Implementation coming in Phase 2 Step 4.
        </Typography>
      </Box>
    </Container>
  );
};
