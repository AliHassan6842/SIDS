import { call, put, takeEvery } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import { actionGetAlerts, actionMarkAllRead, actionSetAlerts, actionSetAlertLoading } from "../slice/slice-alert";
import { apiGetAlerts, apiMarkAllAlertsRead } from "../api/api-alert";
import { showAlert } from "../slice/slice-alert-global";

function* fetchAlerts(): SagaIterator {
  try {
    yield put(actionSetAlertLoading(true));
    const res = yield call(apiGetAlerts);
    yield put(actionSetAlerts(Array.isArray(res) ? res : res?.data ?? []));
  } catch (e: any) {
    yield put(showAlert({ message: "Failed to load alerts", severity: "error" }));
  } finally { yield put(actionSetAlertLoading(false)); }
}

function* markAllRead(): SagaIterator {
  try {
    yield call(apiMarkAllAlertsRead);
    yield put(actionGetAlerts());
  } catch {}
}

export const sagaAlert = [
  takeEvery(actionGetAlerts.type, fetchAlerts),
  takeEvery(actionMarkAllRead.type, markAllRead),
];
