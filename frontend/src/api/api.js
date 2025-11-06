import axios from "axios";

// ✅ Automatically select backend
// - Render backend when deployed
// - Localhost when testing locally
const API_BASE =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" &&
  window.location.hostname.includes("vercel.app"))
    ? "https://wall-finishing-system.onrender.com"
    : "http://127.0.0.1:8000";

console.log("🔗 Using API Base:", API_BASE);

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
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
  // Convert http → ws and https → wss
  const wsBase = API_BASE.replace(/^http:/, "ws:").replace(/^https:/, "wss:");
  return `${wsBase}/ws/play/${plan_id}`;
}
