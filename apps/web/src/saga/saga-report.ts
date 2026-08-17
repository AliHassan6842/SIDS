import { call, put, takeEvery } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import type { PayloadAction } from "@reduxjs/toolkit";
import { actionGetReportSummary, actionSetReportSummary, actionSetReportLoading, actionSetReportError } from "../slice/slice-report";
import { getReportSummary } from "../api/v1-contracts";

function* fetchSummary(action: PayloadAction<Record<string, any> | undefined>): SagaIterator {
  try {
    yield put(actionSetReportLoading(true));
    const res = yield call(getReportSummary, action.payload);
    yield put(actionSetReportSummary(res));
  } catch (e: any) {
    yield put(actionSetReportError(e.message ?? "Failed to load report"));
  } finally { yield put(actionSetReportLoading(false)); }
}

export const sagaReport = [takeEvery(actionGetReportSummary.type, fetchSummary)];
