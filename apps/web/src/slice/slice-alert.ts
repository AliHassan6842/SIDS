import { createSlice, createAction, type PayloadAction } from "@reduxjs/toolkit";
import type { IAlert, IAlertSettings } from "../types/alert/alert";

interface AlertState {
  list: IAlert[]; settings: IAlertSettings | null;
  loading: boolean; error: string | null; unreadCount: number;
}
const initialState: AlertState = {
  list: [], settings: null, loading: false, error: null, unreadCount: 0,
};
export const actionGetAlerts = createAction("alert");
export const actionMarkAllRead = createAction("alert/readAll");
export const alertSlice = createSlice({
  name: "alert",
  initialState,
  reducers: {
    actionSetAlerts(state, action: PayloadAction<IAlert[]>) {
      state.list = action.payload;
      state.unreadCount = action.payload.filter((a) => !a.IsRead).length;
    },
    actionSetAlertLoading(state, action: PayloadAction<boolean>) { state.loading = action.payload; },
    actionSetAlertSettings(state, action: PayloadAction<IAlertSettings>) { state.settings = action.payload; },
    actionMarkAlertReadLocal(state, action: PayloadAction<number>) {
      const alert = state.list.find((a) => a.AlertID === action.payload);
      if (alert) { alert.IsRead = true; state.unreadCount = Math.max(0, state.unreadCount - 1); }
    },
  },
});
export const { actionSetAlerts, actionSetAlertLoading, actionSetAlertSettings, actionMarkAlertReadLocal } = alertSlice.actions;
export default alertSlice.reducer;
