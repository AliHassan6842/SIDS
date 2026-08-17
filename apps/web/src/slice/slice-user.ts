import { createSlice, createAction, type PayloadAction } from "@reduxjs/toolkit";
import type { IUserProfile } from "../types/user/user";

interface UserState { profile: IUserProfile | null; loading: boolean; saveLoading: boolean; error: string | null; }
const initialState: UserState = { profile: null, loading: false, saveLoading: false, error: null };
export const actionGetProfile = createAction("user/profile");
export const actionUpdateProfile = createAction<Partial<IUserProfile>>("user/update");
const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    actionSetProfile(state, action: PayloadAction<IUserProfile>) { state.profile = action.payload; },
    actionSetUserLoading(state, action: PayloadAction<boolean>) { state.loading = action.payload; },
    actionSetUserSaveLoading(state, action: PayloadAction<boolean>) { state.saveLoading = action.payload; },
    actionSetUserError(state, action: PayloadAction<string | null>) { state.error = action.payload; },
  },
});
export const { actionSetProfile, actionSetUserLoading, actionSetUserSaveLoading, actionSetUserError } = userSlice.actions;
export default userSlice.reducer;
