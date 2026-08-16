import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface GlobalAlertState {
  message: string | null;
  severity: "success" | "error" | "warning" | "info";
  open: boolean;
}
const initialState: GlobalAlertState = { message: null, severity: "info", open: false };

const alertGlobalSlice = createSlice({
  name: "alertGlobal",
  initialState,
  reducers: {
    showAlert(state, action: PayloadAction<{ message: string; severity: GlobalAlertState["severity"] }>) {
      state.message = action.payload.message;
      state.severity = action.payload.severity;
      state.open = true;
    },
    hideAlert(state) { state.open = false; },
  },
});

export const { showAlert, hideAlert } = alertGlobalSlice.actions;
export default alertGlobalSlice.reducer;
