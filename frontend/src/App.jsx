import { useState } from "react";
import CoverageForm from "./components/CoverageForm";
import PathVisualizer from "./components/PathVisualizer";
import TrajectoryList from "./components/TrajectoryList";
import { useCoverageApi } from "./hooks/useApi";

export default function App() {
  const { createPlan, fetchRecent, fetchByPlan, loading } = useCoverageApi();

  const [currentPlanId, setCurrentPlanId] = useState(null);
  const [points, setPoints] = useState([]);
  const [message, setMessage] = useState("");

  // 🧠 Generate new coverage path
  async function handleCreate(params) {
    setMessage("");
    try {
      const res = await createPlan(params);
      if (res?.plan_id && res?.points) {
        setCurrentPlanId(res.plan_id);
        setPoints(res.points);
        setMessage(`✅ Plan ${res.plan_id} created with ${res.points.length} points`);
      } else {
        throw new Error("Invalid response from backend");
      }
    } catch (err) {
      console.error("Error creating plan:", err);
      setMessage("❌ Error creating plan. Check console for details.");
    }
  }

  // 🧠 Load an existing plan by ID
  async function handleSelectPlan(plan_id) {
    setMessage("");
    try {
      const rows = await fetchByPlan(plan_id);
      if (!rows || rows.length === 0) {
        setMessage(`⚠️ No trajectory data found for plan ${plan_id}`);
        return;
      }
      const pts = rows.map((r) => ({
        x: r.x,
        y: r.y,
        timestamp: r.timestamp,
      }));
      setCurrentPlanId(plan_id);
      setPoints(pts);
      setMessage(`📂 Loaded plan ${plan_id} (${pts.length} points)`);
    } catch (err) {
      console.error("Error loading plan:", err);
      setMessage("❌ Error loading plan.");
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 text-gray-800 font-poppins">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 shadow-md sticky top-0 z-50">
        <h1 className="text-center text-3xl font-bold tracking-wide">
          🧱 Wall Finishing Coverage Planner
        </h1>
        <p className="text-center text-sm opacity-90">Autonomous Path Planning Visualizer</p>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Left Sidebar */}
        <div className="col-span-1 space-y-6">
          {/* Coverage Planner Form */}
          <div className="card">
            <h2 className="card-header">🧩 Coverage Planner</h2>
            <CoverageForm onSubmit={handleCreate} loading={loading} />
          </div>

          {/* Status Section */}
          <div className="card">
            <h2 className="card-header">📡 Status</h2>
            <div className="text-sm text-gray-700 mt-2">
              {loading ? (
                <span className="text-blue-600 animate-pulse">⏳ Generating path...</span>
              ) : (
                message || "Idle"
              )}
            </div>
            {currentPlanId && (
              <div className="text-xs text-gray-500 mt-2 break-all">
                Plan ID: <span className="font-mono text-blue-600">{currentPlanId}</span>
              </div>
            )}
          </div>

          {/* Recent Plans */}
          <div className="card">
            <h2 className="card-header">🕒 Recent Plans</h2>
            <TrajectoryList fetchRecent={fetchRecent} onSelectPlan={handleSelectPlan} />
          </div>
        </div>

        {/* Visualization Panel */}
        <div className="col-span-2 space-y-6">
          <div className="card">
            <h2 className="card-header">📈 Path Visualization</h2>
            <PathVisualizer
              key={currentPlanId}
              currentPlanId={currentPlanId}
              points={points}
            />
          </div>

          {/* Instructions */}
          <div className="card">
            <h2 className="card-header">💡 Instructions</h2>
            <ul className="text-sm text-gray-600 mt-2 list-disc list-inside space-y-1">
              <li>Enter wall size, step, and obstacles to generate a path.</li>
              <li>Use “Recent Plans” to view and replay older plans.</li>
              <li>Click “Play” to stream path points live from the backend.</li>
              <li>Click “Reset” to clear the canvas for a new simulation.</li>
            </ul>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-sm text-gray-500">
        Built with ❤️ by <span className="text-blue-600 font-medium">Joy Dalal</span>
      </footer>
    </div>
  );
}
