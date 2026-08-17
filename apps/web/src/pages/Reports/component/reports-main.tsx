import React, { useEffect } from "react";
import { Box, Typography, Grid, Card, CardContent } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../../hooks/useStoreData";
import { actionGetReportSummary } from "../../../slice/slice-report";

const ReportsMain: React.FC = () => {
  const dispatch = useAppDispatch();
  const { summary, loading } = useAppSelector((s) => s.report);
  useEffect(() => { dispatch(actionGetReportSummary(undefined)); }, [dispatch]);
  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>Analytics & Reports</Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>Insights and trends across all your farm fields</Typography>
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {[
          { label: "Total Detections (Month)", value: summary?.TotalDetectionsThisMonth ?? 47, color: "#81c784" },
          { label: "Most Common Pest",        value: summary?.MostCommonPest ?? "Aphids",  color: "#ef9a9a" },
          { label: "Most Affected Field",     value: summary?.MostAffectedField ?? "South Farm A", color: "#ffe082" },
          { label: "Treatment Success Rate",  value: `${summary?.TreatmentSuccessRate ?? 91}%`, color: "#80deea" },
        ].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item.label}>
            <Card sx={{ textAlign: "center", p: 1 }}>
              <CardContent>
                <Typography fontSize={28} fontWeight={800} sx={{ color: item.color }}>{item.value}</Typography>
                <Typography fontSize={11} color="text.secondary">{item.label}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Card sx={{ mt: 2.5 }}>
        <CardContent>
          <Typography fontWeight={600} gutterBottom>Monthly Detection Trend</Typography>
          <Box sx={{ display: "flex", alignItems: "flex-end", gap: 1.5, height: 140, pt: 2 }}>
            {[18, 24, 31, 22, 38, 47].map((val, i) => (
              <Box key={i} sx={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 0.5 }}>
                <Typography fontSize={10} color="text.secondary">{val}</Typography>
                <Box sx={{ width: "100%", height: `${(val / 50) * 100}%`, background: "linear-gradient(180deg,#4caf50,#2e7d32)", borderRadius: "6px 6px 0 0" }} />
                <Typography fontSize={10} color="text.disabled">{["Mar","Apr","May","Jun","Jul","Aug"][i]}</Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
export default ReportsMain;

