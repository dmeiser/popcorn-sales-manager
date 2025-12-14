/**
 * SeasonSettingsPage - Season-specific settings only
 *
 * Note: Profile-level settings (invites, shares, profile deletion) have been moved
 * to ProfileManagementPage to clarify that invites belong to profiles, not seasons.
 */

import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@apollo/client/react";
import {
  Box,
  Typography,
  Paper,
  Stack,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from "@mui/material";
import { Delete as DeleteIcon } from "@mui/icons-material";
import {
  GET_SEASON,
  UPDATE_SEASON,
  DELETE_SEASON,
} from "../lib/graphql";

interface Season {
  seasonId: string;
  seasonName: string;
  startDate: string;
  endDate?: string;
  catalogId: string;
  profileId: string;
}

export const SeasonSettingsPage: React.FC = () => {
  const { profileId: encodedProfileId, seasonId: encodedSeasonId } = useParams<{
    profileId: string;
    seasonId: string;
  }>();
  const profileId = encodedProfileId
    ? decodeURIComponent(encodedProfileId)
    : "";
  const seasonId = encodedSeasonId ? decodeURIComponent(encodedSeasonId) : "";
  const navigate = useNavigate();
  const [seasonName, setSeasonName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Fetch season
  const {
    data: seasonData,
    loading,
    refetch,
  } = useQuery<{ getSeason: Season }>(GET_SEASON, {
    variables: { seasonId },
    skip: !seasonId,
  });

  // Initialize form when season loads
  React.useEffect(() => {
    if (seasonData?.getSeason) {
      setSeasonName(seasonData.getSeason.seasonName);
      setStartDate(seasonData.getSeason.startDate?.split("T")[0] || "");
      setEndDate(seasonData.getSeason.endDate?.split("T")[0] || "");
    }
  }, [seasonData]);

  // Update season mutation
  const [updateSeason, { loading: updating }] = useMutation(UPDATE_SEASON, {
    onCompleted: () => {
      refetch();
    },
  });

  // Delete season mutation
  const [deleteSeason] = useMutation(DELETE_SEASON, {
    onCompleted: () => {
      navigate(`/profiles/${encodeURIComponent(profileId || "")}/seasons`);
    },
  });

  const season = seasonData?.getSeason;

  const handleSaveChanges = async () => {
    if (!seasonId || !seasonName.trim()) return;

    // Convert YYYY-MM-DD to ISO 8601 datetime
    const startDateTime = new Date(startDate + "T00:00:00.000Z").toISOString();
    const endDateTime = endDate
      ? new Date(endDate + "T23:59:59.999Z").toISOString()
      : null;

    await updateSeason({
      variables: {
        input: {
          seasonId,
          seasonName: seasonName.trim(),
          startDate: startDateTime,
          endDate: endDateTime,
        },
      },
    });
  };

  const handleDeleteSeason = async () => {
    if (!seasonId) return;
    await deleteSeason({ variables: { seasonId } });
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="200px"
      >
        <CircularProgress />
      </Box>
    );
  }

  const hasChanges =
    season &&
    season.seasonName &&
    season.startDate &&
    (seasonName !== season.seasonName ||
      startDate !== season.startDate.split("T")[0] ||
      endDate !== (season.endDate?.split("T")[0] || ""));

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h5">
          Season Settings
        </Typography>
        <Button
          variant="text"
          color="primary"
          onClick={() => navigate(`/profiles/${encodeURIComponent(profileId)}/manage`)}
        >
          Manage Seller Profile
        </Button>
      </Stack>

      {/* Basic Settings */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Basic Information
        </Typography>
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Season Name"
            value={seasonName}
            onChange={(e) => setSeasonName(e.target.value)}
            disabled={updating}
          />
          <TextField
            fullWidth
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            disabled={updating}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            label="End Date (Optional)"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            disabled={updating}
            InputLabelProps={{ shrink: true }}
          />
          <Button
            variant="contained"
            onClick={handleSaveChanges}
            disabled={!hasChanges || updating}
          >
            {updating ? "Saving..." : "Save Changes"}
          </Button>
        </Stack>
      </Paper>

      {/* Danger Zone */}
      <Paper
        sx={{
          p: 3,
          borderColor: "error.main",
          borderWidth: 1,
          borderStyle: "solid",
        }}
      >
        <Typography variant="h6" gutterBottom color="error">
          Danger Zone
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Deleting this season will permanently remove all orders and data. This
          action cannot be undone.
        </Typography>
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          onClick={() => setDeleteConfirmOpen(true)}
        >
          Delete Season
        </Button>
      </Paper>

      {/* Delete Season Confirmation Dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Delete Season?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{season?.seasonName}"? All orders
            and data will be permanently deleted. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteSeason}
            color="error"
            variant="contained"
          >
            Delete Permanently
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

