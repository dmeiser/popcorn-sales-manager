/**
 * Reusable navigation breadcrumb component.
 *
 * Provides a consistent breadcrumb trail for page navigation
 * across the application.
 */

import React from 'react';
import { Breadcrumbs as MuiBreadcrumbs, Link, Typography } from '@mui/material';
import type { SxProps, Theme } from '@mui/material';

/**
 * A single breadcrumb item in the navigation trail.
 */
export interface BreadcrumbItem {
  /** Display label for the breadcrumb */
  label: string;
  /** Click handler for navigation (if undefined, renders as text) */
  onClick?: () => void;
}

/**
 * Props for the NavBreadcrumbs component.
 */
export interface NavBreadcrumbsProps {
  /** Array of breadcrumb items to display */
  items: BreadcrumbItem[];
  /** Additional MUI sx styles */
  sx?: SxProps<Theme>;
  /** Typography variant for links (default: 'body1') */
  variant?: 'body1' | 'body2';
}

/**
 * Navigation breadcrumb component.
 *
 * Renders a trail of navigation breadcrumbs. Items with onClick handlers
 * are rendered as clickable links; items without are rendered as plain text.
 *
 * @example
 * ```tsx
 * <NavBreadcrumbs
 *   items={[
 *     { label: 'Scouts', onClick: () => navigate('/scouts') },
 *     { label: 'John Doe', onClick: () => navigate('/scouts/123/campaigns') },
 *     { label: 'Fall 2025' }, // Current page - no onClick
 *   ]}
 * />
 * ```
 */
export const NavBreadcrumbs: React.FC<NavBreadcrumbsProps> = ({ items, sx, variant = 'body1' }) => {
  return (
    <MuiBreadcrumbs sx={{ mb: 2, ...sx }}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        const isClickable = item.onClick !== undefined;

        // Last item or no onClick - render as text
        if (isLast || !isClickable) {
          return (
            <Typography key={index} variant={variant} color={isLast ? 'text.primary' : 'text.secondary'}>
              {item.label}
            </Typography>
          );
        }

        // Clickable link
        return (
          <Link
            key={index}
            component="button"
            variant={variant}
            onClick={item.onClick}
            sx={{ textDecoration: 'none', cursor: 'pointer' }}
          >
            {item.label}
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
};

export default NavBreadcrumbs;
