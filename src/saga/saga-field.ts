import { call, put, takeEvery } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { IField } from "../types/field/field";
import {
  actionGetFields, actionUpsertField, actionDeleteField,
  actionSetFields, actionSetFieldLoading, actionSetFieldSaveLoading,
  actionSetFieldError, actionSetFieldSuccess, actionUpsertFieldLocal, actionRemoveField,
} from "../slice/slice-field";
import { apiGetFields, apiUpsertField, apiDeleteField } from "../api/api-field";
import { showAlert } from "../slice/slice-alert-global";

function* fetchFields(action: PayloadAction<Record<string, any> | undefined>): SagaIterator {
  try {
    yield put(actionSetFieldLoading(true));
    const res = yield call(apiGetFields, action.payload);
    yield put(actionSetFields(res));
  } catch (e: any) {
    yield put(actionSetFieldError(e.message ?? "Failed to load fields"));
  } finally { yield put(actionSetFieldLoading(false)); }
}

function* upsertField(action: PayloadAction<Partial<IField>>): SagaIterator {
  try {
    yield put(actionSetFieldSaveLoading(true));
    const res: IField = yield call(apiUpsertField, action.payload);
    yield put(actionUpsertFieldLocal(res));
    const msg = action.payload.FieldID ? "Field updated" : "Field created";
    yield put(actionSetFieldSuccess(msg));
    yield put(showAlert({ message: msg, severity: "success" }));
  } catch (e: any) {
    yield put(showAlert({ message: e.message ?? "Save failed", severity: "error" }));
  } finally { yield put(actionSetFieldSaveLoading(false)); }
}

function* deleteField(action: PayloadAction<number>): SagaIterator {
  try {
    yield call(apiDeleteField, action.payload);
    yield put(actionRemoveField(action.payload));
    yield put(showAlert({ message: "Field deleted", severity: "success" }));
  } catch (e: any) {
    yield put(showAlert({ message: e.message ?? "Delete failed", severity: "error" }));
  }
}

export const sagaField = [
  takeEvery(actionGetFields.type, fetchFields),
  takeEvery(actionUpsertField.type, upsertField),
  takeEvery(actionDeleteField.type, deleteField),
];
