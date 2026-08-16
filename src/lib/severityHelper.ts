import type { SeverityLevel } from "../constants/severityLevels";

export const getSeverityLevel = (confidence: number): SeverityLevel => {
  if (confidence >= 0.85) return "High";
  if (confidence >= 0.70) return "Medium";
  if (confidence >= 0.60) return "Low";
  return "Uncertain";
};

export const getSeverityColor = (level: string): string => {
  switch (level) {
    case "High":   return "#ef5350";
    case "Medium": return "#ff9800";
    case "Low":    return "#4caf50";
    default:       return "#90a4ae";
  }
};
