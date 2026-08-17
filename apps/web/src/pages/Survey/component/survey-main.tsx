import React, { useState } from "react";
import { Box, Typography, Button, Card, CardContent, LinearProgress, Grid } from "@mui/material";
import MapIcon from "@mui/icons-material/Map";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { enqueueTask } from "../../../slice/slice-sync";

const TOTAL_SAMPLES = 20;

const SurveyMain: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isOffline } = useAppSelector(s => s.sync);
  
  const [step, setStep] = useState<"setup" | "tracking" | "result" | "queued">("setup");
  const [samples, setSamples] = useState<{ id: number, status: "healthy" | "affected" | null }[]>(
    Array.from({ length: TOTAL_SAMPLES }, (_, i) => ({ id: i + 1, status: null }))
  );

  const currentSampleIndex = samples.findIndex(s => s.status === null);
  const isComplete = currentSampleIndex === -1;
  const currentSampleNumber = isComplete ? TOTAL_SAMPLES : currentSampleIndex + 1;
  
  const healthyCount = samples.filter(s => s.status === "healthy").length;
  const affectedCount = samples.filter(s => s.status === "affected").length;
  const progress = ((healthyCount + affectedCount) / TOTAL_SAMPLES) * 100;

  const handleRecord = (status: "healthy" | "affected") => {
    if (isComplete) return;
    const newSamples = [...samples];
    newSamples[currentSampleIndex].status = status;
    setSamples(newSamples);
    if (currentSampleIndex === TOTAL_SAMPLES - 1) {
      if (isOffline) {
        dispatch(enqueueTask({ type: "field_survey", payload: { healthy: healthyCount, affected: affectedCount + (status === "affected" ? 1 : 0) } }));
        setStep("queued");
      } else {
        setStep("result");
      }
    }
  };

  const incidence = (affectedCount / TOTAL_SAMPLES) * 100;
  let statusText = "Normal";
  let statusColor = theme.palette.success.main;
  if (incidence > 20) { statusText = "Threshold Reached - Action Required"; statusColor = theme.palette.error.main; }
  else if (incidence > 5) { statusText = "Monitor Closely"; statusColor = theme.palette.warning.main; }

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", pb: 10 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/home')} sx={{ mr: 1, minWidth: 'auto', p: 1 }}>Back</Button>
        <Typography variant="h5" fontWeight={700} sx={{ flex: 1 }}>Field Survey</Typography>
      </Box>

      {step === "setup" && (
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <MapIcon sx={{ fontSize: 64, color: 'primary.main', opacity: 0.8, mb: 2 }} />
              <Typography variant="h6" fontWeight={700}>Standard Protocol</Typography>
              <Typography color="text.secondary">20 geographically distributed samples</Typography>
            </Box>
            
            <Typography variant="body2" sx={{ mb: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
              Walk in a W-pattern across the field. Stop at 20 distinct points and inspect a plant at each point.
            </Typography>

            <Button variant="contained" fullWidth size="large" onClick={() => setStep("tracking")} sx={{ py: 1.5, fontWeight: 700 }}>
              Start Tracking
            </Button>
          </CardContent>
        </Card>
      )}

      {step === "tracking" && (
        <Box>
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography fontWeight={600}>Sample {currentSampleNumber} of {TOTAL_SAMPLES}</Typography>
                <Typography variant="body2" color="text.secondary">{Math.round(progress)}% Complete</Typography>
              </Box>
              <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
              
              <Grid container spacing={2} sx={{ mt: 2, textAlign: 'center' }}>
                <Grid item xs={6}>
                  <Typography fontSize={24} fontWeight={800} color="success.main">{healthyCount}</Typography>
                  <Typography variant="caption" color="text.secondary" textTransform="uppercase">Healthy</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography fontSize={24} fontWeight={800} color="error.main">{affectedCount}</Typography>
                  <Typography variant="caption" color="text.secondary" textTransform="uppercase">Affected</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Typography variant="subtitle1" fontWeight={600} textAlign="center" mb={2}>
            Inspect plant #{currentSampleNumber}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Button 
                variant="outlined" 
                color="error" 
                fullWidth 
                sx={{ height: 120, display: 'flex', flexDirection: 'column', gap: 1, borderRadius: 3, border: `2px solid ${theme.palette.error.main}` }}
                onClick={() => handleRecord("affected")}
              >
                <CancelIcon sx={{ fontSize: 32 }} />
                <Typography fontWeight={700}>AFFECTED</Typography>
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button 
                variant="outlined" 
                color="success" 
                fullWidth 
                sx={{ height: 120, display: 'flex', flexDirection: 'column', gap: 1, borderRadius: 3, border: `2px solid ${theme.palette.success.main}` }}
                onClick={() => handleRecord("healthy")}
              >
                <CheckCircleIcon sx={{ fontSize: 32 }} />
                <Typography fontWeight={700}>HEALTHY</Typography>
              </Button>
            </Grid>
          </Grid>
        </Box>
      )}

      {step === "queued" && (
        <Card sx={{ mt: 2, borderRadius: 3, border: `1px solid ${theme.palette.warning.main}`, bgcolor: `${theme.palette.warning.main}15` }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Saved Offline
            </Typography>
            <Typography color="text.secondary" mb={3}>
              You are currently offline. This survey has been added to your queue and will be processed when you reconnect.
            </Typography>
            <Button variant="contained" fullWidth onClick={() => navigate('/home')} sx={{ py: 1.5, fontWeight: 700 }}>
              Return Home
            </Button>
          </CardContent>
        </Card>
      )}

      {step === "result" && (
        <Card sx={{ borderRadius: 3, border: `2px solid ${statusColor}` }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="subtitle2" color="text.secondary" textTransform="uppercase" gutterBottom>
              Survey Complete
            </Typography>
            <Typography variant="h3" fontWeight={800} color={statusColor} gutterBottom>
              {incidence}%
            </Typography>
            <Typography fontWeight={600} gutterBottom>Incidence Rate</Typography>
            
            <Box sx={{ p: 2, bgcolor: `${statusColor}15`, borderRadius: 2, mt: 3, mb: 3 }}>
              <Typography fontWeight={700} color={statusColor}>{statusText}</Typography>
            </Box>

            <Grid container spacing={2} sx={{ mb: 4 }}>
              <Grid item xs={6}>
                <Typography fontSize={20} fontWeight={800} color="success.main">{healthyCount}</Typography>
                <Typography variant="caption" color="text.secondary" textTransform="uppercase">Healthy</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography fontSize={20} fontWeight={800} color="error.main">{affectedCount}</Typography>
                <Typography variant="caption" color="text.secondary" textTransform="uppercase">Affected</Typography>
              </Grid>
            </Grid>

            <Button variant="contained" fullWidth size="large" onClick={() => navigate('/home')} sx={{ py: 1.5, fontWeight: 700 }}>
              Done
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SurveyMain;
