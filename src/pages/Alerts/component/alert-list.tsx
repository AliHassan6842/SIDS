import React, { useEffect } from "react";
import { Box, Card, CardContent, Typography, Chip, Button, Switch, FormControlLabel } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { actionGetAlerts, actionMarkAllRead } from "../../../slice/slice-alert";

const SEVERITY_STYLES: Record<string, any> = {
  High:   { bg: "rgba(239,83,80,0.08)", border: "rgba(239,83,80,0.25)", icon: "!" },
  Medium: { bg: "rgba(255,152,0,0.08)", border: "rgba(255,152,0,0.25)",  icon: "!" },
  Low:    { bg: "rgba(76,175,80,0.08)", border: "rgba(76,175,80,0.25)",  icon: "!" },
};

const AlertList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { list, loading, unreadCount } = useAppSelector((s) => s.alert);

  useEffect(() => { dispatch(actionGetAlerts()); }, [dispatch]);

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={700}>Alerts & Notifications</Typography>
          <Typography variant="body2" color="text.secondary">{unreadCount} active alerts require your attention</Typography>
        </Box>
        <Button variant="outlined" size="small" onClick={() => dispatch(actionMarkAllRead())}>Mark All Read</Button>
      </Box>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
        {loading && <Typography color="text.secondary">Loading alerts...</Typography>}
        {list.length === 0 && !loading && (
          <Card><CardContent><Typography color="text.secondary" textAlign="center">No active alerts </Typography></CardContent></Card>
        )}
        {list.map((alert) => {
          const style = SEVERITY_STYLES[alert.Severity] ?? SEVERITY_STYLES.Low;
          return (
            <Card key={alert.AlertID} sx={{ border: `1px solid ${style.border}`, bgcolor: style.bg, opacity: alert.IsRead ? 0.6 : 1 }}>
              <CardContent sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
                <Box sx={{ width: 38, height: 38, borderRadius: "10px", bgcolor: style.border, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0 }}>{style.icon}</Box>
                <Box sx={{ flex: 1 }}>
                  <Typography fontSize={13} fontWeight={600}>{alert.Title}</Typography>
                  <Typography fontSize={12} color="text.secondary">{alert.Message}</Typography>
                  <Typography fontSize={11} color="text.disabled" mt={0.5}>{new Date(alert.CreatedAt).toLocaleString()} · {alert.PestName}</Typography>
                </Box>
                <Chip label={alert.Severity} size="small" sx={{ fontSize: 10 }} />
              </CardContent>
            </Card>
          );
        })}
      </Box>
    </Box>
  );
};

export default AlertList;

