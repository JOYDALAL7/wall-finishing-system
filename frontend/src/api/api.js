import axios from "axios";

// ============================
// 🌐 Determine API Base URL
// ============================
let API_BASE = import.meta.env.VITE_API_URL;

if (!API_BASE) {
  if (
    typeof window !== "undefined" &&
    (window.location.hostname.includes("vercel.app") ||
      window.location.hostname.includes("onrender.com"))
  ) {
    // ✅ Production (Vercel → Render backend)
    API_BASE = "https://wall-finishing-system.onrender.com";
  } else {
    // ✅ Local Development
    API_BASE = "http://127.0.0.1:8000";
  }
}

console.log("🔗 Using API Base:", API_BASE);

// ============================
// ⚙️ Axios Client
// ============================
const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

// ============================
// 📦 Coverage Planning API
// ============================
export async function planCoverage({ wall_width, wall_height, obstacles, step }) {
  try {
    const payload = { wall_width, wall_height, obstacles, step };
    const res = await client.post("/api/coverage/", payload);
    return res.data; // { plan_id, points: [{x, y, timestamp}] }
  } catch (err) {
    console.error("❌ Error creating coverage plan:", err.response?.data || err.message);
    throw err;
  }
}

// ============================
// 📦 Get Recent Trajectories
// ============================
export async function getRecentTrajectories(limit = 200) {
  const res = await client.get(`/api/trajectory/recent?limit=${limit}`);
  return res.data;
}

// ============================
// 📦 Get Trajectories by Plan ID
// ============================
export async function getTrajectoriesByPlan(plan_id) {
  const res = await client.get(`/api/trajectory/${plan_id}`);
  return res.data;
}

// ============================
// 🔌 WebSocket for Live Playback
// ============================
export function wsUrlForPlan(plan_id) {
  if (!plan_id) {
    console.error("⚠️ Missing plan_id for WebSocket connection.");
    return null;
  }

  // ✅ Convert http → ws and https → wss
  let wsBase = API_BASE.replace(/^http:/, "ws:").replace(/^https:/, "wss:");

  // ✅ Always force Render backend in production
  if (
    typeof window !== "undefined" &&
    (window.location.hostname.includes("vercel.app") ||
      window.location.hostname.includes("onrender.com"))
  ) {
    wsBase = "wss://wall-finishing-system.onrender.com";
  }

  // ✅ Try both possible routes (player or trajectory)
  // FastAPI includes both: `/ws/play/{plan_id}` and `/api/trajectory/ws/play/{plan_id}`
  const wsUrl = `${wsBase}/ws/play/${plan_id}`;
  console.log("🎥 WebSocket URL:", wsUrl);

  return wsUrl;
}
