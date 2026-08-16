export interface IField {
  FieldID: number;
  FieldName: string;
  Location: string;
  Latitude?: number;
  Longitude?: number;
  CropType: string;
  SizeAcres: number;
  PlantingDate: string;
  HealthScore: number;
  AlertLevel: "Safe" | "Warning" | "Critical";
  LastScannedAt?: string;
  IsActive: boolean;
}
