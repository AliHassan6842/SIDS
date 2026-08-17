import React from "react";
import { Box, Typography, Card, CardContent, Grid, TextField, Button, Avatar } from "@mui/material";
import { useTheme } from "@mui/material";

const ProfileMain: React.FC = () => {
  const theme = useTheme();
  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>My Profile</Typography>
      <Card sx={{ mb: 3, background: "linear-gradient(135deg, rgba(46,125,50,0.2), rgba(76,255,3,0.05))" }}>
        <CardContent sx={{ display: "flex", alignItems: "center", gap: 3 }}>
          <Avatar sx={{ width: 72, height: 72, background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.secondary.main})`, fontSize: 28, fontWeight: 700 }}>UA</Avatar>
          <Box>
            <Typography variant="h6" fontWeight={700}>Umar Ali</Typography>
            <Typography fontSize={13} color="text.secondary">farmer@agrosense.com ·- +92-300-1234567</Typography>
            <Box sx={{ mt: 1, px: 1.5, py: 0.5, borderRadius: "50px", bgcolor: "rgba(76,175,80,0.15)", border: "1px solid rgba(76,175,80,0.3)", display: "inline-block" }}>
              <Typography fontSize={12} color="primary" fontWeight={600}>Registered Farmer</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography fontWeight={600} gutterBottom>Personal Information</Typography>
              <Grid container spacing={2}>
                {[["Full Name","Umar Ali"],["Email","farmer@agrosense.com"],["Phone","+92-300-1234567"],["Location","Multan, Punjab"]].map(([label, val]) => (
                  <Grid item xs={12} key={label}><TextField label={label} defaultValue={val} fullWidth size="small" /></Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography fontWeight={600} gutterBottom>Farm Information</Typography>
              <Grid container spacing={2}>
                {[["Farm Name","Ali Farms & Agriculture"],["Total Land","73 Acres"],["Primary Crop","Wheat"]].map(([label, val]) => (
                  <Grid item xs={12} key={label}><TextField label={label} defaultValue={val} fullWidth size="small" /></Grid>
                ))}
              </Grid>
              <Button variant="contained" fullWidth sx={{ mt: 2 }}>Save Changes</Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
export default ProfileMain;


