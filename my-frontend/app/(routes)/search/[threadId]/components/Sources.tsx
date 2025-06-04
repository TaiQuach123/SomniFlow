import React from "react";

export default function Sources({ sources }: { sources: string[] }) {
  return (
    <div className="p-4 bg-blue-50 rounded">
      <div className="font-semibold mb-2">Sources:</div>
      <ul className="list-disc pl-5">
        {sources.map((src, idx) => (
          <li key={idx}>{src}</li>
        ))}
      </ul>
    </div>
  );
}
