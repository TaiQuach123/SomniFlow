import React from "react";
import { Search } from "lucide-react";

export default function Tasks({ tasks }: { tasks: any[] }) {
  return (
    <div className="p-4 bg-yellow-50 rounded">
      <div className="font-semibold mb-2">Tasks Timeline:</div>
      <ol className="border-l-2 border-yellow-400 pl-4">
        {tasks.map((task, idx) => (
          <li key={idx} className="mb-4 relative">
            <div className="absolute -left-2 top-1 w-3 h-3 bg-yellow-400 rounded-full border-2 border-white" />
            {task.type === "step_retrieval" ||
            task.type === "step_web_search" ? (
              <div className="bg-white rounded shadow p-4">
                <div className="font-semibold mb-2">
                  {task.type === "step_retrieval"
                    ? "Searching local data"
                    : "Searching the web"}
                </div>
                <div className="mb-2">
                  <span className="font-medium">Searching</span>
                  <ul className="ml-4 mt-1">
                    {Array.isArray(task.data) && task.data.length > 0 ? (
                      task.data.map((query: string, i: number) => (
                        <li
                          key={i}
                          className="flex items-center gap-2 text-gray-700 text-sm mb-1"
                        >
                          <Search className="w-4 h-4 text-yellow-500" />
                          <span>{query}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-gray-400 text-sm">No queries</li>
                    )}
                  </ul>
                </div>
                <div>
                  <span className="font-medium">Reading</span>
                  <ul className="ml-4 mt-1 text-gray-400 text-sm">
                    {/* Reading section intentionally left empty for now */}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="ml-4 text-sm text-gray-700">
                {typeof task.data === "string"
                  ? task.data
                  : JSON.stringify(task.data)}
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
