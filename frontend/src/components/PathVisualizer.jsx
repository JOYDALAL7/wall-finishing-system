import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import { getTrajectoriesByPlan } from "../api/api";

export default function PathVisualizer({ currentPlanId }) {
  const [points, setPoints] = useState([]);
  const [playing, setPlaying] = useState(false);
  const [index, setIndex] = useState(0);
  const [status, setStatus] = useState("Idle");
  const intervalRef = useRef(null);

  // ✅ Fetch trajectory points from backend
  const loadTrajectory = async () => {
    if (!currentPlanId) {
      alert("⚠️ No plan selected!");
      return;
    }
    setStatus("Loading...");
    try {
      const data = await getTrajectoriesByPlan(currentPlanId);
      if (!data || !data.length) {
        setStatus("No trajectory data found");
        return;
      }
      setPoints(data);
      setStatus("Loaded ✅");
      setIndex(0);
    } catch (error) {
      console.error("❌ Error loading trajectory:", error);
      setStatus("Error loading data");
    }
  };

  // ✅ Play animation smoothly
  const handlePlay = () => {
    if (!points.length) {
      alert("⚠️ Load trajectory first!");
      return;
    }
    if (playing) return;

    setPlaying(true);
    setStatus("Playing ▶");

    let i = index;
    intervalRef.current = setInterval(() => {
      i++;
      if (i >= points.length) {
        clearInterval(intervalRef.current);
        setPlaying(false);
        setStatus("Completed ✅");
        return;
      }
      setIndex(i);
    }, 60); // adjust speed (lower = faster)
  };

  const handlePause = () => {
    clearInterval(intervalRef.current);
    setPlaying(false);
    setStatus("Paused ⏸");
  };

  const handleReset = () => {
    clearInterval(intervalRef.current);
    setPlaying(false);
    setIndex(0);
    setStatus("Reset 🔄");
  };

  useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);

  const visiblePoints = points.slice(0, index + 1);
  const current = points[index];

  return (
    <div className="card bg-white p-5 rounded-2xl shadow-md border border-gray-100 transition-all duration-300 hover:shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          🧠 Path Visualizer{" "}
          {currentPlanId && (
            <span className="text-sm text-gray-400">
              (ID: {currentPlanId.slice(0, 8)}…)
            </span>
          )}
        </h3>

        <div className="flex gap-2">
          <button
            onClick={loadTrajectory}
            className="px-3 py-1 rounded-md bg-blue-500 text-white text-sm hover:bg-blue-600"
          >
            🔁 Load
          </button>

          {!playing ? (
            <button
              onClick={handlePlay}
              className="px-3 py-1 rounded-md bg-green-500 text-white text-sm hover:bg-green-600"
            >
              ▶ Play
            </button>
          ) : (
            <button
              onClick={handlePause}
              className="px-3 py-1 rounded-md bg-yellow-500 text-white text-sm hover:bg-yellow-600"
            >
              ⏸ Pause
            </button>
          )}

          <button
            onClick={handleReset}
            className="px-3 py-1 rounded-md bg-red-500 text-white text-sm hover:bg-red-600"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="text-sm text-gray-700 mb-3">
        <p>
          <span className="font-medium text-blue-600">Status:</span> {status}
        </p>
      </div>

      {/* Chart */}
      <div
        className={`border border-gray-200 rounded-xl p-3 bg-gray-50 transition-all duration-300 ${
          playing ? "shadow-inner" : ""
        }`}
        style={{ height: 380 }}
      >
        {!points.length ? (
          <div className="flex items-center justify-center h-full text-gray-400 italic">
            Load a plan to visualize coverage.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={visiblePoints}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="x"
                type="number"
                domain={["dataMin", "dataMax"]}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                dataKey="y"
                type="number"
                domain={["dataMin", "dataMax"]}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #e5e7eb",
                }}
              />

              {/* 🔹 Glowing trail */}
              <Line
                dataKey="y"
                dot={false}
                stroke="#2563eb"
                strokeWidth={3}
                strokeOpacity={0.9}
                isAnimationActive={false}
                filter="url(#glow)"
              />

              {/* 🔴 Animated moving dot */}
              <AnimatePresence>
                {current && (
                  <motion.circle
                    key={index}
                    cx={current.x}
                    cy={current.y}
                    r={7}
                    fill="#ef4444"
                    stroke="white"
                    strokeWidth={2}
                    animate={{ scale: [0.8, 1.3, 0.8] }}
                    transition={{ duration: 0.6, repeat: Infinity }}
                  />
                )}
              </AnimatePresence>
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer */}
      <div className="text-xs text-gray-500 mt-3 flex justify-between">
        <span>
          Total Points:{" "}
          <span className="text-blue-600 font-medium">{points.length}</span>
        </span>
        <span>
          Index: <span className="font-medium">{index}</span>
        </span>
        <span>
          {status.includes("Playing") && (
            <span className="text-yellow-600 font-semibold animate-pulse">
              🔵 Playing
            </span>
          )}
          {status.includes("Completed") && (
            <span className="text-green-600 font-semibold">✅ Completed</span>
          )}
          {status.includes("Error") && (
            <span className="text-red-600 font-semibold">❌ Error</span>
          )}
        </span>
      </div>

      {/* ✅ SVG Filter for glow effect */}
      <svg style={{ height: 0 }}>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>
    </div>
  );
}
