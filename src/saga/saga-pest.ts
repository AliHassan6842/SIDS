import { call, put, takeEvery } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import type { PayloadAction } from "@reduxjs/toolkit";
import {
  actionGetDetectionHistory, actionAnalyzePestImage, actionDeleteDetection,
  actionSetDetectionHistory, actionSetCurrentResult, actionSetPestLoading,
  actionSetAnalyzeLoading, actionSetPestSaveLoading, actionSetPestError,
  actionSetPestSuccess, actionRemoveDetection,
} from "../slice/slice-pest";
import { apiGetDetectionHistory, apiUploadPestImage, apiDeleteDetection } from "../api/api-pest";
import { showAlert } from "../slice/slice-alert-global";

function* fetchHistory(action: PayloadAction<Record<string, any> | undefined>): SagaIterator {
  try {
    yield put(actionSetPestLoading(true));
    const res = yield call(apiGetDetectionHistory, action.payload);
    yield put(actionSetDetectionHistory(res));
  } catch (e: any) {
    yield put(actionSetPestError(e.message ?? "Failed to fetch history"));
  } finally { yield put(actionSetPestLoading(false)); }
}

function* analyzeImage(action: PayloadAction<FormData>): SagaIterator {
  try {
    yield put(actionSetAnalyzeLoading(true));
    const result = yield call(apiUploadPestImage, action.payload);
    yield put(actionSetCurrentResult(result));
    yield put(actionSetPestSuccess("Pest analysis complete"));
    yield put(showAlert({ message: "Pest detected successfully!", severity: "success" }));
  } catch (e: any) {
    yield put(actionSetPestError(e.message ?? "Analysis failed"));
    yield put(showAlert({ message: e.message ?? "Analysis failed", severity: "error" }));
  } finally { yield put(actionSetAnalyzeLoading(false)); }
}

function* deleteDetection(action: PayloadAction<number>): SagaIterator {
  try {
    yield call(apiDeleteDetection, action.payload);
    yield put(actionRemoveDetection(action.payload));
    yield put(showAlert({ message: "Detection deleted", severity: "success" }));
  } catch (e: any) {
    yield put(showAlert({ message: e.message ?? "Delete failed", severity: "error" }));
  }
}

export const sagaPest = [
  takeEvery(actionGetDetectionHistory.type, fetchHistory),
  takeEvery(actionAnalyzePestImage.type, analyzeImage),
  takeEvery(actionDeleteDetection.type, deleteDetection),
];
