/**
 * ReportsPage - Generate and download season reports
 */

import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation } from "@apollo/client/react";
import {
  Box,
  Typography,
  Paper,
  Stack,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Link,
} from "@mui/material";
import {
  Download as DownloadIcon,
  Description as FileIcon,
} from "@mui/icons-material";
import { REQUEST_SEASON_REPORT } from "../lib/graphql";

interface ReportResult {
  reportId: string;
  reportUrl?: string;
  status: string;
  expiresAt?: string;
}

export const ReportsPage: React.FC = () => {
  const { seasonId: encodedSeasonId } = useParams<{ seasonId: string }>();
  const seasonId = encodedSeasonId ? decodeURIComponent(encodedSeasonId) : "";
  const [format, setFormat] = useState<"CSV" | "XLSX">("XLSX");
  const [lastReport, setLastReport] = useState<ReportResult | null>(null);

  const [requestReport, { loading, error }] = useMutation<{
    requestSeasonReport: ReportResult;
  }>(REQUEST_SEASON_REPORT, {
    onCompleted: (data) => {
      setLastReport(data.requestSeasonReport);
    },
  });

  const handleGenerateReport = async () => {
    if (!seasonId) return;
    setLastReport(null);
    await requestReport({
      variables: { seasonId, format },
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Reports & Exports
      </Typography>

      {/* Generate Report */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate Season Report
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Export all orders for this season to Excel or CSV format. The report
          includes customer names, contact info, order details, payment methods,
          and totals.
        </Typography>

        <Stack direction="row" spacing={2} alignItems="center" mb={2}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Format</InputLabel>
            <Select
              value={format}
              label="Format"
              onChange={(e) => setFormat(e.target.value as "CSV" | "XLSX")}
              disabled={loading}
            >
              <MenuItem value="XLSX">
                <Stack direction="row" spacing={1} alignItems="center">
                  <FileIcon fontSize="small" />
                  <span>Excel (XLSX)</span>
                </Stack>
              </MenuItem>
              <MenuItem value="CSV">
                <Stack direction="row" spacing={1} alignItems="center">
                  <FileIcon fontSize="small" />
                  <span>CSV</span>
                </Stack>
              </MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={
              loading ? <CircularProgress size={20} /> : <DownloadIcon />
            }
            onClick={handleGenerateReport}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Report"}
          </Button>
        </Stack>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Failed to generate report: {error.message}
          </Alert>
        )}

        {lastReport && (
          <Alert
            severity={lastReport.status === "COMPLETED" ? "success" : "info"}
            sx={{ mt: 2 }}
          >
            {lastReport.status === "COMPLETED" && lastReport.reportUrl ? (
              <Stack spacing={1}>
                <Typography variant="body2">
                  ✅ Report generated successfully! Your download is ready.
                </Typography>
                <Link
                  href={lastReport.reportUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                  sx={{ fontWeight: "medium" }}
                >
                  Download Report ({format})
                </Link>
                {lastReport.expiresAt && (
                  <Typography variant="caption" color="text.secondary">
                    Link expires:{" "}
                    {new Date(lastReport.expiresAt).toLocaleString()}
                  </Typography>
                )}
              </Stack>
            ) : lastReport.status === "PENDING" ? (
              <Typography variant="body2">
                ⏳ Report is being generated. This may take a moment...
              </Typography>
            ) : (
              <Typography variant="body2">
                ❌ Report generation failed. Please try again.
              </Typography>
            )}
          </Alert>
        )}
      </Paper>

      {/* Report Info */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          About Reports
        </Typography>
        <Stack spacing={1}>
          <Typography variant="body2">
            • <strong>Excel (XLSX):</strong> Formatted spreadsheet with multiple
            columns, suitable for further analysis and pivot tables.
          </Typography>
          <Typography variant="body2">
            • <strong>CSV:</strong> Plain text file, compatible with all
            spreadsheet programs and databases.
          </Typography>
          <Typography variant="body2">
            • Report links expire after 24 hours for security reasons.
          </Typography>
          <Typography variant="body2">
            • All customer data is securely encrypted during storage and
            transmission.
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
};
