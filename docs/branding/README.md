# Cognito Hosted UI Branding Assets

This folder contains branding assets used for the Cognito Hosted UI (login page).

## Files

### Logos & Banners
- `popcorn-banner.png` - Main logo displayed on the login page (PNG, optimized)
- `popcorn-banner.svg` - Vector version of the banner (SVG source)
- `popcorn-logo.png` - Alternate logo version (PNG)
- `popcorn-logo.svg` - Vector version of the logo (SVG source)

### Favicons
- `favicon.ico` - Standard favicon (32x32)
- `favicon-large.ico` - Large favicon for high-DPI displays
- `favicon.png` - PNG version of favicon
- `favicon.svg` - Vector version of favicon

### Background
- `page-background.svg` - Solid color background for the login page

### Configuration
- `managed-login-settings.json` - Cognito Managed Login configuration (colors, fonts, COPPA warning)

## Deployment

These assets are deployed to Cognito via the `cdk/deploy-cognito-branding.sh` script.

```bash
cd cdk
./deploy-cognito-branding.sh
```

## Design Specifications

- **Primary Color**: #1976d2 (Material Blue)
- **Font (Headings)**: Satisfy (Google Fonts)
- **Font (Body)**: Open Sans (Google Fonts)
- **COPPA Compliance**: 13+ age requirement warning displayed

## Editing

To update branding:
1. Edit the source SVG files in this directory
2. Export optimized PNG versions if needed
3. Update `managed-login-settings.json` for color/font changes
4. Run `cdk/deploy-cognito-branding.sh` to deploy changes
