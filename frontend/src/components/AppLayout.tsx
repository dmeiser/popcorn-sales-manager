import React from 'react';
import { AppBar, Box, Toolbar, Typography, IconButton, Button, Drawer, List, ListItemText, ListItemButton, Container } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../contexts/AuthContext';
import { Toast } from './Toast';
import { Outlet } from 'react-router-dom';

export const AppLayout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const { account, logout } = useAuth();
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const toggleDrawer = () => setDrawerOpen(!drawerOpen);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      <AppBar position="static" color="primary" sx={{ mb: 2 }}>
        <Toolbar disableGutters>
          <Container maxWidth="lg" sx={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
            {/* Left controls */}
            <Box sx={{ display: 'flex', alignItems: 'center', width: 64 }}>
              <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer}>
                <MenuIcon />
              </IconButton>
            </Box>

            {/* Center title - absolutely centered within container */}
            <Box sx={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', pointerEvents: 'none' }}>
              <Typography
                variant="h6"
                component="div"
                sx={{ fontFamily: 'Satisfy, Open Sans, cursive', fontWeight: 600, letterSpacing: '0.06em' }}
              >
                🍿 Popcorn Sales Manager
              </Typography>
            </Box>

            {/* Right controls */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', flex: 1 }}>
              {account && (
                <Typography variant="body2" sx={{ mr: 2 }}>{account.displayName}</Typography>
              )}
              <Button color="inherit" onClick={logout}>Log out</Button>
            </Box>
          </Container>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer}>
        <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer}>
          <List>
              <ListItemButton>
                <ListItemText primary="Profiles" />
              </ListItemButton>
              <ListItemButton>
                <ListItemText primary="Seasons" />
              </ListItemButton>
              <ListItemButton>
                <ListItemText primary="Reports" />
              </ListItemButton>
              <ListItemButton>
                <ListItemText primary="Catalogs" />
              </ListItemButton>
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Container maxWidth="lg">
          {children}
          {/* Support both nested routes or direct children usage */}
          <Outlet />
        </Container>
      </Box>

      <Toast />
    </Box>
  );
};
