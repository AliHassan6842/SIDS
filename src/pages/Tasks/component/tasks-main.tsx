import React from "react";
import { Box, Typography, Card, CardContent, Button, Divider, CircularProgress } from "@mui/material";
import SyncIcon from "@mui/icons-material/Sync";
import EventIcon from "@mui/icons-material/Event";
import WifiOffIcon from "@mui/icons-material/WifiOff";
import { useTheme } from "@mui/material";
import { useAppSelector, useAppDispatch } from "../../../hooks/useStoreData";
import { startSync, syncSuccess } from "../../../slice/slice-sync";

const TasksMain: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { queue, syncing } = useAppSelector(s => s.sync);

  const handleSync = () => {
    dispatch(startSync());
    setTimeout(() => {
      dispatch(syncSuccess());
    }, 2000);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", pb: 10 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <EventIcon sx={{ color: "primary.main" }} /> Tasks & Offline Queue
      </Typography>

      <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 3, mb: 1, textTransform: 'uppercase' }}>
        Today
      </Typography>
      
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, '&:last-child': { pb: 2 } }}>
          <Box>
            <Typography fontWeight={600} fontSize={15}>Rescout Field A</Typography>
            <Typography fontSize={13} color="text.secondary">8:00 AM</Typography>
          </Box>
        </CardContent>
      </Card>

      <Divider sx={{ my: 4 }} />

      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1, textTransform: 'uppercase' }}>
        Offline Queue: {queue.length}
      </Typography>
      
      <Card sx={{ border: `1px dashed ${theme.palette.divider}`, bgcolor: `${theme.palette.warning.main}10` }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          {queue.length === 0 ? (
            <>
              <Typography fontWeight={600} color="text.secondary">Queue is empty</Typography>
              <Typography fontSize={13} color="text.secondary">All data is synced.</Typography>
            </>
          ) : (
            <>
              <WifiOffIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
              <Typography fontWeight={600}>{queue.length} items waiting to sync</Typography>
              <Typography fontSize={13} color="text.secondary" sx={{ mb: 3 }}>
                These will be uploaded automatically when you regain internet connection.
              </Typography>
              
              <Button 
                variant="contained" 
                fullWidth 
                size="large"
                startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <SyncIcon />}
                disabled={syncing}
                onClick={handleSync}
                sx={{ py: 1.5, fontWeight: 700 }}
              >
                {syncing ? "Syncing..." : "Sync Now"}
              </Button>
            </>
          )}
        </CardContent>
      </Card>
      
      {queue.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
          {queue.map(task => (
            <Card key={task.id} sx={{ bgcolor: 'background.default', border: `1px solid ${theme.palette.divider}` }}>
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography fontSize={13} fontWeight={600} textTransform="capitalize">
                  {task.type.replace('_', ' ')}
                </Typography>
                <Typography fontSize={11} color="text.secondary">
                  {new Date(task.timestamp).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default TasksMain;
