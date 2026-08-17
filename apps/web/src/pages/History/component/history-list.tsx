import React, { useEffect } from "react";
import { Box, Typography, Card, CardContent, Chip, Table, TableHead, TableRow, TableCell, TableBody } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { actionGetDetectionHistory } from "../../../slice/slice-pest";

const HistoryList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { list, loading } = useAppSelector((s) => s.pest);
  useEffect(() => { dispatch(actionGetDetectionHistory(undefined)); }, [dispatch]);
  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>Detection History</Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>Complete log of all past pest detections</Typography>
      <Card sx={{ mt: 2 }}>
        <CardContent>
          {loading ? <Typography color="text.secondary">Loading...</Typography> : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Pest</TableCell><TableCell>Field</TableCell>
                  <TableCell>Confidence</TableCell><TableCell>Severity</TableCell>
                  <TableCell>Date</TableCell><TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {list.data.map((d) => (
                  <TableRow key={d.DetectionID} hover>
                    <TableCell>{d.PestDetected?.PestName ?? "—"}</TableCell>
                    <TableCell>{d.FieldName}</TableCell>
                    <TableCell sx={{ color: "#4caf50", fontWeight: 600 }}>{(d.ConfidenceScore * 100).toFixed(1)}%</TableCell>
                    <TableCell><Chip label={d.SeverityLevel} size="small" /></TableCell>
                    <TableCell sx={{ fontSize: 12 }}>{new Date(d.DetectedAt).toLocaleDateString()}</TableCell>
                    <TableCell><Chip label={d.Status} size="small" color={d.Status === "Treated" ? "success" : "warning"} /></TableCell>
                  </TableRow>
                ))}
                {list.data.length === 0 && <TableRow><TableCell colSpan={6} align="center" sx={{ color: "text.secondary" }}>No detections yet</TableCell></TableRow>}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
export default HistoryList;

