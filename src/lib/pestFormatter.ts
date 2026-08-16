import type { IDetectionResult } from "../types/pest/pest";

export const formatConfidence = (score: number): string =>
  `${(score * 100).toFixed(1)}%`;

export const formatPestResult = (result: IDetectionResult) => ({
  ...result,
  ConfidenceDisplay: formatConfidence(result.ConfidenceScore),
  DetectedAtDisplay: new Date(result.DetectedAt).toLocaleString(),
});
