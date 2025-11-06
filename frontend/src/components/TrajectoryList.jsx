import { useEffect, useState } from "react";

export default function TrajectoryList({ fetchRecent, onSelectPlan }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPlans();
  }, []);

  async function loadPlans() {
    setLoading(true);
    try {
      const data = await fetchRecent();
      if (Array.isArray(data)) {
        // Remove duplicates and sort by most recent
        const uniquePlans = Array.from(new Map(data.map(p => [p.plan_id, p])).values());
        setPlans(uniquePlans.reverse());
      } else {
        setPlans([]);
      }
    } catch (err) {
      console.error("❌ Failed to load recent plans:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="card-header text-lg font-semibold text-blue-600 flex items-center gap-2">
          ⏱️ Recent Plans
        </h3>
        <button
          onClick={loadPlans}
          disabled={loading}
          className={`btn-secondary text-sm px-3 py-1 ${
            loading ? "opacity-60 cursor-not-allowed" : ""
          }`}
        >
          {loading ? "Refreshing..." : "🔄 Refresh"}
        </button>
      </div>

      {/* Plan list container */}
      <div className="max-h-72 overflow-y-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-3 space-y-2">
        {loading ? (
          <p className="text-center text-gray-500 text-sm py-8">Loading recent plans...</p>
        ) : plans.length === 0 ? (
          <p className="text-center text-gray-500 italic py-8">No recent plans found.</p>
        ) : (
          plans.map((p, idx) => (
            <div
              key={p.plan_id || idx}
              onClick={() => onSelectPlan(p.plan_id)}
              className="p-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm hover:shadow-md hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer transition-all"
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  #{plans.length - idx}
                </span>
                <span className="text-[10px] bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-[2px] rounded-full uppercase tracking-wide">
                  Plan
                </span>
              </div>

              <p className="text-sm font-medium text-gray-800 dark:text-gray-100 break-all">
                {p.plan_id}
              </p>

              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Created:{" "}
                {p.created_at
                  ? new Date(p.created_at).toLocaleString()
                  : "Unknown time"}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
