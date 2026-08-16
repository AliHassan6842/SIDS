export type AlertSeverity = "High" | "Medium" | "Low";

export interface IAlert {
  AlertID: number;
  Title: string;
  Message: string;
  FieldName: string;
  PestName: string;
  Severity: AlertSeverity;
  IsRead: boolean;
  CreatedAt: string;
  DetectionID?: number;
}

export interface IAlertSettings {
  EmailAlerts: boolean;
  SMSAlerts: boolean;
  InAppAlerts: boolean;
  WeeklySummary: boolean;
  ConfidenceThreshold: number;
}
