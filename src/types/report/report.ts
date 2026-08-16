export interface IMonthlyTrend {
  Month: string;
  DetectionCount: number;
}

export interface IPestFrequency {
  PestName: string;
  Count: number;
  Percentage: number;
}

export interface IReportSummary {
  TotalDetectionsThisMonth: number;
  MostCommonPest: string;
  MostAffectedField: string;
  TreatmentSuccessRate: number;
  MonthlyTrend: IMonthlyTrend[];
  PestFrequency: IPestFrequency[];
}
