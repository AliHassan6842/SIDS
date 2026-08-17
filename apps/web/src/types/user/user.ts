export interface IUser {
  UserID: number;
  FullName: string;
  Email: string;
  Phone: string;
  Role: "Farmer" | "Admin";
  FarmName: string;
  Location: string;
  TotalLandAcres: number;
  PrimaryCrop: string;
  IsActive: boolean;
  CreatedAt: string;
}

export interface IUserProfile extends IUser {
  NotificationSettings: {
    Email: boolean;
    SMS: boolean;
    InApp: boolean;
  };
}
