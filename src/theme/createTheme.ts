import { createTheme } from "@mui/material/styles";
import { agroSenseDarkPalette, agroSenseLightPalette } from "./defaultTheme";

export const getAppTheme = (mode: "light" | "dark") => {
  const palette = mode === "light" ? agroSenseLightPalette : agroSenseDarkPalette;

  return createTheme({
    palette: {
      mode,
      primary: { main: palette.primary, dark: palette.primaryDark, light: palette.primaryLight },
      secondary: { main: palette.gold },
      error: { main: palette.high },
      warning: { main: palette.medium },
      success: { main: palette.primary },
      background: { default: palette.bg, paper: palette.bg2 },
      text: { primary: palette.textPrimary, secondary: palette.textSecondary, disabled: palette.textDisabled },
      divider: palette.border,
    },
    typography: {
      fontFamily: "'Inter', sans-serif",
      h1: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800 },
      h2: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 },
      h3: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 },
      h4: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 },
      h5: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 },
      h6: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 },
      body1: { fontSize: "0.875rem" },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiCard: {
        styleOverrides: {
          root: { background: palette.surface, border: `1px solid ${palette.border}`, backdropFilter: "blur(10px)" },
        },
      },
      MuiButton: {
        styleOverrides: {
          containedPrimary: {
            background: `linear-gradient(135deg, ${palette.primaryDark}, ${palette.primary})`,
            "&:hover": { boxShadow: "0 8px 25px rgba(76,175,80,0.4)", transform: "translateY(-1px)" },
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: { background: palette.bg2, borderRight: `1px solid ${palette.border}` },
        },
      },
      MuiAppBar: {
        styleOverrides: { root: { background: mode === "light" ? "rgba(255,255,255,0.9)" : "rgba(6,14,24,0.9)", backdropFilter: "blur(20px)", borderBottom: `1px solid ${palette.border}` } },
      },
    },
  });
};
