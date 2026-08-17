import { runtimeConfig } from "../config/runtimeConfig";

const getToken = (): string | null => {
  try { return localStorage.getItem("agrosense_token"); }
  catch { return null; }
};

// MOCK DATA GENERATORS
const getMockData = (path: string) => {
  const url = path.split('?')[0];
  
  if (url === "/api/Detection") {
    return {
      data: [
        { DetectionID: 101, FieldID: 1, FieldName: "South Farm A", CropType: "Wheat", PestDetected: { PestID: 1, PestName: "Aphids", ScientificName: "Aphis gossypii" }, ConfidenceScore: 0.92, SeverityLevel: "High", AffectedAreaPercent: 15, DetectedAt: new Date().toISOString(), Status: "Pending" },
        { DetectionID: 102, FieldID: 2, FieldName: "North Field B", CropType: "Cotton", PestDetected: { PestID: 2, PestName: "Whitefly", ScientificName: "Bemisia tabaci" }, ConfidenceScore: 0.85, SeverityLevel: "Medium", AffectedAreaPercent: 8, DetectedAt: new Date(Date.now() - 86400000).toISOString(), Status: "Treated" },
      ],
      totalCount: 2
    };
  }
  
  if (url === "/api/Detection/analyze") {
    return {
      DetectionID: Math.floor(Math.random() * 1000) + 200,
      FieldID: 1, FieldName: "South Farm A", CropType: "Wheat",
      PestDetected: { PestID: 1, PestName: "Aphids", ScientificName: "Aphis gossypii" },
      ConfidenceScore: 0.89 + (Math.random() * 0.1),
      SeverityLevel: "High", AffectedAreaPercent: 12,
      DetectedAt: new Date().toISOString(), Status: "Pending"
    };
  }

  if (url === "/api/Field") {
    return {
      data: [
        { FieldID: 1, FieldName: "South Farm A", Location: "Multan, Punjab", CropType: "Wheat", SizeAcres: 12, HealthScore: 85, AlertLevel: "Safe", IsActive: true },
        { FieldID: 2, FieldName: "North Field B", Location: "Multan, Punjab", CropType: "Cotton", SizeAcres: 45, HealthScore: 62, AlertLevel: "Warning", IsActive: true },
        { FieldID: 3, FieldName: "East Wheat Plot", Location: "Multan, Punjab", CropType: "Wheat", SizeAcres: 16, HealthScore: 92, AlertLevel: "Safe", IsActive: true },
      ],
      totalCount: 3
    };
  }

  if (url === "/api/Alert") {
    return [
      { AlertID: 1, Title: "High Severity Aphids Detected", Message: "Aphids detected in South Farm A with 92% confidence.", FieldName: "South Farm A", PestName: "Aphids", Severity: "High", IsRead: false, CreatedAt: new Date().toISOString() },
      { AlertID: 2, Title: "Whitefly Warning", Message: "Neighboring farms reported whitefly. Monitor Cotton crops closely.", FieldName: "North Field B", PestName: "Whitefly", Severity: "Medium", IsRead: false, CreatedAt: new Date(Date.now() - 86400000).toISOString() },
    ];
  }

  if (url === "/api/Report/summary") {
    return {
      TotalDetectionsThisMonth: 28, MostCommonPest: "Aphids", MostAffectedField: "South Farm A", TreatmentSuccessRate: 91,
      MonthlyTrend: [], PestFrequency: []
    };
  }

  if (url === "/api/User/profile") {
    return {
      UserID: 1, FullName: "Umar Ali", Email: "farmer@agrosense.com", Phone: "+92-300-1234567",
      Role: "Farmer", FarmName: "Ali Farms & Agriculture", Location: "Multan, Punjab",
      TotalLandAcres: 73, PrimaryCrop: "Wheat", IsActive: true, CreatedAt: "2024-01-01T00:00:00Z",
      NotificationSettings: { Email: true, SMS: false, InApp: true }
    };
  }

  return {};
};

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

class API {
  private base: string;

  constructor() {
    this.base = runtimeConfig.IS_PROXY_REQUIRED
      ? runtimeConfig.GATEWAY_BASE
      : runtimeConfig.API_DIRECT_BASE;
  }

  private headers(isForm = false): HeadersInit {
    const token = getToken();
    const h: HeadersInit = {};
    if (token) h["Authorization"] = `Bearer ${token}`;
    if (!isForm) h["Content-Type"] = "application/json";
    return h;
  }

  private async interceptMock(path: string, body?: any) {
    console.log(`[MOCK API] Intercepted request to ${path}`);
    await delay(600); // Simulate network latency
    return getMockData(path);
  }

  async get(path: string) {
    return this.interceptMock(path);
  }

  async post(path: string, body: unknown) {
    return this.interceptMock(path, body);
  }

  async put(path: string, body: unknown) {
    return this.interceptMock(path, body);
  }

  async delete(path: string) {
    return this.interceptMock(path);
  }

  async getArray(path: string): Promise<any[]> {
    const data = await this.interceptMock(path);
    return Array.isArray(data) ? data : [];
  }

  async postForm(path: string, formData: FormData) {
    return this.interceptMock(path);
  }
}

export default API;
