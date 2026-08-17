import React, { useMemo, useEffect, useState } from "react";
import { ThemeProvider as MuiThemeProvider, CssBaseline } from "@mui/material";
import { getAppTheme } from "./createTheme";
import { useAppSelector } from "../hooks/useStoreData";

interface Props { children: React.ReactNode; }

const ThemeProvider: React.FC<Props> = ({ children }) => {
  const mode = useAppSelector((state) => state.theme.mode);
  const [systemMode, setSystemMode] = useState<"light" | "dark">("light");

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    setSystemMode(mql.matches ? "dark" : "light");
    
    const handler = (e: MediaQueryListEvent) => setSystemMode(e.matches ? "dark" : "light");
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  const activeMode = mode === "system" ? systemMode : mode;
  
  const theme = useMemo(() => getAppTheme(activeMode), [activeMode]);

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
};

export default ThemeProvider;
