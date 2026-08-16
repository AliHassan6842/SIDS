import React from "react";
import { Navigate, useLocation } from "react-router-dom";

interface Props { children: React.ReactNode; }

const RequireAuth: React.FC<Props> = ({ children }) => {
  const token = localStorage.getItem("agrosense_token");
  const location = useLocation();
  if (!token) return <Navigate to="/login" state={{ from: location }} replace />;
  return <>{children}</>;
};

export default RequireAuth;
