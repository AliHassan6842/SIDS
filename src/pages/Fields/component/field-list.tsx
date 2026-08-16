import React, { useEffect, useState } from "react";
import { Grid, Card, CardContent, Typography, Box, Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { actionGetFields, actionUpsertField, actionDeleteField } from "../../../slice/slice-field";
import { useTheme } from "@mui/material";

const HEALTH_COLOR = (score: number) => score >= 75 ? "#4caf50" : score >= 50 ? "#ff9800" : "#ef5350";

const FieldList: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { list, loading } = useAppSelector((s) => s.field);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ FieldName: "", Location: "", CropType: "Wheat", SizeAcres: 10, Variety: "", SowingDate: "", Irrigation: "" });

  useEffect(() => { dispatch(actionGetFields(undefined)); }, [dispatch]);

  const handleSave = () => {
    dispatch(actionUpsertField({ ...form, IsActive: true, PlantingDate: form.SowingDate || new Date().toISOString(), HealthScore: 80, AlertLevel: "Safe" as const }));
    setOpen(false);
    setForm({ FieldName: "", Location: "", CropType: "Wheat", SizeAcres: 10, Variety: "", SowingDate: "", Irrigation: "" });
  };

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={700}>Field Management</Typography>
          <Typography variant="body2" color="text.secondary">Monitor and manage all your registered fields</Typography>
        </Box>
        <Button variant="contained" onClick={() => setOpen(true)}>+ Add New Field</Button>
      </Box>
      {loading ? <Typography color="text.secondary">Loading fields...</Typography> : (
        <Grid container spacing={2.5}>
          {list.data.map((field) => (
            <Grid item xs={12} sm={6} md={4} key={field.FieldID}>
              <Card sx={{ transition: "0.3s", "&:hover": { borderColor: theme.palette.primary.main, transform: "translateY(-2px)" } }}>
                <CardContent>
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1.5 }}>
                    <Box sx={{ width: 44, height: 44, borderRadius: "12px", bgcolor: "rgba(76,175,80,0.12)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>i</Box>
                    <Chip label={field.AlertLevel} size="small" sx={{ bgcolor: field.AlertLevel === "Critical" ? "rgba(239,83,80,0.15)" : field.AlertLevel === "Warning" ? "rgba(255,152,0,0.15)" : "rgba(76,175,80,0.15)", color: field.AlertLevel === "Critical" ? "#ef9a9a" : field.AlertLevel === "Warning" ? "#ffcc80" : "#a5d6a7", fontSize: 10 }} />
                  </Box>
                  <Typography fontWeight={700}>{field.FieldName}</Typography>
                  <Typography fontSize={12} color="text.secondary">{field.Location} ·- {field.CropType}</Typography>
                  <Grid container spacing={1} sx={{ mt: 1.5, pt: 1.5, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                    {[
                      { label: "Size", value: `${field.SizeAcres} Acres` },
                      { label: "Health", value: `${field.HealthScore}%`, color: HEALTH_COLOR(field.HealthScore) },
                    ].map((item) => (
                      <Grid item xs={6} key={item.label}>
                        <Typography fontSize={10} color="text.secondary" textTransform="uppercase">{item.label}</Typography>
                        <Typography fontSize={13} fontWeight={600} sx={{ color: item.color ?? "text.primary" }}>{item.value}</Typography>
                      </Grid>
                    ))}
                  </Grid>
                  <Box sx={{ display: "flex", gap: 1, mt: 1.5 }}>
                    <Button size="small" fullWidth sx={{ bgcolor: "rgba(76,175,80,0.1)", color: "#81c784", "&:hover": { bgcolor: "rgba(76,175,80,0.2)" } }}>View</Button>
                    <Button size="small" fullWidth color="error" variant="text" onClick={() => dispatch(actionDeleteField(field.FieldID))}>Delete</Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          <Grid item xs={12} sm={6} md={4}>
            <Card onClick={() => setOpen(true)} sx={{ border: "2px dashed rgba(76,175,80,0.3)", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", minHeight: 200, "&:hover": { borderColor: "#4caf50" }, transition: "0.3s" }}>
              <Box sx={{ textAlign: "center" }}>
                <Typography fontSize={32}>+</Typography>
                <Typography fontSize={13} color="primary" fontWeight={600}>Add New Field</Typography>
              </Box>
            </Card>
          </Grid>
        </Grid>
      )}
      <Dialog open={open} onClose={() => setOpen(false)} PaperProps={{ sx: { bgcolor: "background.paper", border: `1px solid ${theme.palette.divider}` } }}>
        <DialogTitle>Add New Field</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2, minWidth: 360 }}>
          <TextField label="Field Name" value={form.FieldName} onChange={(e) => setForm({ ...form, FieldName: e.target.value })} size="small" fullWidth />
          <TextField label="Location / City" value={form.Location} onChange={(e) => setForm({ ...form, Location: e.target.value })} size="small" fullWidth />
          <TextField label="Size (Acres)" type="number" value={form.SizeAcres} onChange={(e) => setForm({ ...form, SizeAcres: Number(e.target.value) })} size="small" fullWidth />
          
          <Typography variant="subtitle2" sx={{ mt: 1, color: "text.secondary" }}>Crop Cycle Details</Typography>
          <TextField label="Crop Type" value={form.CropType} onChange={(e) => setForm({ ...form, CropType: e.target.value })} size="small" fullWidth />
          <TextField label="Variety" value={form.Variety} onChange={(e) => setForm({ ...form, Variety: e.target.value })} size="small" fullWidth />
          <TextField label="Sowing Date" type="date" InputLabelProps={{ shrink: true }} value={form.SowingDate} onChange={(e) => setForm({ ...form, SowingDate: e.target.value })} size="small" fullWidth />
          <TextField label="Irrigation" placeholder="e.g. Drip, Flood" value={form.Irrigation} onChange={(e) => setForm({ ...form, Irrigation: e.target.value })} size="small" fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>Save Field</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FieldList;


