/**
 * SeasonSettingsPage - Season metadata and sharing settings
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client/react';
import {
  Box,
  Typography,
  Paper,
  Stack,
  TextField,
  Button,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import {
  GET_SEASON,
  UPDATE_SEASON,
  DELETE_SEASON,
  CREATE_PROFILE_INVITE,
} from '../lib/graphql';

interface Season {
  seasonId: string;
  seasonName: string;
  startDate: string;
  endDate?: string;
  catalogId: string;
  profileId: string;
}

export const SeasonSettingsPage: React.FC = () => {
  const { profileId: encodedProfileId, seasonId: encodedSeasonId } = useParams<{ profileId: string; seasonId: string }>();
  const profileId = encodedProfileId ? decodeURIComponent(encodedProfileId) : '';
  const seasonId = encodedSeasonId ? decodeURIComponent(encodedSeasonId) : '';
  const navigate = useNavigate();
  const [seasonName, setSeasonName] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [inviteCode, setInviteCode] = useState<string | null>(null);

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
      setStartDate(seasonData.getSeason.startDate?.split('T')[0] || '');
      setEndDate(seasonData.getSeason.endDate?.split('T')[0] || '');
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
      navigate(`/profiles/${encodeURIComponent(profileId || '')}/seasons`);
    },
  });

  // Create profile invite
  const [createInvite, { loading: creatingInvite }] = useMutation<{
    createProfileInvite: { inviteCode: string };
  }>(CREATE_PROFILE_INVITE, {
    onCompleted: (data) => {
      setInviteCode(data.createProfileInvite.inviteCode);
    },
  });

  const season = seasonData?.getSeason;

  const handleSaveChanges = async () => {
    if (!seasonId || !seasonName.trim()) return;
    
    // Convert YYYY-MM-DD to ISO 8601 datetime
    const startDateTime = new Date(startDate + 'T00:00:00.000Z').toISOString();
    const endDateTime = endDate ? new Date(endDate + 'T23:59:59.999Z').toISOString() : null;
    
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

  const handleCreateInvite = async () => {
    if (!profileId) return;
    await createInvite({
      variables: {
        profileId,
        permissions: ['READ', 'WRITE'],
      },
    });
  };

  const handleCopyInviteCode = () => {
    if (inviteCode) {
      navigator.clipboard.writeText(inviteCode);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  const hasChanges =
    season &&
    season.seasonName &&
    season.startDate &&
    (seasonName !== season.seasonName ||
      startDate !== season.startDate.split('T')[0] ||
      endDate !== (season.endDate?.split('T')[0] || ''));

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Season Settings
      </Typography>

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
            {updating ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </Paper>

      {/* Profile Sharing */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Profile Sharing
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Share this seller profile with others. They will be able to view and edit all seasons
          for this profile.
        </Typography>
        <Button
          variant="outlined"
          startIcon={creatingInvite ? <CircularProgress size={20} /> : <ShareIcon />}
          onClick={handleCreateInvite}
          disabled={creatingInvite}
        >
          Generate Invite Code
        </Button>
        {inviteCode && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="body2">
                Invite Code: <strong>{inviteCode}</strong>
              </Typography>
              <IconButton size="small" onClick={handleCopyInviteCode}>
                <CopyIcon fontSize="small" />
              </IconButton>
            </Stack>
            <Typography variant="caption" display="block" mt={1}>
              Share this code with others. It expires in 14 days and can only be used once.
            </Typography>
          </Alert>
        )}
      </Paper>

      {/* Danger Zone */}
      <Paper sx={{ p: 3, borderColor: 'error.main', borderWidth: 1, borderStyle: 'solid' }}>
        <Typography variant="h6" gutterBottom color="error">
          Danger Zone
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Deleting this season will permanently remove all orders and data. This action cannot be
          undone.
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Delete Season?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{season?.seasonName}"? All orders and data will be
            permanently deleted. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteSeason} color="error" variant="contained">
            Delete Permanently
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
