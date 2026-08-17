import { configureStore, combineReducers } from "@reduxjs/toolkit";
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from "redux-persist";
import storage from "redux-persist/lib/storage";
import createSagaMiddleware from "redux-saga";
import rootSaga from "../saga";
import alertGlobalReducer from "../slice/slice-alert-global";
import pestReducer from "../slice/slice-pest";
import fieldReducer from "../slice/slice-field";
import alertReducer from "../slice/slice-alert";
import reportReducer from "../slice/slice-report";
import userReducer from "../slice/slice-user";
import themeReducer from "../slice/slice-theme";
import agrishieldReducer from "../slice/slice-agrishield";
import syncReducer from "../slice/slice-sync";

const sagaMiddleware = createSagaMiddleware();

const rootReducer = combineReducers({
  alertGlobal: alertGlobalReducer,
  pest: pestReducer,
  field: fieldReducer,
  alert: alertReducer,
  report: reportReducer,
  user: userReducer,
  theme: themeReducer,
  agrishield: agrishieldReducer,
  sync: syncReducer,
});

const persistConfig = {
  key: "agrosense-root",
  storage,
  whitelist: ["user", "theme", "agrishield", "sync"],
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }).concat(sagaMiddleware),
});

sagaMiddleware.run(rootSaga);

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;
