import React, { useState } from "react";
import { Box, Card, CardContent, Typography, Button, CircularProgress } from "@mui/material";
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useTheme } from "@mui/material";
import { enqueueTask } from "../../../slice/slice-sync";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";

const DetectionUpload: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { isOffline } = useAppSelector(s => s.sync);
  
  const [isCapturing, setIsCapturing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [queued, setQueued] = useState(false);

  const handleCapture = () => {
    setIsCapturing(true);
    
    if (isOffline) {
      setTimeout(() => {
        setIsCapturing(false);
        dispatch(enqueueTask({ type: "quick_scan", payload: { field: "Field A", crop: "Cotton" } }));
        setQueued(true);
      }, 1000);
      return;
    }

    // Simulate AI processing
    setTimeout(() => {
      setIsCapturing(false);
      setResult({
        diagnosis: "Cotton Whitefly",
        confidence: "92%",
        observed: 14,
        reason: "Characteristic white wings and typical leaf underside grouping detected."
      });
    }, 1500);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", pb: 10 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CameraAltIcon sx={{ color: "primary.main" }} /> Guided Scan
      </Typography>
      
      {!result && !queued ? (
        <>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Cotton - Field A
          </Typography>
          
          <Box sx={{ 
            mt: 2, 
            mb: 2, 
            height: 350, 
            bgcolor: '#000', 
            borderRadius: 3, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Simulated Camera Viewfinder Frame */}
            <Box sx={{ position: 'absolute', inset: 20, border: '2px solid rgba(255,255,255,0.3)', borderRadius: 2 }}>
              {/* Corner brackets */}
              <Box sx={{ position: 'absolute', top: -2, left: -2, width: 20, height: 20, borderTop: '4px solid #fff', borderLeft: '4px solid #fff' }} />
              <Box sx={{ position: 'absolute', top: -2, right: -2, width: 20, height: 20, borderTop: '4px solid #fff', borderRight: '4px solid #fff' }} />
              <Box sx={{ position: 'absolute', bottom: -2, left: -2, width: 20, height: 20, borderBottom: '4px solid #fff', borderLeft: '4px solid #fff' }} />
              <Box sx={{ position: 'absolute', bottom: -2, right: -2, width: 20, height: 20, borderBottom: '4px solid #fff', borderRight: '4px solid #fff' }} />
            </Box>
            
            <Typography color="rgba(255,255,255,0.5)">[ Live Camera Feed ]</Typography>
            
            {isCapturing && (
              <Box sx={{ position: 'absolute', inset: 0, bgcolor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <CircularProgress color="primary" />
                <Typography color="white" mt={2}>Analyzing image...</Typography>
              </Box>
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3, color: theme.palette.success.main, justifyContent: 'center' }}>
            <CheckCircleIcon fontSize="small" />
            <Typography fontWeight={600}>light good</Typography>
          </Box>

          <Button 
            variant="contained" 
            fullWidth 
            size="large"
            disabled={isCapturing}
            onClick={handleCapture}
            sx={{ py: 2, fontSize: 16, fontWeight: 700, borderRadius: 3 }}
          >
            CAPTURE
          </Button>
        </>
      ) : queued ? (
        <Card sx={{ mt: 2, borderRadius: 3, border: `1px solid ${theme.palette.warning.main}`, bgcolor: `${theme.palette.warning.main}15` }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" fontWeight={800} gutterBottom>
              Saved Offline
            </Typography>
            <Typography color="text.secondary" mb={3}>
              You are currently offline. This scan has been added to your queue and will be processed when you reconnect.
            </Typography>
            <Button variant="contained" fullWidth onClick={() => setQueued(false)} sx={{ py: 1.5, fontWeight: 700 }}>
              Scan Another
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card sx={{ mt: 2, borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
          <CardContent sx={{ p: '24px !important' }}>
            <Typography variant="h5" fontWeight={800} color="error.main" gutterBottom>
              {result.diagnosis}
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Box>
                <Typography fontSize={12} color="text.secondary" textTransform="uppercase">Confidence</Typography>
                <Typography fontWeight={700}>High {result.confidence}</Typography>
              </Box>
              <Box>
                <Typography fontSize={12} color="text.secondary" textTransform="uppercase">Observed</Typography>
                <Typography fontWeight={700}>{result.observed} in sample</Typography>
              </Box>
            </Box>

            <Box sx={{ p: 2, bgcolor: `${theme.palette.primary.main}10`, borderRadius: 2, mb: 3 }}>
              <Typography fontSize={13} fontWeight={600} gutterBottom>Why SIDS thinks this</Typography>
              <Typography fontSize={13} color="text.secondary">{result.reason}</Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Button 
                variant="outlined" 
                fullWidth 
                startIcon={<MenuBookIcon />}
                sx={{ py: 1.5, fontWeight: 600, borderRadius: 2 }}
              >
                Evidence
              </Button>

              <Button 
                variant="contained" 
                fullWidth 
                endIcon={<ArrowForwardIcon />}
                sx={{ py: 1.5, fontWeight: 700, borderRadius: 2 }}
                onClick={() => setResult(null)}
              >
                Next: Start Field Survey
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DetectionUpload;
