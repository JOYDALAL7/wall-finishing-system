import { useState, useEffect, useRef } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";

export default function PathVisualizer({ currentPlanId }) {
  const [points, setPoints] = useState([]);
  const [playing, setPlaying] = useState(false);
  const [index, setIndex] = useState(0);
  const [status, setStatus] = useState("Idle");

  const wsRef = useRef(null);

  // ✅ Build correct WebSocket URL (auto detect environment)
  const getWsUrl = () => {
    let base;
    if (
      typeof window !== "undefined" &&
      (window.location.hostname.includes("vercel.app") ||
        window.location.hostname.includes("onrender.com"))
    ) {
      base = "wss://wall-finishing-system.onrender.com";
    } else {
      base = "ws://127.0.0.1:8000";
    }
    return `${base}/ws/play/${currentPlanId}`;
  };

  const handlePlay = () => {
    if (!currentPlanId) {
      alert("⚠️ No plan selected to play!");
      return;
    }
    if (playing) return;

    setPlaying(true);
    setStatus("Connecting...");

    const ws = new WebSocket(getWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ Connected to WebSocket:", getWsUrl());
      setStatus("Streaming...");
      setPoints([]);
      setIndex(0);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        console.error("❌ WebSocket error:", data.error);
        setStatus("Error: " + data.error);
        setPlaying(false);
        ws.close();
        return;
      }

      setPoints((prev) => [...prev, { x: data.x, y: data.y, index: data.index }]);
      setIndex((prev) => prev + 1);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      setStatus("Completed");
      setPlaying(false);
    };

    ws.onerror = (err) => {
      console.error("⚠️ WebSocket Error:", err);
      setStatus("Error");
      setPlaying(false);
    };
  };

  const handleStop = () => {
    wsRef.current?.close();
    setPlaying(false);
    setStatus("Stopped");
  };

  const handleReset = () => {
    handleStop();
    setPoints([]);
    setIndex(0);
    setStatus("Idle");
  };

  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="card-header flex items-center gap-2">
          📈 Path Visualizer
          <span className="text-sm text-gray-500">
            {currentPlanId ? `(Plan ID: ${currentPlanId.slice(0, 8)}...)` : ""}
          </span>
        </h3>
        <div className="flex gap-2">
          <button
            onClick={handlePlay}
            disabled={playing}
            className={`btn px-4 py-1 text-sm ${playing ? "opacity-60 cursor-not-allowed" : ""}`}
          >
            ▶ Play
          </button>
          <button
            onClick={handleStop}
            disabled={!playing}
            className={`btn-secondary px-4 py-1 text-sm ${!playing ? "opacity-60 cursor-not-allowed" : ""}`}
          >
            ⏹ Stop
          </button>
          <button onClick={handleReset} className="btn-danger px-4 py-1 text-sm">
            🔄 Reset
          </button>
        </div>
      </div>

      <div className="text-sm text-gray-700 mb-3">
        <p>
          <span className="font-medium text-blue-600">Status:</span> {status}
        </p>
      </div>

      <div
        className={`border border-gray-200 rounded-xl p-3 bg-gray-50 transition-all duration-300 ${
          playing ? "shadow-inner" : ""
        }`}
        style={{ height: 360 }}
      >
        {points.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400 italic">
            No path points yet — click "Play" to visualize the coverage path.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="x" type="number" domain={["dataMin", "dataMax"]} />
              <YAxis dataKey="y" type="number" domain={["dataMin", "dataMax"]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #e5e7eb",
                }}
              />
              <Line dot={false} dataKey="y" stroke="#2563eb" strokeWidth={2} isAnimationActive={false} />
              {points[index] && (
                <ReferenceDot
                  x={points[index].x}
                  y={points[index].y}
                  r={6}
                  fill="#ef4444"
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="text-xs text-gray-500 mt-3 flex justify-between">
        <span>
          Total Points: <span className="text-blue-600 font-medium">{points.length}</span>
        </span>
        <span>Index: <span className="font-medium">{index}</span></span>
        <span>
          {status === "Completed" && <span className="badge badge-success">✅ Completed</span>}
          {status === "Streaming..." && (
            <span className="badge badge-warning animate-pulse">🔵 Live Streaming</span>
          )}
          {status === "Error" && <span className="badge badge-error">❌ Error</span>}
        </span>
      </div>
    </div>
  );
}
