import { createSlice, createAction, type PayloadAction } from "@reduxjs/toolkit";
import type { IDetectionResult } from "../types/pest/pest";
import { normalizeListPayload } from "../lib/safeArray";

interface PestState {
  list: { data: IDetectionResult[]; totalCount: number };
  currentResult: IDetectionResult | null;
  loading: boolean;
  analyzeLoading: boolean;
  saveLoading: boolean;
  error: string | null;
  success: string | null;
}
const initialState: PestState = {
  list: { data: [], totalCount: 0 },
  currentResult: null, loading: false, analyzeLoading: false,
  saveLoading: false, error: null, success: null,
};

export const actionGetDetectionHistory = createAction<Record<string, any> | undefined>("pest");
export const actionAnalyzePestImage = createAction<FormData>("pest/analyze");
export const actionDeleteDetection = createAction<number>("pest/delete");

const pestSlice = createSlice({
  name: "pest",
  initialState,
  reducers: {
    actionSetDetectionHistory(state, action: PayloadAction<any>) {
      state.list = {
        data: normalizeListPayload<IDetectionResult>(action.payload?.data ?? action.payload),
        totalCount: action.payload?.totalCount ?? 0,
      };
    },
    actionSetCurrentResult(state, action: PayloadAction<IDetectionResult | null>) { state.currentResult = action.payload; },
    actionSetPestLoading(state, action: PayloadAction<boolean>) { state.loading = action.payload; },
    actionSetAnalyzeLoading(state, action: PayloadAction<boolean>) { state.analyzeLoading = action.payload; },
    actionSetPestSaveLoading(state, action: PayloadAction<boolean>) { state.saveLoading = action.payload; },
    actionSetPestError(state, action: PayloadAction<string | null>) { state.error = action.payload; },
    actionSetPestSuccess(state, action: PayloadAction<string | null>) { state.success = action.payload; },
    actionRemoveDetection(state, action: PayloadAction<number>) {
      state.list.data = state.list.data.filter((d) => d.DetectionID !== action.payload);
    },
  },
});
export const {
  actionSetDetectionHistory, actionSetCurrentResult, actionSetPestLoading, actionSetAnalyzeLoading,
  actionSetPestSaveLoading, actionSetPestError, actionSetPestSuccess, actionRemoveDetection,
} = pestSlice.actions;
export default pestSlice.reducer;
