/**
 * CreateProfileDialog component - Dialog for creating a new seller profile
 */

import React, { useState } from "react";
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

interface CreateProfileDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (
    sellerName: string,
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

export const CreateProfileDialog: React.FC<CreateProfileDialogProps> = ({
  open,
  onClose,
  onSubmit,
}) => {
  const [sellerName, setSellerName] = useState("");
  const [unitType, setUnitType] = useState("");
  const [unitNumber, setUnitNumber] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!sellerName.trim()) return;

    setLoading(true);
    try {
      const parsedUnitNumber = unitNumber.trim()
        ? parseInt(unitNumber.trim(), 10)
        : undefined;
      await onSubmit(
        sellerName.trim(),
        unitType || undefined,
        parsedUnitNumber,
      );
      setSellerName("");
      setUnitType("");
      setUnitNumber("");
      onClose();
    } catch (error) {
      console.error("Failed to create profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setSellerName("");
      setUnitType("");
      setUnitNumber("");
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create New Seller Profile</DialogTitle>
      <DialogContent>
        <Box pt={1} display="flex" flexDirection="column" gap={2}>
          <TextField
            autoFocus
            fullWidth
            label="Seller Name"
            placeholder="e.g., Scout's First and Last Name"
            value={sellerName}
            onChange={(e) => setSellerName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && sellerName.trim()) {
                handleSubmit();
              }
            }}
            disabled={loading}
            helperText="Enter the name of the Scout or seller"
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
          disabled={!sellerName.trim() || loading}
        >
          {loading ? "Creating..." : "Create Seller"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
