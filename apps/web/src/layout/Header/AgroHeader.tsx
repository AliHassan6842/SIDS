import React from "react";
import { AppBar, Toolbar, Typography, IconButton, Badge, Box, InputBase } from "@mui/material";
import NotificationsOutlined from "@mui/icons-material/NotificationsOutlined";
import SearchIcon from "@mui/icons-material/Search";
import AccountCircle from "@mui/icons-material/AccountCircle";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import SettingsBrightnessIcon from "@mui/icons-material/SettingsBrightness";
import { useAppSelector, useAppDispatch } from "../../hooks/useStoreData";
import { setThemeMode } from "../../slice/slice-theme";

interface Props { drawerWidth: number; onToggle: () => void; }

const AgroHeader: React.FC<Props> = ({ drawerWidth }) => {
  const unreadCount = useAppSelector((s) => s.alert.unreadCount);
  const themeMode = useAppSelector((s) => s.theme.mode);
  const dispatch = useAppDispatch();

  const handleToggleTheme = () => {
    if (themeMode === "light") dispatch(setThemeMode("dark"));
    else if (themeMode === "dark") dispatch(setThemeMode("system"));
    else dispatch(setThemeMode("light"));
  };

  const ThemeIcon = themeMode === "light" ? LightModeIcon : themeMode === "dark" ? DarkModeIcon : SettingsBrightnessIcon;

  return (
    <AppBar position="fixed" elevation={0} sx={{ zIndex: (t) => t.zIndex.drawer + 1, width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}>
      <Toolbar sx={{ gap: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", bgcolor: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "50px", px: 2, py: 0.5, gap: 1 }}>
          <SearchIcon sx={{ fontSize: 18, color: "text.secondary" }} />
          <InputBase placeholder="Search pests, fields..." sx={{ fontSize: 13, color: "text.primary", width: 180 }} />
        </Box>
        <Box sx={{ ml: "auto", display: "flex", gap: 1.5, alignItems: "center" }}>
          <IconButton size="small" onClick={handleToggleTheme}>
            <ThemeIcon sx={{ color: "text.secondary", fontSize: 20 }} />
          </IconButton>
          <IconButton size="small">
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsOutlined sx={{ color: "text.secondary" }} />
            </Badge>
          </IconButton>
          <IconButton size="small">
            <AccountCircle sx={{ color: "text.secondary" }} />
          </IconButton>
          <Typography variant="caption" color="text.secondary">Umar Ali</Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default AgroHeader;
