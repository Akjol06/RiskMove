# Credit Scoring System

An intelligent credit scoring API built with Domain-Driven Design (DDD) principles.

## Features
- **XGBoost Classifier**: High-performance risk prediction.
- **Explainable AI (SHAP)**: Feature-level impact analysis for every prediction.
- **DDD Architecture**: Clean separation of Domain, Application, Infrastructure, and Interfaces.
- **FastAPI**: Modern, high-performance API framework.

## Project Structure
- `app/domain`: Domain entities and value objects.
- `app/application`: Use cases and orchestration services.
- `app/infrastructure`: ML model implementation and data access.
- `app/interfaces`: FastAPI routes and request/response schemas.
- `data/`: Dataset and analysis files.
- `models/`: Serialized models and explainers.
- `scripts/`: Utility scripts for data prep and training.

## Setup and Running

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation
```bash
uv sync
```

### 1. Data Preparation
```bash
uv run python scripts/data_prep.py
```

### 2. Model Training
```bash
uv run python scripts/train_model.py
```

### 3. Start API
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. 
Explore the documentation at `http://localhost:8000/docs`.

## API Endpoints
- `POST /api/v1/predict`: Submit a credit application and receive a decision with probability and explanation.
- `GET /api/v1/health`: Check API status.
