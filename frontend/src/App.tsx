/**
 * Main App component
 * 
 * Sets up routing, authentication, Apollo Client, and theme.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { ApolloProvider } from '@apollo/client/react';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { ProfilesPage } from './pages/ProfilesPage';
import { apolloClient } from './lib/apollo';
import { theme } from './lib/theme';
import { AppLayout } from './components/AppLayout';


function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ApolloProvider client={apolloClient}>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected routes */}
              <Route
                path="/profiles"
                element={
                  <ProtectedRoute>
                    <AppLayout>
                      <ProfilesPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/profiles" replace />} />
              
              {/* 404 catch-all */}
              <Route path="*" element={<Navigate to="/profiles" replace />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ApolloProvider>
    </ThemeProvider>
  );
}

export default App;
