export interface IField {
  fieldId: number;
  fieldName: string;
  location: string;
  latitude?: number;
  longitude?: number;
  cropType: string;
  sizeAcres: number;
  plantingDate: string;
  healthScore: number;
  alertLevel: "Safe" | "Warning" | "Critical";
  lastScannedAt?: string;
  isActive: boolean;
}
