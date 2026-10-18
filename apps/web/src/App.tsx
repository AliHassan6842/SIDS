import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { RequireAuth } from "./auth/RequireAuth";
import { AppShell } from "./components/AppShell";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { LoadingState } from "./components/AsyncState";

const LoginPage = lazy(() => import("./pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const RegisterPage = lazy(() => import("./pages/RegisterPage").then((module) => ({ default: module.RegisterPage })));
const HomePage = lazy(() => import("./pages/HomePage").then((module) => ({ default: module.HomePage })));
const IdentifyPage = lazy(() => import("./pages/IdentifyPage").then((module) => ({ default: module.IdentifyPage })));
const ResultPage = lazy(() => import("./pages/ResultPage").then((module) => ({ default: module.ResultPage })));
const PestLibraryPage = lazy(() => import("./pages/PestLibraryPage").then((module) => ({ default: module.PestLibraryPage })));
const PestDetailsPage = lazy(() => import("./pages/PestDetailsPage").then((module) => ({ default: module.PestDetailsPage })));
const HistoryPage = lazy(() => import("./pages/HistoryPage").then((module) => ({ default: module.HistoryPage })));
const ProfilePage = lazy(() => import("./pages/ProfilePage").then((module) => ({ default: module.ProfilePage })));

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Suspense fallback={<div className="route-loader"><LoadingState /></div>}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<RequireAuth><AppShell /></RequireAuth>}>
              <Route index element={<Navigate to="/home" replace />} />
              <Route path="home" element={<HomePage />} />
              <Route path="identify" element={<IdentifyPage />} />
              <Route path="result/:scanId" element={<ResultPage />} />
              <Route path="pests" element={<PestLibraryPage />} />
              <Route path="pests/:pestId" element={<PestDetailsPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
