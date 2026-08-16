import React from "react";
import { Box, Typography, Grid, Card, CardContent } from "@mui/material";

const AdminDashboard: React.FC = () => (
  <Box>
    <Typography variant="h5" fontWeight={700} gutterBottom>Admin Dashboard</Typography>
    <Typography variant="body2" color="text.secondary" gutterBottom>System overview and user management</Typography>
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {[
        { label: "Registered Farmers", value: 124, color: "#81c784" },
        { label: "Total Detections",  value: 1847, color: "#ef9a9a" },
        { label: "Active Fields",     value: 389, color: "#ffe082" },
        { label: "AI Model Accuracy", value: "94.3%", color: "#80deea" },
      ].map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item.label}>
          <Card>
            <CardContent sx={{ textAlign: "center" }}>
              <Typography fontSize={30} fontWeight={800} sx={{ color: item.color }}>{item.value}</Typography>
              <Typography fontSize={11} color="text.secondary">{item.label}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
);
export default AdminDashboard;

