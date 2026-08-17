export const normalizeListPayload = <T>(data: any): T[] => {
  if (Array.isArray(data)) return data as T[];
  if (data && Array.isArray(data.data)) return data.data as T[];
  return [];
};
