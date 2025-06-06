"use client";
import useSWR from "swr";
import Link from "next/link";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function LibraryPage() {
  const { data: sessions, mutate } = useSWR("/api/chats", fetcher);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Your Sessions</h1>
      <button
        onClick={() => mutate()} // Manual refresh button
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Refresh
      </button>
      <ul>
        {sessions?.map((session: any) => (
          <li key={session.thread_id} className="mb-2">
            <Link
              href={`/search/${session.thread_id}`}
              className="text-blue-600 underline"
            >
              {session.title || session.thread_id}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
