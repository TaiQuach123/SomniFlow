import React, { useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Search } from "lucide-react";
import { AiFillFilePdf } from "react-icons/ai";
import Sources from "./Sources";

interface StreamingInteractionProps {
  userQuery: string;
  showTimeline: boolean;
  taskTimeline: any[];
  showSkeleton: boolean;
  streamedAnswer: string;
  sources: any[];
}

function getIcon(type: string, domain?: string) {
  console.log(type, domain);
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

export default function StreamingInteraction({
  userQuery,
  showTimeline,
  taskTimeline,
  showSkeleton,
  streamedAnswer,
  sources,
}: StreamingInteractionProps) {
  // Collapsed state for each parent task
  const [collapsed, setCollapsed] = useState<{ [k: number]: boolean }>({});

  const toggleCollapse = (idx: number) => {
    setCollapsed((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="mb-8 w-full">
      <h2 className="font-bold text-2xl text-left mt-16 ml-4">{userQuery}</h2>
      <div className="w-full px-4 mt-4">
        {showTimeline ? (
          <div className="w-full my-8">
            <div className="font-semibold mb-2"></div>
            <ol className="border-l-2 border-yellow-400 pl-4">
              {taskTimeline.map((task, idx) => (
                <li key={idx} className="mb-4 relative">
                  <div className="absolute -left-2 top-1 w-3 h-3 bg-yellow-400 rounded-full border-2 border-white" />
                  {task.type === "retrieval" || task.type === "webSearch" ? (
                    <div className="bg-white rounded shadow p-4">
                      <div
                        className="flex items-center justify-between cursor-pointer"
                        onClick={() => toggleCollapse(idx)}
                      >
                        <div className="font-semibold mb-2">
                          {task.type === "retrieval"
                            ? "Searching local data"
                            : "Searching the web"}
                        </div>
                        <button
                          className="ml-2 text-xs text-gray-500"
                          aria-label="Toggle collapse"
                        >
                          {collapsed[idx] ? "▶" : "▼"}
                        </button>
                      </div>
                      {!collapsed[idx] && (
                        <>
                          <div className="mb-2">
                            <span className="font-medium">Searching</span>
                            <ul className="ml-4 mt-1">
                              {Array.isArray(task.searching) &&
                              task.searching.length > 0 ? (
                                task.searching.map(
                                  (query: string, i: number) => (
                                    <li
                                      key={i}
                                      className="flex items-center gap-2 text-gray-700 text-sm mb-1"
                                    >
                                      <Search className="w-4 h-4 text-yellow-500" />
                                      <span>{query}</span>
                                    </li>
                                  )
                                )
                              ) : (
                                <li className="text-gray-400 text-sm">
                                  No queries
                                </li>
                              )}
                            </ul>
                          </div>
                          <div>
                            <span className="font-medium">Reading</span>
                            <div className="flex flex-wrap gap-2 ml-4 mt-2">
                              {Array.isArray(task.reading) &&
                              task.reading.length > 0 ? (
                                task.reading.map((src: any, i: number) => (
                                  <a
                                    key={i}
                                    href={
                                      src.url && src.url.startsWith("http")
                                        ? src.url
                                        : undefined
                                    }
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded shadow text-sm hover:bg-blue-100 transition cursor-pointer"
                                    title={src.title || src.url}
                                  >
                                    {getIcon(
                                      src.type,
                                      src.domain ||
                                        (src.url &&
                                          src.url.match(
                                            /https?:\/\/(www\.)?([^\/]+)/
                                          )?.[2])
                                    )}
                                    <span className="font-semibold">
                                      {src.type === "local"
                                        ? src.url.split("/").pop()
                                        : src.domain ||
                                          (src.url &&
                                            src.url.match(
                                              /https?:\/\/(www\.)?([^\/]+)/
                                            )?.[2])}
                                    </span>
                                  </a>
                                ))
                              ) : (
                                <span className="text-gray-400 text-sm">
                                  No sources
                                </span>
                              )}
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="ml-4 text-sm text-gray-700">
                      {typeof task.label === "string"
                        ? task.label
                        : JSON.stringify(task.label)}
                    </div>
                  )}
                </li>
              ))}
            </ol>
          </div>
        ) : showSkeleton ? (
          <div className="w-full my-8">
            <div className="mb-2 font-semibold">Preparing answer...</div>
            <div className="w-full">
              <Skeleton className="h-8 w-full mb-2" />
              <Skeleton className="h-8 w-5/6 mb-2" />
              <Skeleton className="h-8 w-2/3" />
            </div>
          </div>
        ) : streamedAnswer ? (
          <div className="w-full my-8">
            <Sources sources={sources || []} />
            <div className="p-4 bg-green-50 rounded">
              <span className="font-semibold"></span>
              <span>{streamedAnswer}</span>
              <span className="animate-pulse text-gray-400 ml-2">|</span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
