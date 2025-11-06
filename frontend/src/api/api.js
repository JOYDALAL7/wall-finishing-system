// frontend/src/api/api.js
import axios from "axios";

// ✅ Automatically use Render backend when deployed on Vercel
const API_BASE =
  import.meta.env.VITE_API_URL || "https://wall-finishing-system.onrender.com";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// ============================
// 📦 Coverage Planning API
// ============================
export async function planCoverage({ wall_width, wall_height, obstacles, step }) {
  const payload = { wall_width, wall_height, obstacles, step };
  const res = await client.post("/api/coverage/", payload);
  return res.data; // {plan_id, points: [{x,y,timestamp}]}
}

// ============================
// 📦 Get Recent Trajectories
// ============================
export async function getRecentTrajectories(limit = 200) {
  const res = await client.get(`/api/trajectory/?limit=${limit}&offset=0`);
  return res.data; // list of trajectory rows
}

// ============================
// 📦 Get Trajectories by Plan ID
// ============================
export async function getTrajectoriesByPlan(plan_id) {
  const res = await client.get(`/api/trajectory/by_plan/${plan_id}`);
  return res.data; // list of points
}

// ============================
// 🔌 WebSocket Stream for Live Playback
// ============================
export function wsUrlForPlan(plan_id) {
  // Use ws:// locally, wss:// on production
  const backendUrl =
    import.meta.env.VITE_API_URL || "https://wall-finishing-system.onrender.com";
  const wsBase = backendUrl.replace(/^http/, "ws");
  return `${wsBase}/ws/play/${plan_id}`; // ✅ correct live playback route
}
