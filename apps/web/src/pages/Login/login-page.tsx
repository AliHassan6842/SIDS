import React, { useState } from "react";
import { Box, TextField, Button, Typography, CircularProgress, useTheme } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { setToken } from "../../auth/tokenStore";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [email, setEmail] = useState("farmer@agrosense.com");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1200));
    setToken("demo-agrosense-token-2026");
    setLoading(false);
    navigate("/dashboard");
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", bgcolor: "background.default", position: "relative", overflow: "hidden" }}>
      <Box sx={{ position: "absolute", width: 600, height: 600, background: `radial-gradient(circle, ${theme.palette.primary.main}25 0%, transparent 70%)`, top: -100, left: -100, pointerEvents: "none" }} />
      <Box sx={{ flex: 1, display: { xs: "none", md: "flex" }, alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 4, p: 8 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Box sx={{ width: 56, height: 56, borderRadius: "14px", background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, color: "#fff", boxShadow: `0 0 30px ${theme.palette.primary.main}40` }}>{String.fromCodePoint(0x1f33f)}</Box>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ color: "text.primary" }}>AgroSense</Typography>
            <Typography variant="caption" color="text.secondary" letterSpacing={1} textTransform="uppercase">Intelligent Farm Advisory</Typography>
          </Box>
        </Box>
        <Box sx={{ maxWidth: 420, textAlign: "center" }}>
          <Typography variant="h3" fontWeight={800} lineHeight={1.2} mb={2} color="text.primary">Protect Your Crops with <Box component="span" sx={{ color: "primary.main" }}>AI-Powered</Box> Detection</Typography>
          <Typography color="text.secondary" lineHeight={1.7}>Upload a field photo, detect pests instantly, and receive expert treatment recommendations — all in one platform.</Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap", justifyContent: "center" }}>
          {[{i:0x1f3af,t:" Computer Vision"}, {i:0x1f9e0,t:" AI Advisory"}, {i:0x1f514,t:" Real-time Alerts"}, {i:0x1f4ca,t:" Analytics"}].map((f, idx) => (
            <Box key={idx} sx={{ px: 2, py: 0.8, borderRadius: "50px", bgcolor: `${theme.palette.primary.main}15`, border: `1px solid ${theme.palette.primary.main}30`, fontSize: 13, color: "primary.main", fontWeight: 600 }}>{String.fromCodePoint(f.i) + f.t}</Box>
          ))}
        </Box>
      </Box>
      <Box sx={{ width: { xs: "100%", md: 460 }, display: "flex", alignItems: "center", justifyContent: "center", p: 4, bgcolor: "background.paper", borderLeft: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ width: "100%", maxWidth: 380 }}>
          <Typography variant="h5" fontWeight={700} mb={0.5} color="text.primary">Welcome Back {String.fromCodePoint(0x1f44b)}</Typography>
          <Typography color="text.secondary" fontSize={14} mb={3.5}>Sign in to your AgroSense dashboard</Typography>
          <TextField label="Email Address" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth size="small" sx={{ mb: 2 }} />
          <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth size="small" sx={{ mb: 2.5 }} />
          <Button fullWidth variant="contained" size="large" onClick={handleLogin} disabled={loading} startIcon={loading ? <CircularProgress size={16} color="inherit" /> : undefined} sx={{ py: 1.4, fontSize: 15, fontWeight: 600 }}>
            {loading ? "Signing in..." : "Sign In to Dashboard"}
          </Button>
          <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={2.5}>Don't have an account? <Box component="span" sx={{ color: "primary.main", cursor: "pointer", fontWeight: 600 }}>Register your Farm</Box></Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default LoginPage;
