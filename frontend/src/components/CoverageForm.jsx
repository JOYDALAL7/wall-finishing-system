import { useState } from "react";

export default function CoverageForm({ onSubmit, loading }) {
  const [wallWidth, setWallWidth] = useState(5);
  const [wallHeight, setWallHeight] = useState(5);
  const [step, setStep] = useState(0.25);
  const [obstacles, setObstacles] = useState([]);

  function addObstacle() {
    setObstacles([...obstacles, { x: 1, y: 1, width: 0.25, height: 0.25 }]);
  }

  function updateObstacle(idx, key, val) {
    const copy = [...obstacles];
    copy[idx][key] = Number(val);
    setObstacles(copy);
  }

  function removeObstacle(idx) {
    const copy = [...obstacles];
    copy.splice(idx, 1);
    setObstacles(copy);
  }

  async function submit(e) {
    e.preventDefault();
    await onSubmit({
      wall_width: Number(wallWidth),
      wall_height: Number(wallHeight),
      step: Number(step),
      obstacles: obstacles.map((o) => ({
        x: Number(o.x),
        y: Number(o.y),
        width: Number(o.width),
        height: Number(o.height),
      })),
    });
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      {/* Section Title */}
      <h3 className="text-lg font-semibold text-blue-600 border-b border-gray-200 pb-2 flex items-center gap-2">
        🧩 Coverage Planner
      </h3>

      {/* Wall Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <label className="flex flex-col">
          <span className="text-sm text-gray-600 mb-1">Wall Width (m)</span>
          <input
            type="number"
            step="0.1"
            value={wallWidth}
            onChange={(e) => setWallWidth(e.target.value)}
            className="input"
          />
        </label>

        <label className="flex flex-col">
          <span className="text-sm text-gray-600 mb-1">Wall Height (m)</span>
          <input
            type="number"
            step="0.1"
            value={wallHeight}
            onChange={(e) => setWallHeight(e.target.value)}
            className="input"
          />
        </label>

        <label className="flex flex-col">
          <span className="text-sm text-gray-600 mb-1">Step (m)</span>
          <input
            type="number"
            step="0.01"
            value={step}
            onChange={(e) => setStep(e.target.value)}
            className="input"
          />
        </label>
      </div>

      {/* Obstacles */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Obstacles
          </h4>
          <button
            type="button"
            onClick={addObstacle}
            className="btn px-3 py-1 text-sm flex items-center gap-1"
          >
            ➕ Add Obstacle
          </button>
        </div>

        {obstacles.length > 0 ? (
          <div className="space-y-3">
            {obstacles.map((o, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm"
              >
                <h5 className="text-xs font-semibold text-blue-600 mb-2">
                  Obstacle #{idx + 1}
                </h5>

                <div className="grid grid-cols-5 gap-3 items-end">
                  {/* X */}
                  <div className="flex flex-col">
                    <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      X (m)
                    </label>
                    <input
                      className="input text-sm"
                      type="number"
                      value={o.x}
                      onChange={(e) => updateObstacle(idx, "x", e.target.value)}
                      placeholder="X"
                    />
                  </div>

                  {/* Y */}
                  <div className="flex flex-col">
                    <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      Y (m)
                    </label>
                    <input
                      className="input text-sm"
                      type="number"
                      value={o.y}
                      onChange={(e) => updateObstacle(idx, "y", e.target.value)}
                      placeholder="Y"
                    />
                  </div>

                  {/* Width */}
                  <div className="flex flex-col">
                    <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      Width (m)
                    </label>
                    <input
                      className="input text-sm"
                      type="number"
                      value={o.width}
                      onChange={(e) =>
                        updateObstacle(idx, "width", e.target.value)
                      }
                      placeholder="Width"
                    />
                  </div>

                  {/* Height */}
                  <div className="flex flex-col">
                    <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      Height (m)
                    </label>
                    <input
                      className="input text-sm"
                      type="number"
                      value={o.height}
                      onChange={(e) =>
                        updateObstacle(idx, "height", e.target.value)
                      }
                      placeholder="Height"
                    />
                  </div>

                  {/* Remove Button */}
                  <button
                    type="button"
                    onClick={() => removeObstacle(idx)}
                    className="btn-danger text-xs px-3 py-2"
                  >
                    ❌ Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 italic">
            No obstacles added yet.
          </p>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className={`btn ${
            loading ? "opacity-70 cursor-not-allowed" : ""
          } flex items-center gap-2`}
        >
          {loading ? (
            <>
              <span className="animate-spin">⚙️</span> Generating...
            </>
          ) : (
            <>
              🚀 Generate Path
            </>
          )}
        </button>
      </div>
    </form>
  );
}
