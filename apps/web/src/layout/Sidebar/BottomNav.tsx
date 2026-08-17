import React from "react";
import { BottomNavigation, BottomNavigationAction, Paper } from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import LandscapeIcon from "@mui/icons-material/Landscape";
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import AssignmentIcon from "@mui/icons-material/Assignment";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import { useNavigate, useLocation } from "react-router-dom";

export const NAV_ITEMS = [
  { label: "Home", value: "/home", icon: <HomeIcon /> },
  { label: "Fields", value: "/fields", icon: <LandscapeIcon /> },
  { label: "Scan", value: "/scan", icon: <CameraAltIcon /> },
  { label: "Tasks", value: "/tasks", icon: <AssignmentIcon /> },
  { label: "More", value: "/more", icon: <MoreHorizIcon /> },
];

const BottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000, display: { md: 'none' } }} elevation={3}>
      <BottomNavigation
        showLabels
        value={location.pathname}
        onChange={(_, newValue) => {
          navigate(newValue);
        }}
        sx={{
          height: 65,
          "& .MuiBottomNavigationAction-root": {
            minWidth: "auto",
            padding: "6px 0",
          }
        }}
      >
        {NAV_ITEMS.map((item) => (
          <BottomNavigationAction
            key={item.value}
            label={item.label}
            value={item.value}
            icon={item.icon}
          />
        ))}
      </BottomNavigation>
    </Paper>
  );
};

export default BottomNav;
