# AgroSense: Farmer Mobile App (Frontend Prototype)

Welcome to the frontend prototype of the **AgroSense AI Digital Crop Scout** (SIDS 2026 Blueprint). 

This is an **Offline-First**, mobile-responsive web application built with React and Vite. It is designed to be fully compliant with the frontend architecture and API contracts outlined in the SIDS 2026 Blueprint.

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```
The app will be available at `http://localhost:5173`. 

*Note: For the best experience, open Chrome DevTools (F12) and toggle the **Device Toolbar** to view the app in a mobile resolution (e.g., iPhone 12/14 Pro).*

---

## 🔌 Backend Integration (Java Spring Boot)

This frontend has been strictly typed and mapped to expect a **Java Spring Boot** backend. 

### API Proxy
The Vite development server is configured to proxy all `/v1/*` API requests to **`http://localhost:8080`**. 
When you run your Spring Boot application locally on port 8080, this frontend will automatically route requests to it without CORS issues.

### API Contracts
All API endpoints are defined in a single source of truth:
👉 `src/api/v1-contracts.ts`

The frontend will attempt to call the following core routes:
- `GET /v1/me` (Auth profile)
- `GET /v1/fields` (Farm/Field management)
- `POST /v1/fields` (Upsert field)
- `POST /v1/observations` (Quick Scan captures)
- `POST /v1/surveys` (Protocol-based field surveys)
- `POST /v1/sync` (Idempotent background sync queue)

### Data Payloads
All Typescript interfaces (e.g., `src/types/field/field.ts`) have been refactored to use standard **`camelCase`**. 
* Ensure your Java DTOs use standard Jackson serialization (e.g., `fieldName`, `cropType`, `sizeAcres`). Do **NOT** use PascalCase.

---

## 🏗️ Architecture & Features

### Form Validation (Zod)
In compliance with the blueprint, all critical forms (like Field Setup) use **Zod** paired with **React Hook Form** (`src/pages/Fields/component/field-list.tsx`). This ensures strict data validation before payloads ever reach the backend.

### Offline Queue (Redux)
Because this is an offline-first tool, data mutations (like Scans and Surveys) are not always sent to the server immediately.
- If the app is "Offline" (you can toggle this via the top banner in the UI), tasks are intercepted by Redux and stored in an **Offline Queue** (`src/slice/slice-sync.ts`).
- You can view and manually flush this queue from the **Tasks** tab in the app.

### Dynamic Theming
The app supports dynamic **Light/Dark/System** theming. This state is managed via Redux and can be toggled from the **More** tab.

---

## 📚 Tech Stack
- **Framework**: React 18 + Vite
- **Routing**: React Router DOM (v6)
- **State Management**: Redux Toolkit + Redux Persist + Redux Saga
- **UI Components**: Material-UI (MUI v5)
- **Validation**: Zod + React Hook Form
