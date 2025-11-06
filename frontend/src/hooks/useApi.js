import { useState } from "react";
import axios from "axios";

// ✅ Use your backend URL from .env (or default to localhost)
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function useCoverageApi() {
  const [loading, setLoading] = useState(false);

  // Create a new wall finishing plan
  async function createPlan(params) {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/coverage/`, params);
      return res.data;
    } finally {
      setLoading(false);
    }
  }

  // Fetch recently created plans
  async function fetchRecent() {
    try {
      const res = await axios.get(`${API_URL}/api/trajectory/recent`);
      return res.data;
    } catch (err) {
      console.error("Failed to fetch recent plans:", err);
      return [];
    }
  }

  // Fetch a plan’s trajectory by ID
  async function fetchByPlan(plan_id) {
    try {
      const res = await axios.get(`${API_URL}/api/trajectory/${plan_id}`);
      return res.data;
    } catch (err) {
      console.error(`Failed to fetch plan ${plan_id}:`, err);
      return [];
    }
  }

  return { createPlan, fetchRecent, fetchByPlan, loading };
}
