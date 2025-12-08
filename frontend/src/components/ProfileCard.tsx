/**
 * ProfileCard component - Display a single seller profile
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Stack,
  Box,
} from "@mui/material";
import {
  Person as PersonIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
} from "@mui/icons-material";

interface ProfileCardProps {
  profileId: string;
  sellerName: string;
  isOwner: boolean;
  permissions: string[];
  onEdit?: () => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({
  profileId,
  sellerName,
  isOwner,
  permissions,
  onEdit,
}) => {
  const navigate = useNavigate();

  const handleViewSeasons = () => {
    navigate(`/profiles/${encodeURIComponent(profileId)}/seasons`);
  };

  const canEdit = isOwner || permissions.includes("WRITE");

  return (
    <Card elevation={2}>
      <CardContent>
        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <PersonIcon color="primary" fontSize="large" />
          <Box flexGrow={1}>
            <Typography variant="h6" component="h3">
              {sellerName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Profile ID: {profileId.substring(0, 8)}...
            </Typography>
          </Box>
          {isOwner && <Chip label="Owner" color="primary" size="small" />}
          {!isOwner && permissions.includes("WRITE") && (
            <Chip label="Editor" color="secondary" size="small" />
          )}
          {!isOwner && !permissions.includes("WRITE") && (
            <Chip label="Viewer" color="default" size="small" />
          )}
        </Stack>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          variant="outlined"
          startIcon={<ViewIcon />}
          onClick={handleViewSeasons}
        >
          View Seasons
        </Button>
        {canEdit && onEdit && (
          <Button
            size="small"
            variant="text"
            startIcon={<EditIcon />}
            onClick={onEdit}
          >
            Edit Name
          </Button>
        )}
      </CardActions>
    </Card>
  );
};
