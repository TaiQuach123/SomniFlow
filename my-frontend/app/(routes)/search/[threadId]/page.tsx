"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";

export default function ThreadPage() {
  const params = useParams();
  const threadId = params?.threadId;
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    if (!threadId) return;
    const accessToken =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    fetch(`/api/chats/${threadId}`, {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setSession(data);
        console.log("Chat history for thread", threadId, data);
      })
      .catch((err) => {
        console.error("Failed to fetch chat history", err);
      });
  }, [threadId]);

  // Dummy user avatar
  const avatarUrl =
    session?.session_metadata?.avatar_url ||
    "https://ssl.gstatic.com/accounts/ui/avatar_2x.png";

  // Find the latest user message and extract its created_at from metadata
  let userMessageTime = "";
  if (session?.messages && Array.isArray(session.messages)) {
    const latestUserMsg = [...session.messages]
      .reverse()
      .find((msg) => msg.role === "user" && msg.metadata);
    if (latestUserMsg) {
      try {
        const meta = JSON.parse(latestUserMsg.metadata);
        if (meta.created_at) userMessageTime = meta.created_at;
      } catch (e) {
        // ignore JSON parse error
      }
    }
  }

  console.log("userMessageTime passed to Header:", userMessageTime);

  return (
    <div className="flex flex-col items-center min-h-screen relative w-full">
      <Header avatarUrl={avatarUrl} userMessageTime={userMessageTime} />
      <div className="w-full max-w-4xl mx-auto mt px-4">
        <ChatWindow messages={session?.messages || []} />
      </div>
    </div>
  );
}
