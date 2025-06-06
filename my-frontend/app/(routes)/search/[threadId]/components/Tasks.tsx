import React from "react";

export default function Tasks({ tasks }: { tasks: any[] }) {
  return (
    <div className="p-4 bg-yellow-50 rounded">
      <div className="font-semibold mb-2">Tasks Timeline:</div>
      <ol className="border-l-2 border-yellow-400 pl-4">
        {tasks.map((task, idx) => (
          <li key={idx} className="mb-4 relative">
            <div className="absolute -left-2 top-1 w-3 h-3 bg-yellow-400 rounded-full border-2 border-white" />
            <div className="ml-4 text-sm text-gray-700">
              {typeof task.data === "string"
                ? task.data
                : JSON.stringify(task.data)}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
