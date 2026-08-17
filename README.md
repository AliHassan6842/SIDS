# SIDS — AI Digital Crop Scout

SIDS (Smart Insect Detection System) is an offline-first platform that helps farmers capture crop observations, obtain bounded AI analysis, and make field decisions using verified agricultural context. 

## 🚀 Getting Started

This repository is built as a **Feature-First Modular Monolith** spanning across Java (Core Business), Python (AI/ML), and React (Web). Follow these steps to spin up the entire cluster locally.

### Prerequisites
- **Java 21 JDK**: Required for the Spring Boot Core API. (Ensure `JAVA_HOME` is set).
- **Python 3.10+**: Required for the FastAPI AI Service and ML training pipelines.
- **Docker Desktop**: Required to spin up local infrastructure (PostgreSQL, Valkey, MinIO).
- **Node.js & pnpm**: Required for frontend and monorepo script management (`corepack enable`).

### Step 1: Download the Datasets & Models
Because ML models and datasets are massively large binary files, they are securely managed externally via Google Drive. You must download them before running the inference engine.

We have built an automated downloader that syncs the assets straight from Drive into your local workspace. From the root directory, simply run:
```sh
pnpm run download:assets
```
This single command will:
1. Download the YOLO Pest Detector (`best.pt`).
2. Download the PyTorch Disease Classifier (`best_model.pth`).
3. Download and extract the raw training images (`datasets.zip`).
It will place all models inside `ml/model-registry/` and the images inside `ml/datasets/` automatically.

### Step 2: Environment Configuration
Copy the sample environment file to create your local active configuration:
```sh
cp .env.example .env
```
This `.env` securely holds the database credentials and MinIO storage keys globally for all modules without hardcoding them in the source.

### Step 3: Run the System
You can boot the entire system with one single command using `pnpm`.

```sh
# 1. Install workspace dependencies
pnpm install

# 2. Boot the entire cluster (Infra + AI + Java + Web)
pnpm run dev:all
```

If you prefer to run services individually:
- `pnpm run infra:up`: Starts PostgreSQL (with pgvector), Valkey, and MinIO locally via Docker.
- `pnpm run api:dev`: Starts the Java Spring Boot Core API.
- `pnpm run ai:dev`: Starts the Python FastAPI AI inference engine.
- `pnpm run ai:worker`: Starts the Python Valkey background consumer.
- `pnpm run web:dev`: Starts the React Web Frontend.

---

## 🏗️ Architecture & Dependencies

The system uses specific, isolated dependencies for each module to enforce the **IPM-First (Integrated Pest Management)** agronomic rules.

### 1. Core API (`services/core-api`)
**Language**: Java 21 | **Framework**: Spring Boot 3.4
- **Spring Boot Modulith**: Ensures strict boundaries between modules like `farm`, `survey`, `diagnosis`, and `agronomy`.
- **Spring Data JPA (Hibernate)**: Manages all business-critical domain tables (like Users, Tasks, and Farm Memberships) inside PostgreSQL.
- **Spring JdbcClient**: Used specifically in the `knowledge` module for lightweight raw-read access to Python's threshold tables, avoiding duplicated schemas.
- **Spring Boot OAuth2 Resource Server**: Enforces secure JWT validation on all endpoints.
- **AWS SDK (S3)**: Connects to MinIO (`StorageProvider`) for durable agricultural image preservation.

### 2. AI Inference Engine (`services/ai-service`)
**Language**: Python 3.10 | **Framework**: FastAPI
- **Ultralytics (YOLO)**: Runs in the `detector.py` to identify pests within raw images.
- **ONNX Runtime**: Used by `classifier.py` for highly optimized, low-latency crop disease classification without massive GPU overhead.
- **Redis (Valkey) Streams**: Acts as the asynchronous transport layer (`sids:ai:jobs`) bridging Java requests with Python processing nodes.
- **pgvector**: Used in `retrieval` to query the AI embeddings for semantic knowledge extraction.

### 3. Infrastructure (`infra/docker-compose.yml`)
- **PostgreSQL 16 (pgvector)**: The single source of durable truth for both business state and ML vector embeddings.
- **Valkey 7.2**: High-performance transient memory store managing the AI Job queues and Redis consumer groups.
- **MinIO**: Local S3-compatible object storage server that hosts the uploaded observation imagery securely behind presigned URLs.

## ⚙️ Development Workflow

1. **Frontend**: The `apps/web` folder is owned by the Frontend team. Backend engineers must not mutate React components or Vite settings.
2. **AI Analysis Flow**:
   - The user submits an image to Java. Java streams it to MinIO.
   - Java drops a job on the Valkey stream.
   - The Python `ai:worker` consumes the image, evaluates it using YOLO, and posts back to Valkey.
   - Java reads the response, validates it, and triggers the `AgronomyDecisionEngine` to look up localized thresholds (e.g., Punjab Agriculture tables) and assigns a recommended Task.
3. **Commit Rules**: Never commit AI prompt markdown files. The `.gitignore` at the root automatically filters these out to maintain project cleanliness.
