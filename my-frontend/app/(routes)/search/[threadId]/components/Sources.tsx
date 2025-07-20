import React, { useState } from "react";
import { AiFillFilePdf } from "react-icons/ai";

// Utility function to truncate long filenames
function truncateFilename(filename: string, maxLength: number = 30): string {
  if (!filename || filename.length <= maxLength) {
    return filename;
  }

  const extension = filename.split(".").pop();
  const nameWithoutExt = filename.substring(0, filename.lastIndexOf("."));

  if (!extension || nameWithoutExt.length <= 3) {
    return filename.substring(0, maxLength - 3) + "...";
  }

  const maxNameLength = maxLength - extension.length - 4; // 4 for "..." and "."
  if (maxNameLength <= 0) {
    return "..." + extension;
  }

  return nameWithoutExt.substring(0, maxNameLength) + "..." + extension;
}

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

// Function to get the proper URL for a source
function getSourceUrl(src: any) {
  if (src.type === "web") {
    return src.url;
  } else if (src.type === "local") {
    // For local PDF files, remove database/ prefix if it exists to avoid duplication
    let cleanUrl = src.url;
    if (cleanUrl.startsWith("database/")) {
      cleanUrl = cleanUrl.substring(9); // Remove "database/" prefix
    }
    return `/database/${cleanUrl}`;
  }
  return undefined;
}

const CARDS_PER_VIEW = 4;
const SOURCES_PER_PAGE = 5;

export default function Sources({
  sources,
  variant = "horizontal",
}: {
  sources: any[];
  variant?: "horizontal" | "vertical";
}) {
  // Horizontal (card) layout for Answer tab
  if (variant === "horizontal") {
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
            <span className="sr-only">Previous</span>
            {/* Use your icon here if needed */}
            &#8592;
          </button>
        )}
        <div className="flex flex-nowrap gap-2 overflow-x-auto scrollbar-hide">
          {sources.slice(startIdx, endIdx).map((src, idx) => {
            const domain =
              src.domain ||
              (src.url && src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2]);
            const filename =
              src.type === "local" ? src.url.split("/").pop() : undefined;
            const sourceUrl = getSourceUrl(src);
            return (
              <a
                key={startIdx + idx}
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex flex-col items-start gap-1 px-4 py-3 bg-gray-100 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-xl shadow-sm hover:bg-blue-100 dark:hover:bg-neutral-700 transition cursor-pointer min-w-[190px] max-w-[190px] w-[190px]"
                title={src.title || src.url}
                style={{ textDecoration: "none" }}
              >
                <div className="flex items-center gap-1 mb-1 h-4">
                  {getIcon(src.type, domain)}
                  <span className="text-xs text-gray-500 font-medium truncate h-4 flex items-center">
                    {src.type === "local"
                      ? truncateFilename(filename, 18)
                      : domain}
                  </span>
                </div>
                <span
                  className="font-semibold text-gray-900 dark:text-gray-100 w-full text-xs line-clamp-2"
                  style={{ lineHeight: 1.2 }}
                >
                  {src.title ||
                    (src.type === "local"
                      ? truncateFilename(filename, 25)
                      : domain)}
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
            <span className="sr-only">Next</span>
            {/* Use your icon here if needed */}
            &#8594;
          </button>
        )}
      </div>
    );
  }

  // Vertical (list) layout for Sources tab
  const [visibleCount, setVisibleCount] = useState(SOURCES_PER_PAGE);
  if (!sources || sources.length === 0) return null;
  const showLoadMore = sources.length > visibleCount;
  const visibleSources = sources.slice(0, visibleCount);

  return (
    <div className="bg-white dark:bg-neutral-900 rounded mb-4 flex flex-col pb-2">
      <ul className="divide-y divide-gray-100 dark:divide-neutral-800">
        {visibleSources.map((src, idx) => {
          const domain =
            src.domain ||
            (src.url && src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2]);
          const filename =
            src.type === "local" ? src.url.split("/").pop() : undefined;
          const refNum = src.ref || idx + 1;
          const sourceUrl = getSourceUrl(src);
          return (
            <li
              key={idx}
              className="px-4 py-4 group hover:bg-gray-50 dark:hover:bg-neutral-800 transition"
            >
              <div className="flex flex-row items-start gap-3">
                {/* Icon on top left */}
                <div className="flex-shrink-0 mt-0.5">
                  {getIcon(src.type, domain)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-xs font-bold text-gray-400">
                      {refNum}.
                    </span>
                    <span className="text-xs font-semibold text-gray-500 truncate max-w-[160px]">
                      {src.type === "local"
                        ? truncateFilename(filename, 18)
                        : domain}
                    </span>
                  </div>
                  <a
                    href={sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-gray-900 dark:text-gray-100 group-hover:underline block text-base truncate mt-0.5"
                    title={src.title || src.url}
                  >
                    {src.title ||
                      (src.type === "local"
                        ? truncateFilename(filename, 30)
                        : domain)}
                  </a>
                  {(src.description ||
                    (src.type === "local" &&
                      (src.metadata?.summary ||
                        src.summary ||
                        src.content?.summary))) && (
                    <div className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {src.description ||
                        (src.type === "local"
                          ? src.metadata?.summary ||
                            src.summary ||
                            src.content?.summary
                          : "")}
                    </div>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
      {showLoadMore && (
        <button
          className="mt-2 mx-auto px-4 py-1 text-sm rounded bg-gray-100 dark:bg-neutral-800 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-neutral-700 transition"
          onClick={() => setVisibleCount((c) => c + SOURCES_PER_PAGE)}
        >
          Load more
        </button>
      )}
    </div>
  );
}
