import React from "react";
import { Skeleton } from "@/components/ui/skeleton";

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
                  <div className="ml-4">
                    {typeof task.data === "string"
                      ? task.data
                      : JSON.stringify(task.data)}
                  </div>
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
