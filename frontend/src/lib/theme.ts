import { createTheme } from '@mui/material/styles';

// Branding colors
const primary = '#1976d2';
const secondary = '#dc004e';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: primary },
    secondary: { main: secondary },
    background: { default: '#f5f5f5' },
    text: { primary: '#333333' },
  },
  typography: {
    fontFamily: [
      '"Open Sans"',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontFamily: '"Satisfy", "Open Sans", cursive',
      fontWeight: 600,
      letterSpacing: '0.08em',
      fontSize: '2rem',
      // Larger on medium and up
      '@media (min-width: 900px)': {
        fontSize: '3rem',
      },
    },
    h2: { fontFamily: '"Open Sans", sans-serif', fontWeight: 700 },
    h3: { fontFamily: '"Open Sans", sans-serif', fontWeight: 700 },
  },
});
