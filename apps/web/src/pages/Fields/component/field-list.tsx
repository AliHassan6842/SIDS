import React, { useEffect, useState } from "react";
import { Grid, Card, CardContent, Typography, Box, Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { actionGetFields, actionUpsertField, actionDeleteField } from "../../../slice/slice-field";
import { useTheme } from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const HEALTH_COLOR = (score: number) => score >= 75 ? "#4caf50" : score >= 50 ? "#ff9800" : "#ef5350";

const fieldSchema = z.object({
  fieldName: z.string().min(2, "Field Name is required (min 2 chars)"),
  location: z.string().min(2, "Location is required"),
  sizeAcres: z.number({ invalid_type_error: "Must be a number" }).positive("Size must be positive"),
  cropType: z.string().min(2, "Crop Type is required"),
  variety: z.string().optional(),
  sowingDate: z.string().min(1, "Sowing Date is required"),
  irrigation: z.string().optional()
});

type FieldFormValues = z.infer<typeof fieldSchema>;

const FieldList: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { list, loading } = useAppSelector((s) => s.field);
  const [open, setOpen] = useState(false);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<FieldFormValues>({
    resolver: zodResolver(fieldSchema),
    defaultValues: {
      fieldName: "", location: "", cropType: "Wheat", sizeAcres: 10, variety: "", sowingDate: "", irrigation: ""
    }
  });

  useEffect(() => { dispatch(actionGetFields(undefined)); }, [dispatch]);

  const onSubmit = (data: FieldFormValues) => {
    dispatch(actionUpsertField({ 
      ...data, 
      isActive: true, 
      plantingDate: data.sowingDate, 
      healthScore: 80, 
      alertLevel: "Safe" 
    }));
    setOpen(false);
    reset();
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
            <Grid item xs={12} sm={6} md={4} key={field.fieldId}>
              <Card sx={{ transition: "0.3s", "&:hover": { borderColor: theme.palette.primary.main, transform: "translateY(-2px)" } }}>
                <CardContent>
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1.5 }}>
                    <Box sx={{ width: 44, height: 44, borderRadius: "12px", bgcolor: "rgba(76,175,80,0.12)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🌿</Box>
                    <Chip label={field.alertLevel} size="small" sx={{ bgcolor: field.alertLevel === "Critical" ? "rgba(239,83,80,0.15)" : field.alertLevel === "Warning" ? "rgba(255,152,0,0.15)" : "rgba(76,175,80,0.15)", color: field.alertLevel === "Critical" ? "#ef9a9a" : field.alertLevel === "Warning" ? "#ffcc80" : "#a5d6a7", fontSize: 10 }} />
                  </Box>
                  <Typography fontWeight={700}>{field.fieldName}</Typography>
                  <Typography fontSize={12} color="text.secondary">{field.location} · {field.cropType}</Typography>
                  <Grid container spacing={1} sx={{ mt: 1.5, pt: 1.5, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                    {[
                      { label: "Size", value: `${field.sizeAcres} Acres` },
                      { label: "Health", value: `${field.healthScore}%`, color: HEALTH_COLOR(field.healthScore) },
                    ].map((item) => (
                      <Grid item xs={6} key={item.label}>
                        <Typography fontSize={10} color="text.secondary" textTransform="uppercase">{item.label}</Typography>
                        <Typography fontSize={13} fontWeight={600} sx={{ color: item.color ?? "text.primary" }}>{item.value}</Typography>
                      </Grid>
                    ))}
                  </Grid>
                  <Box sx={{ display: "flex", gap: 1, mt: 1.5 }}>
                    <Button size="small" fullWidth sx={{ bgcolor: "rgba(76,175,80,0.1)", color: "#81c784", "&:hover": { bgcolor: "rgba(76,175,80,0.2)" } }}>View</Button>
                    <Button size="small" fullWidth color="error" variant="text" onClick={() => dispatch(actionDeleteField(field.fieldId))}>Delete</Button>
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

      <Dialog open={open} onClose={() => { setOpen(false); reset(); }} PaperProps={{ sx: { bgcolor: "background.paper", border: `1px solid ${theme.palette.divider}` } }}>
        <DialogTitle>Add New Field</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2, minWidth: 360 }}>
          <Controller name="fieldName" control={control} render={({ field }) => (
            <TextField {...field} label="Field Name" size="small" fullWidth error={!!errors.fieldName} helperText={errors.fieldName?.message} />
          )} />
          <Controller name="location" control={control} render={({ field }) => (
            <TextField {...field} label="Location / City" size="small" fullWidth error={!!errors.location} helperText={errors.location?.message} />
          )} />
          <Controller name="sizeAcres" control={control} render={({ field }) => (
            <TextField {...field} label="Size (Acres)" type="number" size="small" fullWidth error={!!errors.sizeAcres} helperText={errors.sizeAcres?.message} onChange={e => field.onChange(Number(e.target.value))} />
          )} />
          
          <Typography variant="subtitle2" sx={{ mt: 1, color: "text.secondary" }}>Crop Cycle Details</Typography>
          
          <Controller name="cropType" control={control} render={({ field }) => (
            <TextField {...field} label="Crop Type" size="small" fullWidth error={!!errors.cropType} helperText={errors.cropType?.message} />
          )} />
          <Controller name="variety" control={control} render={({ field }) => (
            <TextField {...field} label="Variety (Optional)" size="small" fullWidth error={!!errors.variety} helperText={errors.variety?.message} />
          )} />
          <Controller name="sowingDate" control={control} render={({ field }) => (
            <TextField {...field} label="Sowing Date" type="date" InputLabelProps={{ shrink: true }} size="small" fullWidth error={!!errors.sowingDate} helperText={errors.sowingDate?.message} />
          )} />
          <Controller name="irrigation" control={control} render={({ field }) => (
            <TextField {...field} label="Irrigation (Optional)" placeholder="e.g. Drip, Flood" size="small" fullWidth error={!!errors.irrigation} helperText={errors.irrigation?.message} />
          )} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpen(false); reset(); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit(onSubmit)}>Save Field</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FieldList;
