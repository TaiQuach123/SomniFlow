"use client";
import React, { useEffect, useState, useRef } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import { Skeleton } from "@/components/ui/skeleton";
import StreamingInteraction from "./components/StreamingInteraction";
import { Globe, Paperclip, AudioLines, SearchCheck, Atom } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";

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
  const [structuredTimeline, setStructuredTimeline] = useState<any[]>([]);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [streamedAnswer, setStreamedAnswer] = useState("");
  const [streamingSources, setStreamingSources] = useState<any[]>([]);
  const [showTabs, setShowTabs] = useState(true);
  const [currentParentTask, setCurrentParentTask] = useState<any | null>(null);
  const [sourceCards, setSourceCards] = useState<any[]>([]);

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
    setStructuredTimeline([]);
    setStreamedAnswer("");
    setStreamingSources([]);
    setSourceCards([]);
    setCurrentParentTask(null);

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
    let timeline: any[] = [];
    let parentTask: any = null;
    let messageId = null;
    let tempSources: any[] = [];
    let refCounter = 1;
    let latestSources: any[] = [];

    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;
      if (value) {
        const chunk = decoder.decode(value, { stream: true });
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
              setStructuredTimeline([]);
              timeline = [];
              parentTask = null;
              messageId = event.messageId;
              break;
            case "step":
              // General step
              timeline.push({ type: "step", label: event.data });
              setStructuredTimeline([...timeline]);
              break;
            case "retrievalStart":
              parentTask = {
                type: "retrieval",
                label: event.data || "Searching local storage",
                searching: [],
                reading: [],
                collapsed: false,
              };
              timeline.push(parentTask);
              setStructuredTimeline([...timeline]);
              break;
            case "retrievalQueries":
              if (parentTask && parentTask.type === "retrieval") {
                parentTask.searching = event.data || [];
                setStructuredTimeline([...timeline]);
              }
              break;
            case "retrievalSources":
              if (parentTask && parentTask.type === "retrieval") {
                // Convert object to array of cards for Reading section
                let readingCards = [];
                if (
                  event.data &&
                  typeof event.data === "object" &&
                  !Array.isArray(event.data)
                ) {
                  Object.entries(event.data).forEach(
                    ([filename, meta]: any) => {
                      readingCards.push({
                        type: "local",
                        url: filename,
                        title: meta.title || filename,
                        description: meta.description || undefined,
                        icon: "pdf",
                      });
                    }
                  );
                } else if (Array.isArray(event.data)) {
                  readingCards = event.data.map((src: any) => ({
                    ...src,
                    description: src.description || undefined,
                  }));
                }
                parentTask.reading = readingCards;
                setStructuredTimeline([...timeline]);
              }
              break;
            case "retrievalEnd":
              parentTask = null;
              setStructuredTimeline([...timeline]);
              break;
            case "webSearchStart":
              parentTask = {
                type: "webSearch",
                label: event.data || "Searching the web",
                searching: [],
                reading: [],
                collapsed: false,
              };
              timeline.push(parentTask);
              setStructuredTimeline([...timeline]);
              break;
            case "webSearchQueries":
              if (parentTask && parentTask.type === "webSearch") {
                parentTask.searching = event.data || [];
                setStructuredTimeline([...timeline]);
              }
              break;
            case "webSearchSources":
              if (parentTask && parentTask.type === "webSearch") {
                parentTask.reading = (event.data || []).map((src: any) => ({
                  type: "web",
                  ...src,
                  description: src.description || undefined,
                }));
                setStructuredTimeline([...timeline]);
              }
              break;
            case "webSearchEnd":
              parentTask = null;
              setStructuredTimeline([...timeline]);
              break;
            case "sources":
              console.log(
                "[SOURCES EVENT] Received sources event:",
                event.data
              );
              // Always treat first element as rag_sources, second as web_sources
              let rag_sources = {},
                web_sources = [];
              if (Array.isArray(event.data)) {
                rag_sources = event.data[0] || {};
                web_sources = event.data[1] || [];
              } else if (event.data && typeof event.data === "object") {
                rag_sources = event.data.rag_sources || {};
                web_sources = event.data.web_sources || [];
              }
              let cards: any[] = [];
              // RAG sources first
              Object.entries(rag_sources).forEach(([filename, meta]: any) => {
                cards.push({
                  type: "local",
                  ref: refCounter++,
                  url: filename,
                  title: meta.title || filename,
                  description: meta.description || undefined,
                  icon: "pdf",
                });
              });
              // Web sources
              (Array.isArray(web_sources)
                ? web_sources
                : Object.entries(web_sources)
              ).forEach((src: any) => {
                // src can be [url, meta] or an object
                let url, meta;
                if (Array.isArray(src)) {
                  [url, meta] = src;
                } else {
                  url = src.url || src;
                  meta = src;
                }
                cards.push({
                  type: "web",
                  ref: refCounter++,
                  url,
                  title: meta.title || url,
                  description: meta.description || undefined,
                  domain: url
                    ? url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2] || url
                    : url,
                  icon: "web",
                });
              });
              setSourceCards(cards);
              setStreamingSources(cards); // for compatibility
              tempSources = cards;
              latestSources = cards; // Always keep the latest sources
              console.log("[SOURCES EVENT] Processed cards:", cards);
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
              console.log(
                "[MESSAGE END] latestSources before save:",
                latestSources
              );
              setIsStreaming(false);
              setShowTabs(true);
              setStreamingInteraction((prev: any) =>
                prev
                  ? {
                      ...prev,
                      assistant_response: assistantResponse,
                      tasks: [...timeline],
                      sources: [...latestSources],
                    }
                  : null
              );
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
                      sources: [...latestSources],
                    }),
                  });
                  setRefreshInteractions((prev) => prev + 1); // trigger re-fetch
                } catch (err) {
                  console.error("Failed to save interaction", err);
                }
              })();
              break;
            default:
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

  // Deduplicate interactions by id before rendering
  const dedupedInteractions = Array.from(
    new Map(interactions.map((i) => [i.id, i])).values()
  );

  return (
    <div className="flex flex-col min-h-screen relative w-full">
      <Header avatarUrl={avatarUrl} userMessageTime={userMessageTime} />
      {/* Scrollable chat area now full width, content centered */}
      <div ref={chatAreaRef} className="h-[75vh] overflow-y-auto w-full">
        <div className="w-full max-w-4xl mx-auto px-4">
          <ChatWindow interactions={dedupedInteractions} />
          {isStreaming && (
            <StreamingInteraction
              userQuery={streamingInteraction?.user_query || userInput}
              showTimeline={showTimeline}
              taskTimeline={structuredTimeline}
              showSkeleton={showSkeleton}
              streamedAnswer={streamedAnswer}
              sources={streamingSources}
            />
          )}
        </div>
      </div>
      <div className="w-full max-w-4xl mx-auto px-4">
        <form onSubmit={handleSend} className="w-full mt-8">
          <div className="flex items-center justify-between w-full max-w-4xl border rounded-2xl bg-white dark:bg-neutral-900 p-2 mx-auto">
            <Tabs
              defaultValue={"Search"}
              className="w-[180px] mr-4"
              onValueChange={() => {}}
            >
              <TabsList className="bg-transparent border-none shadow-none p-0">
                <TabsTrigger
                  value="Search"
                  className="text-primary flex items-center gap-1 px-3 py-2 rounded-md data-[state=active]:bg-blue-100 dark:data-[state=active]:bg-neutral-800"
                >
                  <SearchCheck className="h-4 w-4" /> Search
                </TabsTrigger>
                <TabsTrigger
                  value="Research"
                  className="text-primary flex items-center gap-1 px-3 py-2 rounded-md data-[state=active]:bg-blue-100 dark:data-[state=active]:bg-neutral-800"
                >
                  <Atom className="h-4 w-4" /> Research
                </TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="flex-1 flex items-center px-2">
              <div
                className="w-full cursor-text"
                onClick={() => inputRef.current && inputRef.current.focus()}
              >
                <input
                  ref={inputRef}
                  type="text"
                  className="w-full bg-transparent outline-none py-2 text-base placeholder:text-gray-500"
                  placeholder="Type your message..."
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  disabled={isStreaming}
                  style={{ minWidth: 0 }}
                />
              </div>
            </div>
            <div className="flex gap-2 items-center ml-2">
              <Button type="button" variant="ghost" size="icon" tabIndex={-1}>
                <Globe className="text-gray-600 h-5 w-5" />
              </Button>
              <Button type="button" variant="ghost" size="icon" tabIndex={-1}>
                <Paperclip className="text-gray-500 h-5 w-5" />
              </Button>
              <Button
                type="submit"
                size="icon"
                className="bg-blue-500 hover:bg-blue-600 text-white"
                disabled={isStreaming || !userInput.trim()}
              >
                <AudioLines className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
