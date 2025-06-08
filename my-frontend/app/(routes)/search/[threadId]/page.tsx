"use client";
import React, { useEffect, useState, useRef } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import { Skeleton } from "@/components/ui/skeleton";
import StreamingInteraction from "./components/StreamingInteraction";

export default function ThreadPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const threadId = params?.threadId;
  const [interactions, setInteractions] = useState<any[]>([]);
  const [streamingInteraction, setStreamingInteraction] = useState<any | null>(
    null
  );
  const [userInput, setUserInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const hasAutoSentRef = useRef(false);

  // New states for streaming protocol
  const [taskTimeline, setTaskTimeline] = useState<any[]>([]);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [streamedAnswer, setStreamedAnswer] = useState("");
  const [streamingSources, setStreamingSources] = useState<any[]>([]);
  const [streamingTasks, setStreamingTasks] = useState<any[]>([]);
  const [showTabs, setShowTabs] = useState(true);

  const chatAreaRef = useRef<HTMLDivElement>(null);

  const [refreshInteractions, setRefreshInteractions] = useState(0);

  // Load existing interactions
  useEffect(() => {
    if (!threadId) return;
    const accessToken =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    fetch(`/api/interactions/${threadId}`, {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched interactions:", data);
        setInteractions(data);
      })
      .catch((err) => console.error("Failed to fetch interactions", err));
  }, [threadId, refreshInteractions]);

  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [
    interactions,
    streamingInteraction,
    showTimeline,
    showSkeleton,
    streamedAnswer,
  ]);

  // Auto-start chat if query param is present
  useEffect(() => {
    const query = searchParams?.get("query");
    if (
      query &&
      !isStreaming &&
      interactions.length === 0 &&
      !hasAutoSentRef.current
    ) {
      hasAutoSentRef.current = true;
      setTimeout(() => {
        handleSend(undefined, query);
        // Remove query param from URL after auto-send
        const url = new URL(window.location.href);
        url.searchParams.delete("query");
        window.history.replaceState({}, document.title, url.pathname);
      }, 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, interactions, isStreaming]);

  // Streaming handler
  const handleSend = async (e?: React.FormEvent, inputOverride?: string) => {
    if (e) e.preventDefault();
    const inputValue = inputOverride !== undefined ? inputOverride : userInput;
    if (!inputValue.trim() || !threadId) return;
    setIsStreaming(true);
    setShowTabs(false);
    setShowTimeline(false);
    setShowSkeleton(false);
    setTaskTimeline([]);
    setStreamedAnswer("");
    setStreamingSources([]);
    setStreamingTasks([]);

    const newInteraction = {
      id: "streaming",
      thread_id: threadId,
      user_query: inputValue,
      tasks: [],
      sources: [],
      assistant_response: "",
      created_at: new Date().toISOString(),
    };
    setStreamingInteraction(newInteraction);
    setUserInput("");
    inputRef.current?.focus();

    const accessToken =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({
        user_input: newInteraction.user_query,
        thread_id: threadId,
      }),
    });

    if (!res.body) {
      setIsStreaming(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let done = false;
    let assistantResponse = "";
    let tasks: any[] = [];
    let sources: any[] = [];
    let timeline: any[] = [];
    let messageId = null;

    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;
      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        // Each chunk may contain multiple JSON objects separated by newlines
        const lines = chunk.split("\n").filter(Boolean);
        for (const line of lines) {
          let event;
          try {
            event = JSON.parse(line);
          } catch (err) {
            console.error("Failed to parse event", err, line);
            continue;
          }
          switch (event.type) {
            case "taskStart":
              setShowTimeline(true);
              setTaskTimeline([]);
              timeline = [];
              messageId = event.messageId;
              break;
            default:
              // Collect all step* types for tasks
              if (event.type && event.type.startsWith("step")) {
                timeline.push(event);
                setTaskTimeline([...timeline]);
              }
              // Collect all sources type for sources
              if (event.type === "sources") {
                sources.push({ data: event.data });
                setStreamingSources([...sources]);
              }
              break;
            case "taskEnd":
              setShowTimeline(false);
              setShowSkeleton(true);
              break;
            case "messageStart":
              setShowSkeleton(false);
              setStreamedAnswer("");
              assistantResponse = "";
              break;
            case "message":
              assistantResponse += event.data;
              setStreamedAnswer(assistantResponse);
              messageId = event.messageId;
              break;
            case "messageEnd":
              setIsStreaming(false);
              setShowTabs(true);
              // Save the interaction for later POST
              setStreamingInteraction((prev: any) =>
                prev
                  ? {
                      ...prev,
                      assistant_response: assistantResponse,
                      tasks: [...timeline],
                      sources: [...sources],
                    }
                  : null
              );
              setStreamingTasks([...timeline]);
              setStreamingSources([...sources]);
              // POST the new interaction to /api/interactions
              (async () => {
                try {
                  const accessToken =
                    typeof window !== "undefined"
                      ? localStorage.getItem("access_token")
                      : null;
                  await fetch("/api/interactions", {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                      ...(accessToken
                        ? { Authorization: `Bearer ${accessToken}` }
                        : {}),
                    },
                    body: JSON.stringify({
                      thread_id: threadId,
                      user_query: newInteraction.user_query,
                      assistant_response: assistantResponse,
                      tasks: [...timeline],
                      sources: [...sources],
                    }),
                  });
                  setRefreshInteractions((prev) => prev + 1); // trigger re-fetch
                } catch (err) {
                  console.error("Failed to save interaction", err);
                }
              })();
              break;
          }
        }
      }
    }
    setStreamingInteraction(null);
    setIsStreaming(false);
  };

  // Dummy user avatar
  const avatarUrl = "https://ssl.gstatic.com/accounts/ui/avatar_2x.png";

  // Find the latest user interaction and extract its created_at
  let userMessageTime = "";
  if (interactions && Array.isArray(interactions) && interactions.length > 0) {
    const latestUserInteraction = [...interactions]
      .reverse()
      .find((i) => i.user_query);
    if (latestUserInteraction) {
      userMessageTime = latestUserInteraction.created_at;
    }
  }

  console.log("userMessageTime passed to Header:", userMessageTime);

  // Deduplicate interactions by id before rendering
  const dedupedInteractions = Array.from(
    new Map(interactions.map((i) => [i.id, i])).values()
  );

  return (
    <div className="flex flex-col items-center min-h-screen relative w-full">
      <Header avatarUrl={avatarUrl} userMessageTime={userMessageTime} />
      <div className="w-full max-w-4xl mx-auto mt px-4">
        {/* Scrollable chat area */}
        <div ref={chatAreaRef} className="h-[70vh] overflow-y-auto pr-2">
          {/* Always show previous chat, append streaming interaction if present */}
          <ChatWindow interactions={dedupedInteractions} />
          {isStreaming && (
            <StreamingInteraction
              userQuery={streamingInteraction?.user_query || userInput}
              showTimeline={showTimeline}
              taskTimeline={taskTimeline}
              showSkeleton={showSkeleton}
              streamedAnswer={streamedAnswer}
            />
          )}
        </div>
        <form onSubmit={handleSend} className="flex gap-2 mt-8 w-full">
          <input
            ref={inputRef}
            type="text"
            className="flex-1 border rounded px-3 py-2"
            placeholder="Type your message..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            disabled={isStreaming}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded"
            disabled={isStreaming || !userInput.trim()}
          >
            {isStreaming ? "Sending..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
