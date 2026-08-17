import React, { Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { CircularProgress, Box } from "@mui/material";
import { lazyWithRetry } from "../lib/lazyWithRetry";
import MainLayout from "../layout/MainLayout";
import RequireAuth from "../auth/RequireAuth";

const HomePage       = lazyWithRetry(() => import("../pages/Dashboard/component/dashboard-main"));
const ScanPage       = lazyWithRetry(() => import("../pages/Detection/component/detection-upload"));
const SurveyPage     = lazyWithRetry(() => import("../pages/Survey/component/survey-main"));
const FieldsPage     = lazyWithRetry(() => import("../pages/Fields/component/field-list"));
const TasksPage      = lazyWithRetry(() => import("../pages/Tasks/component/tasks-main"));
const MorePage       = lazyWithRetry(() => import("../pages/More/component/more-main"));

const AdvisoryPage   = lazyWithRetry(() => import("../pages/Advisory/component/advisory-main"));
const HistoryPage    = lazyWithRetry(() => import("../pages/History/component/history-list"));
const AlertsPage     = lazyWithRetry(() => import("../pages/Alerts/component/alert-list"));
const ReportsPage    = lazyWithRetry(() => import("../pages/Reports/component/reports-main"));
const ProfilePage    = lazyWithRetry(() => import("../pages/Profile/component/profile-main"));
const AdminPage      = lazyWithRetry(() => import("../pages/Admin/component/admin-dashboard"));
const LoginPage      = lazyWithRetry(() => import("../pages/Login/login-page"));

const Loading = () => (
  <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
    <CircularProgress color="success" />
  </Box>
);

const AppRoutes: React.FC = () => (
  <Suspense fallback={<Loading />}>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RequireAuth><MainLayout /></RequireAuth>}>
        <Route index element={<Navigate to="/home" replace />} />
        {/* 5 Primary Tabs */}
        <Route path="home"   element={<HomePage />} />
        <Route path="fields" element={<FieldsPage />} />
        <Route path="scan"   element={<ScanPage />} />
        <Route path="survey" element={<SurveyPage />} />
        <Route path="tasks"  element={<TasksPage />} />
        <Route path="more"   element={<MorePage />} />
        
        {/* Sub-pages accessed from More or Home */}
        <Route path="advisory"  element={<AdvisoryPage />} />
        <Route path="history"   element={<HistoryPage />} />
        <Route path="alerts"    element={<AlertsPage />} />
        <Route path="reports"   element={<ReportsPage />} />
        <Route path="profile"   element={<ProfilePage />} />
        <Route path="admin"     element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  </Suspense>
);

export default AppRoutes;
