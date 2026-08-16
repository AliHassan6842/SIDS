export interface IPest {
  PestID: number;
  PestName: string;
  ScientificName: string;
  Category: string;
  Description: string;
  ImageUrl: string;
}

export interface IDetectionResult {
  DetectionID: number;
  FieldID: number;
  FieldName: string;
  CropType: string;
  PestDetected: IPest;
  ConfidenceScore: number;
  SeverityLevel: "High" | "Medium" | "Low" | "Uncertain";
  AffectedAreaPercent: number;
  DetectedAt: string;
  Status: "Pending" | "Treated";
  ImageUrl: string;
}

export interface IDetectionFilters {
  fromDate?: string;
  toDate?: string;
  fieldId?: number;
  severity?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}
