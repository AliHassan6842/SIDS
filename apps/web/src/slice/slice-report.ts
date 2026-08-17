import { createSlice, createAction, type PayloadAction } from "@reduxjs/toolkit";
import type { IReportSummary } from "../types/report/report";

interface ReportState { summary: IReportSummary | null; loading: boolean; error: string | null; }
const initialState: ReportState = { summary: null, loading: false, error: null };
export const actionGetReportSummary = createAction<Record<string, any> | undefined>("report");
const reportSlice = createSlice({
  name: "report",
  initialState,
  reducers: {
    actionSetReportSummary(state, action: PayloadAction<IReportSummary>) { state.summary = action.payload; },
    actionSetReportLoading(state, action: PayloadAction<boolean>) { state.loading = action.payload; },
    actionSetReportError(state, action: PayloadAction<string | null>) { state.error = action.payload; },
  },
});
export const { actionSetReportSummary, actionSetReportLoading, actionSetReportError } = reportSlice.actions;
export default reportSlice.reducer;
