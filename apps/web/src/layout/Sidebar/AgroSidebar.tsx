import React from "react";
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, useTheme } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";
import { NAV_ITEMS } from "./BottomNav";

const AgroSidebar: React.FC = () => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Box sx={{ height: "100%", bgcolor: "background.paper", display: "flex", flexDirection: "column" }}>
      <Box sx={{ p: 3, display: "flex", alignItems: "center", gap: 1.5 }}>
        <Box sx={{ width: 40, height: 40, borderRadius: "10px", bgcolor: "primary.main", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
          🌿
        </Box>
        <Box>
          <Typography fontWeight={800} fontSize={18} sx={{ background: `linear-gradient(90deg, ${theme.palette.primary.light}, ${theme.palette.secondary.main})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            AgroSense
          </Typography>
          <Typography fontSize={11} color="text.secondary" textTransform="uppercase" letterSpacing={0.5}>
            Pest Advisory System
          </Typography>
        </Box>
      </Box>

      <List sx={{ px: 2, flex: 1 }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname.startsWith(item.value);
          return (
            <ListItem key={item.label} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.value)}
                sx={{
                  borderRadius: "10px",
                  bgcolor: isActive ? `${theme.palette.primary.main}15` : "transparent",
                  color: isActive ? theme.palette.primary.main : theme.palette.text.secondary,
                  borderLeft: isActive ? `3px solid ${theme.palette.primary.main}` : "3px solid transparent",
                  "&:hover": { bgcolor: `${theme.palette.primary.main}10` },
                }}
              >
                <ListItemIcon sx={{ color: "inherit", minWidth: 40 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: isActive ? 700 : 500, fontSize: 14 }} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
};

export default AgroSidebar;
