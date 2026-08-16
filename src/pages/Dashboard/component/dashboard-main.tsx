import React from "react";
import { Box, Typography, Button, Card, CardContent } from "@mui/material";
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import LandscapeIcon from "@mui/icons-material/Landscape";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@mui/material";

const DashboardMain: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", pb: 10 }}>
      <Typography variant="h4" fontWeight={800} gutterBottom>
        Good morning
      </Typography>

      <Card sx={{ bgcolor: `${theme.palette.error.main}15`, border: `1px solid ${theme.palette.error.main}40`, mb: 4, borderRadius: 3 }}>
        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, p: '16px !important' }}>
          <ErrorOutlineIcon color="error" />
          <Typography fontWeight={600} color="error.dark">
            1 field needs attention
          </Typography>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mb: 4 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<CameraAltIcon />}
          onClick={() => navigate('/scan')}
          sx={{ py: 2, fontSize: 16, fontWeight: 700, borderRadius: 3 }}
        >
          QUICK SCAN
        </Button>

        <Button
          variant="contained"
          color="secondary"
          size="large"
          startIcon={<LandscapeIcon />}
          onClick={() => navigate('/survey')}
          sx={{ py: 2, fontSize: 16, fontWeight: 700, borderRadius: 3 }}
        >
          FIELD SURVEY
        </Button>
      </Box>

      <Card sx={{ mb: 2, borderRadius: 3, bgcolor: theme.palette.background.paper }}>
        <CardContent sx={{ p: '16px !important' }}>
          <Typography fontSize={13} color="text.secondary" textTransform="uppercase" gutterBottom>
            Next action
          </Typography>
          <Typography fontWeight={600}>
            Rescout Field A
          </Typography>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3, bgcolor: theme.palette.background.paper, cursor: 'pointer' }} onClick={() => navigate('/tasks')}>
        <CardContent sx={{ p: '16px !important', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography fontSize={13} color="text.secondary" textTransform="uppercase" gutterBottom>
              Status
            </Typography>
            <Typography fontWeight={600}>
              Offline: 2 items queued
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardMain;
