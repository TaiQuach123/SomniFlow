import React, { useState } from "react";
import { AiFillFilePdf } from "react-icons/ai";
import { FiChevronLeft, FiChevronRight } from "react-icons/fi";

function getIcon(type: string, domain?: string) {
  if (type === "local")
    return <AiFillFilePdf className="text-red-600 w-4 h-4" />;
  if (type === "web" && domain) {
    return (
      <img
        src={`https://icon.horse/icon/${domain}`}
        alt={domain}
        className="w-4 h-4 rounded-full object-cover"
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

const CARDS_PER_VIEW = 4;

export default function Sources({ sources }: { sources: any[] }) {
  const [startIdx, setStartIdx] = useState(0);
  if (!sources || sources.length === 0) return null;
  const endIdx = Math.min(startIdx + CARDS_PER_VIEW, sources.length);
  const canScrollLeft = startIdx > 0;
  const canScrollRight = endIdx < sources.length;

  const handlePrev = () => {
    setStartIdx((prev) => Math.max(prev - CARDS_PER_VIEW, 0));
  };
  const handleNext = () => {
    setStartIdx((prev) =>
      Math.min(
        prev + CARDS_PER_VIEW,
        sources.length - CARDS_PER_VIEW < 0
          ? 0
          : sources.length - CARDS_PER_VIEW
      )
    );
  };

  return (
    <div className="bg-white dark:bg-neutral-900 rounded mb-4 flex items-center pb-2">
      {canScrollLeft && (
        <button
          onClick={handlePrev}
          className="p-1 mr-1 rounded hover:bg-gray-200 dark:hover:bg-neutral-700"
          aria-label="Previous sources"
        >
          <FiChevronLeft className="w-5 h-5" />
        </button>
      )}
      <div className="flex flex-nowrap gap-2 overflow-x-auto scrollbar-hide">
        {sources.slice(startIdx, endIdx).map((src, idx) => {
          const domain =
            src.domain ||
            (src.url && src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2]);
          const filename =
            src.type === "local" ? src.url.split("/").pop() : undefined;
          return (
            <a
              key={startIdx + idx}
              href={src.type === "web" ? src.url : undefined}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-start gap-1 px-4 py-3 bg-gray-100 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-xl shadow-sm hover:bg-blue-100 dark:hover:bg-neutral-700 transition cursor-pointer min-w-[190px] max-w-[190px] w-[190px]"
              title={src.title || src.url}
              style={{ textDecoration: "none" }}
            >
              <div className="flex items-center gap-1 mb-1 h-4">
                {getIcon(src.type, domain)}
                <span className="text-xs text-gray-500 font-medium truncate h-4 flex items-center">
                  {src.type === "local" ? filename : domain}
                </span>
              </div>
              <span
                className="font-semibold text-gray-900 dark:text-gray-100 w-full text-xs line-clamp-2"
                style={{ lineHeight: 1.2 }}
              >
                {src.title || (src.type === "local" ? filename : domain)}
              </span>
            </a>
          );
        })}
      </div>
      {canScrollRight && (
        <button
          onClick={handleNext}
          className="p-1 ml-1 rounded hover:bg-gray-200 dark:hover:bg-neutral-700"
          aria-label="Next sources"
        >
          <FiChevronRight className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
