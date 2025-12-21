/**
 * CampaignPrefillsPage - Manage campaign prefills (shareable season links)
 */

import React, { useState } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stack,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
} from "@mui/material";
import {
  Add as AddIcon,
  ContentCopy as CopyIcon,
  Edit as EditIcon,
  Block as DeactivateIcon,
  QrCode as QrCodeIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
} from "@mui/icons-material";
import QRCode from "qrcode";
import {
  LIST_MY_CAMPAIGN_PREFILLS,
  UPDATE_CAMPAIGN_PREFILL,
  DELETE_CAMPAIGN_PREFILL,
} from "../lib/graphql";
import { CreateCampaignPrefillDialog } from "../components/CreateCampaignPrefillDialog";
import { EditCampaignPrefillDialog } from "../components/EditCampaignPrefillDialog";

interface CampaignPrefill {
  prefillCode: string;
  catalogId: string;
  catalog?: {
    catalogId: string;
    catalogName: string;
  };
  seasonName: string;
  seasonYear: number;
  startDate?: string;
  endDate?: string;
  unitType: string;
  unitNumber: number;
  city: string;
  state: string;
  createdBy: string;
  createdByName: string;
  creatorMessage?: string;
  description?: string;
  isActive: boolean;
  createdAt: string;
}

const MAX_PREFILLS = 50;
const BASE_URL = window.location.origin;

