import { createSlice, createAction, type PayloadAction } from "@reduxjs/toolkit";
import type { IField } from "../types/field/field";
import { normalizeListPayload } from "../lib/safeArray";

interface FieldState {
  list: { data: IField[]; totalCount: number };
  loading: boolean; saveLoading: boolean;
  error: string | null; success: string | null;
}
const initialState: FieldState = {
  list: { data: [], totalCount: 0 }, loading: false, saveLoading: false, error: null, success: null,
};

export const actionGetFields = createAction<Record<string, any> | undefined>("field");
export const actionUpsertField = createAction<Partial<IField>>("field/upsert");
export const actionDeleteField = createAction<number>("field/delete");

const fieldSlice = createSlice({
  name: "field",
  initialState,
  reducers: {
    actionSetFields(state, action: PayloadAction<any>) {
      state.list = {
        data: normalizeListPayload<IField>(action.payload?.data ?? action.payload),
        totalCount: action.payload?.totalCount ?? 0,
      };
    },
    actionSetFieldLoading(state, action: PayloadAction<boolean>) { state.loading = action.payload; },
    actionSetFieldSaveLoading(state, action: PayloadAction<boolean>) { state.saveLoading = action.payload; },
    actionSetFieldError(state, action: PayloadAction<string | null>) { state.error = action.payload; },
    actionSetFieldSuccess(state, action: PayloadAction<string | null>) { state.success = action.payload; },
    actionUpsertFieldLocal(state, action: PayloadAction<IField>) {
      const idx = state.list.data.findIndex((f) => f.fieldId === action.payload.fieldId);
      if (idx >= 0) state.list.data[idx] = action.payload;
      else state.list.data.unshift(action.payload);
    },
    actionRemoveField(state, action: PayloadAction<number>) {
      state.list.data = state.list.data.filter((f) => f.fieldId !== action.payload);
    },
  },
});
export const {
  actionSetFields, actionSetFieldLoading, actionSetFieldSaveLoading,
  actionSetFieldError, actionSetFieldSuccess, actionUpsertFieldLocal, actionRemoveField,
} = fieldSlice.actions;
export default fieldSlice.reducer;
