import React from "react";
import { Box, Typography, Button } from "@mui/material";
interface State { hasError: boolean; error: Error | null; }
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  constructor(props: any) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error: Error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) return (
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", gap: 2 }}>
        <Typography variant="h4">Warning: Something went wrong</Typography>
        <Typography color="text.secondary">{this.state.error?.message}</Typography>
        <Button variant="contained" onClick={() => window.location.reload()}>Reload</Button>
      </Box>
    );
    return this.props.children;
  }
}
export default ErrorBoundary;

