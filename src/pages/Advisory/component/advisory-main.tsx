import React from "react";
import { Box, Typography, Card, CardContent, Grid, Chip } from "@mui/material";

const AdvisoryMain: React.FC = () => (
  <Box>
    <Typography variant="h5" fontWeight={700} gutterBottom>Treatment Advisory</Typography>
    <Typography variant="body2" color="text.secondary" gutterBottom>AI-generated treatment plan for detected pests</Typography>
    <Card sx={{ mt: 2, background: "linear-gradient(135deg, rgba(76,175,80,0.1), rgba(76,255,3,0.05))" }}>
      <CardContent sx={{ display: "flex", alignItems: "center", gap: 2.5 }}>
        <Box sx={{ width: 64, height: 64, borderRadius: "14px", bgcolor: "rgba(239,83,80,0.12)", border: "1px solid rgba(239,83,80,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>i</Box>
        <Box>
          <Typography variant="h6" fontWeight={700}>Aphids (Aphis gossypii)</Typography>
          <Typography fontSize={12} color="text.secondary">South Farm A · Cotton Crop · Detected today</Typography>
          <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
            <Chip label="High Severity" size="small" sx={{ bgcolor: "rgba(239,83,80,0.15)", color: "#ef9a9a", fontSize: 10 }} />
            <Chip label="? Immediate Action" size="small" sx={{ bgcolor: "rgba(255,193,7,0.15)", color: "#ffe082", fontSize: 10 }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
    <Grid container spacing={3} sx={{ mt: 0.5 }}>
      <Grid item xs={12} md={7}>
        <Card>
          <CardContent>
            <Typography fontWeight={600} gutterBottom>Treatment Steps</Typography>
            {["Field Inspection — Assess full extent of infestation", "Prepare spray: Chlorpyrifos 40% EC at 2ml/L", "Apply uniformly on all plant surfaces", "Monitor for 48h, re-apply after 7 days if needed"].map((step, i) => (
              <Box key={i} sx={{ display: "flex", gap: 2, mb: 1.5, p: 1.5, borderRadius: "10px", bgcolor: "rgba(76,175,80,0.05)", border: "1px solid rgba(76,175,80,0.1)" }}>
                <Box sx={{ width: 28, height: 28, borderRadius: "50%", background: "linear-gradient(135deg,#2e7d32,#4caf50)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, flexShrink: 0 }}>{i + 1}</Box>
                <Typography fontSize={13}>{step}</Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={5}>
        <Card>
          <CardContent>
            <Typography fontWeight={600} gutterBottom>Recommended Product</Typography>
            <Typography fontWeight={600}>Chlorpyrifos 40% EC</Typography>
            <Chip label="Primary Recommendation" size="small" sx={{ mt: 0.5, mb: 1.5, bgcolor: "rgba(76,175,80,0.15)", color: "#a5d6a7", fontSize: 10 }} />
            {[["Dosage","2ml / L water"],["Method","Foliar Spray"],["Timing","Early Morning"],["Frequency","Every 7 days"]].map(([k, v]) => (
              <Box key={k} sx={{ display: "flex", justifyContent: "space-between", p: 1, bgcolor: "rgba(255,255,255,0.03)", borderRadius: "6px", mb: 0.5 }}>
                <Typography fontSize={12} color="text.secondary">{k}</Typography>
                <Typography fontSize={12} fontWeight={600}>{v}</Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  </Box>
);
export default AdvisoryMain;

