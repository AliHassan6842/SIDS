import React, { useState } from "react";
import { Box, Drawer, Toolbar, Alert } from "@mui/material";
import { Outlet } from "react-router-dom";
import AgroSidebar from "./Sidebar/AgroSidebar";
import AgroHeader from "./Header/AgroHeader";
import BottomNav from "./Sidebar/BottomNav";
import { useAppDispatch, useAppSelector } from "../hooks/useStoreData";
import { toggleOfflineMode } from "../slice/slice-sync";

const DRAWER_WIDTH = 250;

const MainLayout: React.FC = () => {
  const [open, setOpen] = useState(true);
  const dispatch = useAppDispatch();
  const { isOffline } = useAppSelector(s => s.sync);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default", pb: { xs: 8, md: 0 } }}>
      <AgroHeader drawerWidth={DRAWER_WIDTH} onToggle={() => setOpen(!open)} />
      
      {/* Desktop Sidebar */}
      <Drawer 
        variant="persistent" 
        open={open} 
        sx={{
          display: { xs: 'none', md: 'block' },
          width: open ? DRAWER_WIDTH : 0, 
          flexShrink: 0,
          transition: 'width 0.3s',
          "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" },
        }}
      >
        <AgroSidebar />
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, width: '100%', transition: 'margin 0.3s' }}>
        <Toolbar />
        
        {/* Offline Simulation Banner */}
        <Box sx={{ mb: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
          <Alert 
            severity={isOffline ? "error" : "success"} 
            variant="filled" 
            sx={{ flex: 1, cursor: 'pointer' }}
            onClick={() => dispatch(toggleOfflineMode())}
          >
            {isOffline 
              ? "You are offline. Data is saved locally and will sync when connected. (Tap to toggle)" 
              : "System Online. All data synced. (Tap to simulate offline mode)"}
          </Alert>
        </Box>

        <Outlet />
      </Box>

      {/* Mobile Bottom Navigation */}
      <BottomNav />
    </Box>
  );
};

export default MainLayout;
