export const formatConfidence = (value: number | null): string =>
  value === null ? "Not available" : `${Math.round(value * 100)}%`;

export const formatDate = (value: string): string => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Date unavailable";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

export const humanizeCode = (value: string | null): string =>
  value ? value.toLowerCase().replace(/_/g, " ") : "No additional details";
