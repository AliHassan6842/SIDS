import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAppSelector } from "../hooks/useStoreData";

interface Props {
  allowedRoles: Array<"Admin" | "Farmer">;
}

const RequireRole: React.FC<Props> = ({ allowedRoles }) => {
  const user = useAppSelector((state) => state.user.profile);
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.Role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};

export default RequireRole;
