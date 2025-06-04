import React from "react";

export default function Tasks({ tasks }: { tasks: string[] }) {
  return (
    <div className="p-4 bg-yellow-50 rounded">
      <div className="font-semibold mb-2">Tasks:</div>
      <ul className="list-none pl-0">
        {tasks.map((task, idx) => (
          <li key={idx} className="flex items-center gap-2">
            <input type="checkbox" className="accent-yellow-500" />
            <span>{task}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
