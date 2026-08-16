import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface IAlert {
  id: number;
  msg: string;
  type: "info" | "warn" | "danger";
  time: string;
}

export interface IPesticideRecord {
  id: number;
  datetime: string;
  chemical: string;
  pest: string;
  zone: string;
  dosage: string;
  area: string;
  applier: string;
  status: string;
  notes: string;
}

interface AgrishieldState {
  detections: number;
  activeSensors: number;
  alerts: IAlert[];
  pesticideRecords: IPesticideRecord[];
}

const initialState: AgrishieldState = {
  detections: 0,
  activeSensors: 16,
  alerts: [],
  pesticideRecords: [],
};

const agrishieldSlice = createSlice({
  name: "agrishield",
  initialState,
  reducers: {
    addAlert(state, action: PayloadAction<IAlert>) {
      state.alerts.unshift(action.payload);
      if (state.alerts.length > 20) state.alerts.pop();
    },
    clearAlerts(state) {
      state.alerts = [];
    },
    incrementDetections(state) {
      state.detections += 1;
    },
    addPesticideRecord(state, action: PayloadAction<IPesticideRecord>) {
      state.pesticideRecords.unshift(action.payload);
    },
    deletePesticideRecord(state, action: PayloadAction<number>) {
      state.pesticideRecords = state.pesticideRecords.filter((r) => r.id !== action.payload);
    },
  },
});

export const {
  addAlert,
  clearAlerts,
  incrementDetections,
  addPesticideRecord,
  deletePesticideRecord,
} = agrishieldSlice.actions;

export default agrishieldSlice.reducer;
