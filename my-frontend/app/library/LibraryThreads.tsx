import Link from "next/link";
import { Clock, MoreVertical, Trash2, Plus } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

// Utility function to truncate long titles
function truncateTitle(title: string, maxLength: number = 60) {
  if (!title) return "";
  if (title.length <= maxLength) return title;
  return title.substring(0, maxLength).trim() + "...";
}

export default function LibraryThreads({
  sessions,
  error,
  mutate,
  sessionsLoading,
}: any) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const router = useRouter();

  const handleDelete = async (threadId: string) => {
    setDeletingId(threadId);
    try {
      const accessToken =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;
      await fetch(`/api/chats/${threadId}`, {
        method: "DELETE",
        credentials: "include",
        headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      });
      mutate();
    } finally {
      setDeletingId(null);
    }
  };

  // Bulk delete handler
  const handleDeleteAll = async () => {
    // Placeholder for bulk delete, to be implemented when endpoint is ready
  };

  return (
    <div className="p-0 mt-0 w-full">
      <div className="flex items-center justify-between px-6 pt-6 pb-2">
        <h2 className="font-bold text-2xl flex items-center gap-2 text-green-950">
          <span className="inline-block">
            <Clock className="w-5 h-5 text-green-950" />
          </span>
          Threads
        </h2>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="p-2 rounded-full hover:bg-gray-100 text-gray-500"
                aria-label="More options"
              >
                <MoreVertical className="w-5 h-5 text-gray-500" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={handleDeleteAll}
                disabled={deletingId === "ALL" || sessions.length === 0}
                className="text-gray-500"
              >
                Delete Threads
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <button
            className="p-2 rounded-full hover:bg-gray-100 text-gray-500"
            aria-label="Add thread"
            onClick={() => router.push("/")}
          >
            <Plus className="w-5 h-5 text-gray-500" />
          </button>
        </div>
      </div>
      <hr className="border-gray-100" />
      {sessionsLoading ? (
        <div className="text-center text-gray-500 py-8">
          Loading sessions...
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-8">
          Error loading sessions.
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center text-gray-400 py-8">No sessions found.</div>
      ) : (
        <ul>
          {[...sessions]
            .sort((a, b) => {
              if (!a.last_updated) return 1;
              if (!b.last_updated) return -1;
              return (
                new Date(b.last_updated).getTime() -
                new Date(a.last_updated).getTime()
              );
            })
            .map((session: any, idx: number, arr: any[]) => (
              <li
                key={session.thread_id}
                className="px-6 py-4 group transition relative cursor-pointer hover:bg-gray-100"
                style={{
                  marginLeft: "-1px",
                  marginRight: "-1px",
                  width: "calc(100% + 2px)",
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <Link
                      href={`/search/${session.thread_id}`}
                      className="font-semibold text-lg text-green-950 group-hover:text-green-800 group-hover:underline"
                      title={session.title || session.thread_id}
                    >
                      {truncateTitle(session.title || session.thread_id)}
                    </Link>
                    <div className="text-gray-400 text-xs flex items-center gap-1 mt-1">
                      <Clock className="w-4 h-4" />
                      {session.last_updated
                        ? formatDate(session.last_updated)
                        : ""}
                    </div>
                  </div>
                  <button
                    className="ml-2 p-1 rounded-full hover:bg-gray-100 text-gray-500 transition"
                    title="Delete thread"
                    onClick={() => handleDelete(session.thread_id)}
                    disabled={deletingId === session.thread_id}
                  >
                    <Trash2
                      className={`w-5 h-5 text-gray-500 ${
                        deletingId === session.thread_id ? "animate-spin" : ""
                      }`}
                    />
                  </button>
                </div>
                {session.description && (
                  <div className="text-gray-500 text-sm truncate max-w-full mt-1">
                    {session.description}
                  </div>
                )}
                {idx < arr.length - 1 && (
                  <hr className="mt-4 border-gray-100" />
                )}
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
