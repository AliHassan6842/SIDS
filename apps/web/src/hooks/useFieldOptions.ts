import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "./useStoreData";
import { actionGetFields } from "../slice/slice-field";

export const useFieldOptions = () => {
  const dispatch = useAppDispatch();
  const { list } = useAppSelector((s) => s.field);
  useEffect(() => { dispatch(actionGetFields(undefined)); }, [dispatch]);
  return list.data.map((f) => ({ value: f.FieldID, label: f.FieldName }));
};
