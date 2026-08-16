export interface ITreatmentProduct {
  ProductID: number;
  ProductName: string;
  ChemicalFormula: string;
  DosagePerLiter: string;
  ApplicationMethod: string;
  BestTimeToApply: string;
  FrequencyDays: number;
  Precautions: string;
  IsPrimary: boolean;
}

export interface ITreatmentStep {
  StepNumber: number;
  Title: string;
  Description: string;
}

export interface IAdvisory {
  AdvisoryID: number;
  DetectionID: number;
  PestName: string;
  ScientificName: string;
  SeverityLevel: string;
  FieldName: string;
  CropType: string;
  DetectedAt: string;
  TreatmentSteps: ITreatmentStep[];
  RecommendedProducts: ITreatmentProduct[];
  PreventionTips: string[];
}
