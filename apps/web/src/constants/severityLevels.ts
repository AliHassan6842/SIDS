export const CONFIDENCE_THRESHOLD = 0.6;

export const SEVERITY_LEVELS = {
  High:      { label: "High",      color: "#ef5350", bg: "rgba(239,83,80,0.15)",   minConfidence: 0.85 },
  Medium:    { label: "Medium",    color: "#ff9800", bg: "rgba(255,152,0,0.15)",   minConfidence: 0.70 },
  Low:       { label: "Low",       color: "#4caf50", bg: "rgba(76,175,80,0.15)",   minConfidence: 0.60 },
  Uncertain: { label: "Uncertain", color: "#90a4ae", bg: "rgba(144,164,174,0.15)", minConfidence: 0.00 },
} as const;

export type SeverityLevel = keyof typeof SEVERITY_LEVELS;
