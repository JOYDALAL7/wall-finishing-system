# 🧱 Wall Finishing System  
### BE Intern Assignment – 10X Construction AI  

**👤 Author:** Joy Dalal  
📹 [🎥 Watch Project Walkthrough on Loom →](https://www.loom.com/share/f227a3af248543ce915d17c5b3c3f22f)  

---

## 🧭 Overview  

The **Wall Finishing System** is a complete **backend + frontend application** designed to control and visualize an **autonomous wall-finishing robot**.  
It handles **intelligent path coverage planning**, **data storage**, and **real-time 2D trajectory visualization**, providing insights into how a robot efficiently covers a wall surface.  

This project demonstrates a fully integrated, cloud-deployed solution — built using **FastAPI**, **SQLite**, **React (Vite)**, and **TailwindCSS**, ensuring both performance and scalability.  

---

## 🎯 Objectives  

- Build an optimized backend for coverage planning and trajectory computation.  
- Provide real-time visualization of robot path coverage.  
- Enable playback of movement trajectories for testing and analysis.  
- Create a robust, production-ready architecture with deployment on Render and Vercel.  

---

## ⚙️ Key Features  

✅ **Coverage Planning** – Generates optimized wall coverage trajectories for rectangular areas.  
✅ **Backend API (FastAPI)** – Manages trajectory data, path computation, and response-time logging.  
✅ **Database Layer (SQLite)** – Stores wall dimensions, trajectory points, and timestamps efficiently.  
✅ **Frontend Visualization** – Built with React + Recharts for smooth, animated path playback.  
✅ **REST-based Playback** – Eliminates WebSocket dependencies with a frame-synced REST animation system.  
✅ **Real-time Logs & Monitoring** – Custom middleware for request timing and debugging.  
✅ **Fully Deployed** – Backend (Render) + Frontend (Vercel) for a cloud-hosted end-to-end solution.  

---

## 🧠 Tech Stack  

| Layer | Technology |
|-------|-------------|
| **Backend** | FastAPI, SQLAlchemy, SQLite, Uvicorn |
| **Frontend** | React (Vite), Recharts, TailwindCSS |
| **Deployment** | Render (Backend), Vercel (Frontend) |
| **Version Control** | Git & GitHub |
| **Visualization** | Recharts (2D trajectory animation) |

---

## 🔁 System Architecture / Workflow  

```text
🧍 User Input (Wall Dimensions + Obstacles)
      │
      ▼
🖥️ Frontend (React + Recharts)
      │
      ▼
⚙️ Backend (FastAPI + SQLite)
      │
      ▼
🗄️ Trajectory Database (CRUD Operations)
      │
      ▼
📊 API Response → Animated Path Visualization
```

⚙️ Setup Instructions

🧩 Backend Setup
```bash
# Clone the repository
git clone https://github.com/JOYDALAL7/wall-finishing-system.git
cd wall-finishing-system/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # (For Windows PowerShell)

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload
```
✅ Backend runs at: http://127.0.0.1:8000

🎨 Frontend Setup
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
✅ Frontend runs at: http://127.0.0.1:5173

🌐 Deployed Links
| Component             | Platform  | URL                                                                                      |
| --------------------- | --------- | ---------------------------------------------------------------------------------------- |
| **Frontend (React)**  | 🟦 Vercel | [https://wall-finishing-system.vercel.app](https://wall-finishing-system.vercel.app)     |
| **Backend (FastAPI)** | 🟩 Render | [https://wall-finishing-system.onrender.com](https://wall-finishing-system.onrender.com) |


🎥 Demo Video

🎬 Full Walkthrough (3 mins)
👉 Loom Video – https://www.loom.com/share/f227a3af248543ce915d17c5b3c3f22f

Covered in the video:
Project overview and architecture
FastAPI backend demo (data + logging)
React-based path visualization in action
Cloud deployment explanation

👤 Submission Details

| Field                     | Details                                                                                                                    |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Name**                  | Joy Dalal                                                                                                                  |
| **Assignment**            | BE Intern Assignment – Wall Finishing Robot System                                                                         |
| **Organization**          | 10X Construction AI                                                                                                        |
| **Evaluators**            | [tanay@10xconstruction.ai](mailto:tanay@10xconstruction.ai), [tushar@10xconstruction.ai](mailto:tushar@10xconstruction.ai) |
| **Repository Visibility** | Private (includes code, deployments & video)                                                                               |


📁 Folder Structure
```text

wall-finishing-system/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── coverage.py
│   │   │   ├── trajectory.py
│   │   │   └── player.py
│   │   ├── database.py
│   │   ├── utils/
│   │   │   ├── coverage_planner.py
│   │   │   └── logging.py
│   ├── requirements.txt
│   └── trajectory.db
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CoverageForm.jsx
│   │   │   ├── PathVisualizer.jsx
│   │   │   └── TrajectoryList.jsx
│   │   ├── api/
│   │   │   └── api.js
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
``

🧠 Every component — from FastAPI endpoints to React visualization — was written with clarity, modularity, and scalability in mind.

