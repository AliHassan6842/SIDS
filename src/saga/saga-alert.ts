import { call, put, takeLatest, takeEvery, delay } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import { actionGetAlerts, actionSetAlerts, actionSetAlertLoading, actionSetAlertError, actionMarkAllRead, actionSetAlertSuccess } from "../slice/slice-alert";
import { getAlerts, markAllAlertsRead } from "../api/v1-contracts";
import { showAlert } from "../slice/slice-alert-global";

function* fetchAlerts(): SagaIterator {
  try {
    yield put(actionSetAlertLoading(true));
    const res = yield call(getAlerts);
    yield put(actionSetAlerts(Array.isArray(res) ? res : res?.data ?? []));
  } catch (e: any) {
    yield put(showAlert({ message: "Failed to load alerts", severity: "error" }));
  } finally { yield put(actionSetAlertLoading(false)); }
}

function* markAllRead(): SagaIterator {
  try {
    yield call(markAllAlertsRead);
    yield put(actionGetAlerts());
  } catch {}
}

export const sagaAlert = [
  takeEvery(actionGetAlerts.type, fetchAlerts),
  takeEvery(actionMarkAllRead.type, markAllRead),
];
