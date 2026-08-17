import { Alert, Snackbar } from "@mui/material";
import { useAppDispatch, useAppSelector } from "../../hooks/useStoreData";
import { hideAlert } from "../../slice/slice-alert-global";
const GlobalAlert = () => {
  const dispatch = useAppDispatch();
  const { open, message, severity } = useAppSelector((s) => s.alertGlobal);
  return <Snackbar open={open} autoHideDuration={4000} onClose={() => dispatch(hideAlert())} anchorOrigin={{ vertical: "bottom", horizontal: "right" }}><Alert severity={severity} onClose={() => dispatch(hideAlert())} variant="filled">{message}</Alert></Snackbar>;
};
export default GlobalAlert;
