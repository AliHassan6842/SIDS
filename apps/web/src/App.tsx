import React from "react";
import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes/app-route";

const App: React.FC = () => (
  <BrowserRouter>
    <AppRoutes />
  </BrowserRouter>
);

export default App;
