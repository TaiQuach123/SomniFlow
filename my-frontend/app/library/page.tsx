"use client";
import { useAuth } from "@/hooks/useAuth";
import useSWR from "swr";
import LibraryHeader from "./LibraryHeader";
import LibraryThreads from "./LibraryThreads";
import { useState } from "react";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from "@/components/ui/pagination";

export default function LibraryPage() {
  const { user, loading } = useAuth();
  const {
    data: sessions = [],
    isLoading: sessionsLoading,
    mutate,
    error,
  } = useSWR(
    user ? "/api/chats" : null,
    (url) =>
      fetch(url, {
        credentials: "include",
        headers:
          typeof window !== "undefined" && localStorage.getItem("access_token")
            ? {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
              }
            : {},
      }).then((res) => res.json()),
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const threadsPerPage = 8;
  const sortedSessions = [...sessions].sort((a, b) => {
    if (!a.last_updated) return 1;
    if (!b.last_updated) return -1;
    return (
      new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime()
    );
  });
  const filteredSessions = sortedSessions.filter((session) =>
    (session.title || "").toLowerCase().includes(search.toLowerCase())
  );
  const totalPages = Math.ceil(filteredSessions.length / threadsPerPage);
  const paginatedSessions = filteredSessions.slice(
    (currentPage - 1) * threadsPerPage,
    currentPage * threadsPerPage
  );
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }
  if (!user) {
    return (
      <div className="p-8">You must be signed in to view your library.</div>
    );
  }

  return (
    <div className="flex flex-col items-center w-full min-h-screen bg-white relative">
      <LibraryHeader search={search} onSearchChange={setSearch} />
      <div className="w-full max-w-2xl mx-auto pt-1">
        <LibraryThreads
          sessions={paginatedSessions}
          error={error}
          mutate={mutate}
          sessionsLoading={sessionsLoading}
        />
        {totalPages > 1 && (
          <Pagination className="mt-6 mb-10">
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => handlePageChange(currentPage - 1)}
                  aria-disabled={currentPage === 1}
                  tabIndex={currentPage === 1 ? -1 : 0}
                  className={
                    currentPage === 1 ? "pointer-events-none opacity-50" : ""
                  }
                />
              </PaginationItem>
              {Array.from({ length: totalPages }, (_, i) => (
                <PaginationItem key={i}>
                  <PaginationLink
                    isActive={currentPage === i + 1}
                    onClick={(e) => {
                      e.preventDefault();
                      handlePageChange(i + 1);
                    }}
                    href="#"
                  >
                    {i + 1}
                  </PaginationLink>
                </PaginationItem>
              ))}
              <PaginationItem>
                <PaginationNext
                  onClick={() => handlePageChange(currentPage + 1)}
                  aria-disabled={currentPage === totalPages}
                  tabIndex={currentPage === totalPages ? -1 : 0}
                  className={
                    currentPage === totalPages
                      ? "pointer-events-none opacity-50"
                      : ""
                  }
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        )}
      </div>
    </div>
  );
}
