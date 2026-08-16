import { all } from "redux-saga/effects";
import { sagaPest } from "./saga-pest";
import { sagaField } from "./saga-field";
import { sagaAlert } from "./saga-alert";
import { sagaReport } from "./saga-report";
import { sagaUser } from "./saga-user";

export default function* rootSaga() {
  yield all([
    ...sagaPest,
    ...sagaField,
    ...sagaAlert,
    ...sagaReport,
    ...sagaUser,
  ]);
}