export const CampaignPrefillsPage: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingPrefill, setEditingPrefill] = useState<CampaignPrefill | null>(
    null
  );
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false);
  const [prefillToDeactivate, setPrefillToDeactivate] =
    useState<CampaignPrefill | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");

  // Fetch user's campaign prefills
  const {
    data,
    loading,
    error,
    refetch,
  } = useQuery<{ listMyCampaignPrefills: CampaignPrefill[] }>(
    LIST_MY_CAMPAIGN_PREFILLS
  );

  // Update mutation (for editing)
  const [updatePrefill] = useMutation(UPDATE_CAMPAIGN_PREFILL, {
    onCompleted: () => {
      refetch();
      setEditingPrefill(null);
      showSnackbar("Campaign prefill updated successfully");
    },
  });

  // Delete mutation (soft delete / deactivate)
  const [deletePrefill] = useMutation(DELETE_CAMPAIGN_PREFILL, {
    onCompleted: () => {
      refetch();
      setDeactivateDialogOpen(false);
      setPrefillToDeactivate(null);
      showSnackbar("Campaign prefill deactivated");
    },
  });

  const prefills = data?.listMyCampaignPrefills || [];
  const activePrefillCount = prefills.filter((p) => p.isActive).length;
  const canCreateMore = activePrefillCount < MAX_PREFILLS;

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  const getShortLink = (prefillCode: string) => {
    return `${BASE_URL}/c/${prefillCode}`;
  };

  const handleCopyLink = async (prefillCode: string) => {
    const link = getShortLink(prefillCode);
    try {
      await navigator.clipboard.writeText(link);
      showSnackbar("Link copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy link:", err);
      showSnackbar("Failed to copy link");
    }
  };

  const handleDownloadQRCode = async (prefill: CampaignPrefill) => {
    const link = getShortLink(prefill.prefillCode);
    try {
      const qrDataUrl = await QRCode.toDataURL(link, {
        width: 400,
        margin: 2,
        color: {
          dark: "#000000",
          light: "#ffffff",
        },
      });

      // Create download link
      const downloadLink = document.createElement("a");
      downloadLink.href = qrDataUrl;
      downloadLink.download = `campaign-${prefill.prefillCode}-qr.png`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);

      showSnackbar("QR code downloaded!");
    } catch (err) {
      console.error("Failed to generate QR code:", err);
      showSnackbar("Failed to generate QR code");
    }
  };

  const handleEdit = (prefill: CampaignPrefill) => {
    setEditingPrefill(prefill);
  };

  const handleDeactivate = (prefill: CampaignPrefill) => {
    setPrefillToDeactivate(prefill);
    setDeactivateDialogOpen(true);
  };

  const confirmDeactivate = async () => {
    if (prefillToDeactivate) {
      await deletePrefill({
        variables: { prefillCode: prefillToDeactivate.prefillCode },
      });
    }
  };

  const handleSaveEdit = async (
    prefillCode: string,
    updates: { description?: string; creatorMessage?: string; isActive?: boolean }
  ) => {
    await updatePrefill({
      variables: {
        input: {
          prefillCode,
          ...updates,
        },
      },
    });
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load campaign prefills: {error.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            My Campaign Prefills
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create shareable links that pre-fill season creation for your unit
            members. ({activePrefillCount}/{MAX_PREFILLS} active)
          </Typography>
        </Box>
        <Tooltip
          title={
            !canCreateMore
              ? `You have reached the maximum of ${MAX_PREFILLS} active prefills`
              : ""
          }
        >
          <span>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              disabled={!canCreateMore}
            >
              Create Campaign Prefill
            </Button>
          </span>
        </Tooltip>
      </Stack>

      {prefills.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Campaign Prefills Yet
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Create a campaign prefill to generate shareable links for your unit
            members.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Your First Campaign Prefill
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Catalog</TableCell>
                <TableCell>Season</TableCell>
                <TableCell>Unit</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {prefills.map((prefill) => (
                <TableRow key={prefill.prefillCode}>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {prefill.prefillCode}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        maxWidth: 200,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {prefill.description || "-"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {prefill.catalog?.catalogName || "Unknown Catalog"}
                  </TableCell>
                  <TableCell>
                    {prefill.seasonName} {prefill.seasonYear}
                  </TableCell>
                  <TableCell>
                    {prefill.unitType} {prefill.unitNumber}
                    <Typography variant="caption" display="block" color="text.secondary">
                      {prefill.city}, {prefill.state}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {prefill.isActive ? (
                      <Chip
                        icon={<ActiveIcon />}
                        label="Active"
                        color="success"
                        size="small"
                      />
                    ) : (
                      <Chip
                        icon={<InactiveIcon />}
                        label="Inactive"
                        color="default"
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      <Tooltip title="Copy Link">
                        <IconButton
                          size="small"
                          onClick={() => handleCopyLink(prefill.prefillCode)}
                          aria-label="Copy link"
                        >
                          <CopyIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download QR Code">
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadQRCode(prefill)}
                          aria-label="Download QR code"
                        >
                          <QrCodeIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => handleEdit(prefill)}
                          aria-label="Edit"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {prefill.isActive && (
                        <Tooltip title="Deactivate">
                          <IconButton
                            size="small"
                            onClick={() => handleDeactivate(prefill)}
                            aria-label="Deactivate"
                            color="error"
                          >
                            <DeactivateIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Dialog */}
      <CreateCampaignPrefillDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={() => {
          refetch();
          setCreateDialogOpen(false);
          showSnackbar("Campaign prefill created successfully!");
        }}
        canCreate={canCreateMore}
      />

      {/* Edit Dialog */}
      {editingPrefill && (
        <EditCampaignPrefillDialog
          open={!!editingPrefill}
          prefill={editingPrefill}
          onClose={() => setEditingPrefill(null)}
          onSave={handleSaveEdit}
        />
      )}

      {/* Deactivate Confirmation Dialog */}
      <Dialog
        open={deactivateDialogOpen}
        onClose={() => setDeactivateDialogOpen(false)}
      >
        <DialogTitle>Deactivate Campaign Prefill?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to deactivate this campaign prefill? The link
            will no longer work for new season creation, but existing seasons
            created from this link will not be affected.
          </DialogContentText>
          {prefillToDeactivate && (
            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                <strong>Code:</strong> {prefillToDeactivate.prefillCode}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Unit:</strong> {prefillToDeactivate.unitType}{" "}
                {prefillToDeactivate.unitNumber}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeactivateDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDeactivate} color="error" variant="contained">
            Deactivate
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
};
