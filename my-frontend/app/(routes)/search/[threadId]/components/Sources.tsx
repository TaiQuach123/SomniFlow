import React from "react";

function getIcon(type: string, domain?: string) {
  if (type === "local")
    return (
      <span role="img" aria-label="pdf">
        📄
      </span>
    );
  if (type === "web")
    return (
      <span role="img" aria-label="web">
        🌐
      </span>
    );
  return (
    <span role="img" aria-label="file">
      📁
    </span>
  );
}

export default function Sources({ sources }: { sources: any[] }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="p-4 bg-blue-50 rounded mb-4">
      <div className="font-semibold mb-2">Sources:</div>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, idx) => (
          <a
            key={idx}
            href={src.type === "web" ? src.url : undefined}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1 bg-white rounded shadow text-sm hover:bg-blue-100 transition cursor-pointer min-w-[120px]"
            title={src.title || src.url}
          >
            <span className="font-bold text-xs text-gray-500 mr-1">
              [{src.ref}]
            </span>
            {getIcon(src.type, src.domain)}
            <span className="font-semibold">
              {src.type === "local"
                ? src.url.split("/").pop()
                : src.domain || src.url}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
}
