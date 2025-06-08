import React from "react";
import { AiFillFilePdf } from "react-icons/ai";

function getIcon(type: string, domain?: string) {
  if (type === "local")
    return <AiFillFilePdf className="text-red-600 w-5 h-5" />;
  if (type === "web" && domain) {
    return (
      <img
        src={`https://icon.horse/icon/${domain}`}
        alt={domain}
        className="w-5 h-5 rounded"
        style={{ background: "#fff" }}
        onError={(e) => {
          (e.target as HTMLImageElement).src = "/favicon.ico";
        }}
      />
    );
  }
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
      <div className="font-semibold mb-2"></div>
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
            {getIcon(
              src.type,
              src.domain ||
                (src.url && src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2])
            )}
            <span className="font-semibold">
              {src.type === "local"
                ? src.url.split("/").pop()
                : src.domain ||
                  (src.url &&
                    src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2])}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
}
