import { useAppDispatch, useAppSelector } from "./useStoreData";
import { actionAnalyzePestImage, actionGetDetectionHistory } from "../slice/slice-pest";

export const useDetection = () => {
  const dispatch = useAppDispatch();
  const { list, currentResult, loading, analyzeLoading } = useAppSelector((s) => s.pest);

  const analyzeImage = (file: File, fieldId: number, cropType: string) => {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("fieldId", String(fieldId));
    formData.append("cropType", cropType);
    dispatch(actionAnalyzePestImage(formData));
  };

  const fetchHistory = (filters?: Record<string, any>) => {
    dispatch(actionGetDetectionHistory(filters));
  };

  return { list, currentResult, loading, analyzeLoading, analyzeImage, fetchHistory };
};
