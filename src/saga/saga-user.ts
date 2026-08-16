import { call, put, takeEvery } from "redux-saga/effects";
import type { SagaIterator } from "redux-saga";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { IUserProfile } from "../types/user/user";
import { actionGetProfile, actionSetProfile, actionSetProfileLoading, actionUpdateProfile, actionSetProfileSaveLoading, actionSetProfileError, actionSetProfileSuccess } from "../slice/slice-user";
import { getProfile, updateProfile } from "../api/v1-contracts";
import { showAlert } from "../slice/slice-alert-global";

function* fetchProfile(): SagaIterator {
  try {
    yield put(actionSetProfileLoading(true));
    const res = yield call(getProfile);
    yield put(actionSetProfile(res));
  } catch {} finally { yield put(actionSetUserLoading(false)); }
}

function* updateProfile(action: PayloadAction<Partial<IUserProfile>>): SagaIterator {
  try {
    yield put(actionSetUserSaveLoading(true));
    const res = yield call(updateProfile, action.payload);
    yield put(actionSetProfile(res));
    yield put(showAlert({ message: "Profile updated successfully", severity: "success" }));
  } catch (e: any) {
    yield put(showAlert({ message: e.message ?? "Update failed", severity: "error" }));
  } finally { yield put(actionSetUserSaveLoading(false)); }
}

export const sagaUser = [
  takeEvery(actionGetProfile.type, fetchProfile),
  takeEvery(actionUpdateProfile.type, updateProfile),
];
