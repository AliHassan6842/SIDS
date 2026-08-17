import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface SyncTask {
  id: string;
  type: "quick_scan" | "field_survey";
  payload: any;
  timestamp: string;
}

interface SyncState {
  isOffline: boolean;
  queue: SyncTask[];
  syncing: boolean;
}

const initialState: SyncState = {
  isOffline: false,
  queue: [],
  syncing: false,
};

const syncSlice = createSlice({
  name: "sync",
  initialState,
  reducers: {
    toggleOfflineMode(state) {
      state.isOffline = !state.isOffline;
    },
    enqueueTask(state, action: PayloadAction<Omit<SyncTask, "id" | "timestamp">>) {
      state.queue.push({
        ...action.payload,
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toISOString()
      });
    },
    startSync(state) {
      state.syncing = true;
    },
    syncSuccess(state) {
      state.queue = [];
      state.syncing = false;
    },
    clearQueue(state) {
      state.queue = [];
    }
  }
});

export const { toggleOfflineMode, enqueueTask, startSync, syncSuccess, clearQueue } = syncSlice.actions;
export default syncSlice.reducer;
