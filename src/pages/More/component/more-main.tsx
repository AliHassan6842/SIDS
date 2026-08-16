import React from "react";
import { Box, Typography, List, ListItem, ListItemIcon, ListItemText, ListItemButton, Divider } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import HistoryIcon from "@mui/icons-material/History";
import AssessmentIcon from "@mui/icons-material/Assessment";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LogoutIcon from "@mui/icons-material/Logout";
import WarningIcon from "@mui/icons-material/Warning";
import LocalLibraryIcon from "@mui/icons-material/LocalLibrary";
import { clearToken } from "../../../auth/tokenStore";
import { useTheme, Button, Card, CardContent } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAppDispatch } from "../../../hooks/useStoreData";

const MoreMain: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const dispatch = useAppDispatch();

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  const menuItems = [
    { label: "My Profile", icon: <PersonIcon />, path: "/profile" },
    { label: "Alerts & Notifications", icon: <WarningIcon />, path: "/alerts" },
    { label: "Treatment Advisory", icon: <LocalLibraryIcon />, path: "/advisory" },
    { label: "Detection History", icon: <HistoryIcon />, path: "/history" },
    { label: "Analytics & Reports", icon: <AssessmentIcon />, path: "/reports" },
  ];

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", pb: 10 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom sx={{ px: 2, mb: 2 }}>
        More
      </Typography>

      <List sx={{ bgcolor: theme.palette.background.paper, borderRadius: 2, overflow: 'hidden', border: `1px solid ${theme.palette.divider}` }}>
        {menuItems.map((item, index) => (
          <React.Fragment key={item.label}>
            <ListItem disablePadding>
              <ListItemButton onClick={() => navigate(item.path)} sx={{ py: 2 }}>
                <ListItemIcon sx={{ color: "primary.main" }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 600 }} />
              </ListItemButton>
            </ListItem>
            {index < menuItems.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>

      <Typography variant="subtitle2" color="text.secondary" sx={{ px: 2, mt: 4, mb: 1, textTransform: 'uppercase' }}>
        App Appearance
      </Typography>
      
      <Card sx={{ mx: 2, mb: 4, borderRadius: 2, border: `1px solid ${theme.palette.divider}` }}>
        <CardContent sx={{ display: 'flex', gap: 1, p: '16px !important' }}>
          {['light', 'dark', 'system'].map((mode) => {
            const isSelected = theme.palette.mode === mode || (mode === 'system' && !theme.palette.mode);
            return (
              <Button 
                key={mode}
                variant={isSelected ? "contained" : "outlined"}
                fullWidth
                size="small"
                onClick={() => dispatch({ type: 'theme/actionSetThemeMode', payload: mode })}
                sx={{ textTransform: 'capitalize', fontWeight: 600 }}
              >
                {mode}
              </Button>
            );
          })}
        </CardContent>
      </Card>

      <Typography variant="subtitle2" color="text.secondary" sx={{ px: 2, mb: 1, textTransform: 'uppercase' }}>
        Administration
      </Typography>

      <List sx={{ bgcolor: theme.palette.background.paper, borderRadius: 2, overflow: 'hidden', border: `1px solid ${theme.palette.divider}` }}>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate("/admin")} sx={{ py: 2 }}>
            <ListItemIcon sx={{ color: "secondary.main" }}><AdminPanelSettingsIcon /></ListItemIcon>
            <ListItemText primary="Admin Dashboard" primaryTypographyProps={{ fontWeight: 600 }} />
          </ListItemButton>
        </ListItem>
        <Divider />
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout} sx={{ py: 2 }}>
            <ListItemIcon sx={{ color: "error.main" }}><LogoutIcon /></ListItemIcon>
            <ListItemText primary="Log out" primaryTypographyProps={{ fontWeight: 600, color: "error.main" }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};

export default MoreMain;
