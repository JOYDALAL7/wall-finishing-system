import axios from "axios";

// ✅ Determine API base URL safely for both local & deployed builds
let API_BASE = import.meta.env.VITE_API_URL;

if (!API_BASE) {
  if (typeof window !== "undefined" && window.location.hostname.includes("vercel.app")) {
    // Production (Vercel → talks to Render backend)
    API_BASE = "https://wall-finishing-system.onrender.com";
  } else {
    // Local development
    API_BASE = "http://127.0.0.1:8000";
  }
}

console.log("🔗 Using API Base:", API_BASE);

// ✅ Axios client
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
  return res.data; // { plan_id, points: [{x,y,timestamp}] }
}

// ============================
// 📦 Get Recent Trajectories
// ============================
export async function getRecentTrajectories(limit = 200) {
  const res = await client.get(`/api/trajectory/recent?limit=${limit}`);
  return res.data; // list of trajectory rows
}

// ============================
// 📦 Get Trajectories by Plan ID
// ============================
export async function getTrajectoriesByPlan(plan_id) {
  const res = await client.get(`/api/trajectory/${plan_id}`);
  return res.data; // list of points
}

// ============================
// 🔌 WebSocket Stream for Live Playback
// ============================
export function wsUrlForPlan(plan_id) {
  let wsBase = API_BASE.replace(/^http:/, "ws:").replace(/^https:/, "wss:");

  // ✅ Always use Render backend when running from Vercel
  if (typeof window !== "undefined" && window.location.hostname.includes("vercel.app")) {
    wsBase = "wss://wall-finishing-system.onrender.com";
  }

  // ✅ Correct WebSocket endpoint (matches backend route)
  const wsUrl = `${wsBase}/ws/play/${plan_id}`;
  console.log("🎥 Final WebSocket URL:", wsUrl);
  return wsUrl;
}
