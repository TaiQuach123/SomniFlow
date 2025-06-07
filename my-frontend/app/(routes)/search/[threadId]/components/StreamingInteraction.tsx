import React from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Search } from "lucide-react";

interface StreamingInteractionProps {
  userQuery: string;
  showTimeline: boolean;
  taskTimeline: any[];
  showSkeleton: boolean;
  streamedAnswer: string;
}

export default function StreamingInteraction({
  userQuery,
  showTimeline,
  taskTimeline,
  showSkeleton,
  streamedAnswer,
}: StreamingInteractionProps) {
  return (
    <div className="mb-8 w-full">
      <h2 className="font-bold text-2xl text-left mt-16 ml-4">{userQuery}</h2>
      <div className="w-full px-4 mt-4">
        {showTimeline ? (
          <div className="w-full my-8">
            <div className="font-semibold mb-2">Task Timeline</div>
            <ol className="border-l-2 border-yellow-400 pl-4">
              {taskTimeline.map((task, idx) => (
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
                            <li className="text-gray-400 text-sm">
                              No queries
                            </li>
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
                    <div className="ml-4">
                      {typeof task.data === "string"
                        ? task.data
                        : JSON.stringify(task.data)}
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
            <div className="p-4 bg-green-50 rounded">
              <span className="font-semibold">Answer: </span>
              <span>{streamedAnswer}</span>
              <span className="animate-pulse text-gray-400 ml-2">|</span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
