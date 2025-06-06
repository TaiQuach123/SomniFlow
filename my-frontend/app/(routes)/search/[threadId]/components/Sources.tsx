import React from "react";

export default function Sources({ sources }: { sources: any[] }) {
  return (
    <div className="p-4 bg-blue-50 rounded">
      <div className="font-semibold mb-2">Sources:</div>
      <ul className="list-disc pl-5">
        {sources.map((src, idx) => (
          <li key={idx}>
            {src && src.data
              ? typeof src.data === "string"
                ? src.data
                : JSON.stringify(src.data)
              : typeof src === "string"
              ? src
              : JSON.stringify(src)}
          </li>
        ))}
      </ul>
    </div>
  );
}
