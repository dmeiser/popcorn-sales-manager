/**
 * EditProfileDialog component - Dialog for editing a seller profile name
 */

import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  MenuItem,
} from "@mui/material";

interface EditProfileDialogProps {
  open: boolean;
  profileId: string;
  currentName: string;
  currentUnitType?: string;
  currentUnitNumber?: number;
  onClose: () => void;
  onSubmit: (
    profileId: string,
    newName: string,
    unitType?: string,
    unitNumber?: number,
  ) => Promise<void>;
}

const UNIT_TYPES = [
  { value: "", label: "None" },
  { value: "Pack", label: "Pack (Cub Scouts)" },
  { value: "Troop", label: "Troop (Scouts BSA)" },
  { value: "Crew", label: "Crew (Venturing)" },
  { value: "Ship", label: "Ship (Sea Scouts)" },
  { value: "Post", label: "Post (Exploring)" },
  { value: "Club", label: "Club (Exploring)" },
];

export const EditProfileDialog: React.FC<EditProfileDialogProps> = ({
  open,
  profileId,
  currentName,
  currentUnitType = "",
  currentUnitNumber,
  onClose,
  onSubmit,
}) => {
  const [sellerName, setSellerName] = useState(currentName);
  const [unitType, setUnitType] = useState(currentUnitType);
  const [unitNumber, setUnitNumber] = useState(
    currentUnitNumber ? String(currentUnitNumber) : "",
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSellerName(currentName);
    setUnitType(currentUnitType);
    setUnitNumber(currentUnitNumber ? String(currentUnitNumber) : "");
  }, [currentName, currentUnitType, currentUnitNumber, open]);

  const hasChanges = () => {
    const currentNumStr = currentUnitNumber ? String(currentUnitNumber) : "";
    return (
      sellerName !== currentName ||
      unitType !== currentUnitType ||
      unitNumber !== currentNumStr
    );
  };

  const handleSubmit = async () => {
    if (!sellerName.trim() || !hasChanges()) return;

    setLoading(true);
    try {
      const parsedUnitNumber = unitNumber.trim()
        ? parseInt(unitNumber.trim(), 10)
        : undefined;
      await onSubmit(
        profileId,
        sellerName.trim(),
        unitType || undefined,
        parsedUnitNumber,
      );
      onClose();
    } catch (error) {
      console.error("Failed to update profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setSellerName(currentName);
      setUnitType(currentUnitType);
      setUnitNumber(currentUnitNumber ? String(currentUnitNumber) : "");
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Seller Profile</DialogTitle>
      <DialogContent>
        <Box pt={1} display="flex" flexDirection="column" gap={2}>
          <TextField
            autoFocus
            fullWidth
            label="Seller Name"
            value={sellerName}
            onChange={(e) => setSellerName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && sellerName.trim() && hasChanges()) {
                handleSubmit();
              }
            }}
            disabled={loading}
          />

          <TextField
            fullWidth
            select
            label="Unit Type (Optional)"
            value={unitType}
            onChange={(e) => setUnitType(e.target.value)}
            disabled={loading}
            helperText="Select the type of Scouting unit"
          >
            {UNIT_TYPES.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            type="number"
            label="Unit Number (Optional)"
            placeholder="e.g., 123"
            value={unitNumber}
            onChange={(e) => setUnitNumber(e.target.value)}
            disabled={loading}
            helperText="Enter the unit number if applicable"
            slotProps={{
              htmlInput: {
                min: 1,
                step: 1,
              },
            }}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!sellerName.trim() || !hasChanges() || loading}
        >
          {loading ? "Saving..." : "Save Changes"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
