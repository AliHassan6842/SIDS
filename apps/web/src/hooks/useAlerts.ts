import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "./useStoreData";
import { actionGetAlerts } from "../slice/slice-alert";

export const useAlerts = () => {
  const dispatch = useAppDispatch();
  const { list, loading, unreadCount } = useAppSelector((s) => s.alert);
  useEffect(() => { dispatch(actionGetAlerts()); }, [dispatch]);
  return { alerts: list, loading, unreadCount };
};
