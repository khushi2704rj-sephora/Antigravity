<div align="center">

# 🌌 Antigravity: The Game Theory Lab

[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![SciPy](https://img.shields.io/badge/Math-SciPy_Optimization-8CAAE6?logo=scipy&logoColor=white)](https://scipy.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**A modern, interactive simulation platform for visualizing Game Theory concepts, Nash Equilibria, and Multi-Agent dynamics.**

[🚀 **Live Demo**](https://antigravity.railway.app) · [📖 **API Documentation**](https://antigravity.railway.app/docs)

</div>

---

## 🎯 Project Overview

**Antigravity** bridges the gap between abstract mathematical models and intuitive understanding. Built with a high-performance **FastAPI** backend and a **React 19** frontend, it allows researchers and students to simulate complex game-theoretic scenarios in real-time.

**Key Features:**
- **20+ Simulations**: Prisoner's Dilemma, Stag Hunt, Ultimatum Game, and more.
- **Nash Solver**: Real-time calculation of pure and mixed strategy equilibria using `Nashpy`.
- **Interactive Visuals**: Dynamic payoff matrices and evolution graphs using `Plotly.js`.
- **Material Design 3**: A polished, Google-inspired UI with glassmorphism effects.

---

## 🏗️ System Architecture

The application follows a decoupled microservices architecture, containerized with Docker for seamless deployment.

```mermaid
graph TD
    User[👤 User / Browser] -->|HTTPS| Nginx[🌐 Nginx Reverse Proxy]
    
    subgraph "Docker Network"
        Nginx -->|/api/*| API[⚡ FastAPI Backend]
        Nginx -->|/*| Client[⚛️ React Frontend]
        
        API -->|Computation| SciPy[🧮 SciPy / Nashpy Solver]
        API -->|Data Handling| NumPy[Pandas / NumPy]
    end
    
    style User fill:#fff,stroke:#333
    style Nginx fill:#009639,stroke:#006400,color:#fff
    style API fill:#009688,stroke:#004d40,color:#fff
    style Client fill:#61DAFB,stroke:#0d47a1,color:#000
    style SciPy fill:#8CAAE6,stroke:#1a237e,color:#fff
```

---

## 📂 Repository Structure

```
antigravity/
│
├── backend/                  ← Python Service
│   ├── app/
│   │   ├── main.py           ← API Entrypoint & Routes
│   │   ├── simulations/      ← Game Logic Modules
│   │   └── solver.py         ← Nash Equilibrium Algorithms
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                 ← TypeScript React App
│   ├── src/
│   │   ├── components/       ← Creating Reusable UI
│   │   ├── stores/           ← State Management
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml        ← Orchestration Config
├── LICENSE                   ← MIT License
└── README.md                 ← Project Documentation
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

Run the entire stack with a single command:

```bash
# Clone the repository
git clone https://github.com/khushi2704rj-sephora/Antigravity.git
cd Antigravity

# Start services
docker-compose up --build
```

Access the app at `http://localhost:3000` and the API docs at `http://localhost:8000/docs`.

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🤝 Contributing

We welcome contributions! Whether it's adding a new game simulation, optimizing the solver, or polishing the UI. 

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

<div align="center">

**Built with ❤️ for Game Theory**

</div>
