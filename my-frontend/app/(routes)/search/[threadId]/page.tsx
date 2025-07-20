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
import { Spinner } from "@/components/ui/spinner";

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
      agents: [],
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
    let parentTasks: any = {};
    let messageId = null;
    let tempSources: any[] = [];
    let refCounter = 1;
    let latestSources: any[] = [];
    let latestAgents: any[] = [];
    let sourcesEventData: any = null;
    let taskEnded = false;

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
              parentTasks = {};
              messageId = event.messageId;
              taskEnded = false;
              break;
            case "step":
              if (event.agent) {
                timeline.push({
                  type: "step",
                  label: event.data,
                  agent: event.agent,
                });
              } else {
                timeline.push({ type: "step", label: event.data });
              }
              setStructuredTimeline([...timeline]);
              break;
            case "retrievalStart":
            case "webSearchStart": {
              const agent = event.agent || "default";
              const type =
                event.type === "retrievalStart" ? "retrieval" : "webSearch";
              const key = `${type}:${agent}`;
              parentTasks[key] = {
                type,
                agent,
                label:
                  event.data ||
                  (type === "retrieval"
                    ? "Searching local storage"
                    : "Searching the web"),
                searching: [],
                reading: [],
                collapsed: false,
              };
              timeline.push(parentTasks[key]);
              setStructuredTimeline([...timeline]);
              break;
            }
            case "retrievalQueries":
            case "webSearchQueries": {
              const agent = event.agent || "default";
              const type =
                event.type === "retrievalQueries" ? "retrieval" : "webSearch";
              const key = `${type}:${agent}`;
              if (parentTasks[key]) {
                parentTasks[key].searching = event.data || [];
                setStructuredTimeline([...timeline]);
              }
              break;
            }
            case "retrievalSources":
            case "webSearchSources": {
              const agent = event.agent || "default";
              const type =
                event.type === "retrievalSources" ? "retrieval" : "webSearch";
              const key = `${type}:${agent}`;
              if (parentTasks[key]) {
                let readingCards = [];
                if (type === "retrieval") {
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
                } else {
                  readingCards = (event.data || []).map((src: any) => ({
                    type: "web",
                    ...src,
                    description: src.description || undefined,
                  }));
                }
                parentTasks[key].reading = readingCards;
                setStructuredTimeline([...timeline]);
              }
              break;
            }
            case "retrievalEnd":
            case "webSearchEnd": {
              const agent = event.agent || "default";
              const type =
                event.type === "retrievalEnd" ? "retrieval" : "webSearch";
              const key = `${type}:${agent}`;
              // Instead of setting to null, mark the task as completed
              if (parentTasks[key]) {
                parentTasks[key].completed = true;
                parentTasks[key].ended = true;
              }
              setStructuredTimeline([...timeline]);
              break;
            }
            case "evaluationStart":
            case "contextExtractionStart":
            case "reflectionStart":
            case "planningStart": {
              const agent = event.agent || "default";
              const type = event.type.replace("Start", "");
              const key = `${type}:${agent}`;
              parentTasks[key] = {
                type,
                agent,
                label: event.data || type,
                searching: [],
                reading: [],
                collapsed: false,
              };
              timeline.push(parentTasks[key]);
              setStructuredTimeline([...timeline]);
              break;
            }
            case "evaluationEnd":
            case "contextExtractionEnd":
            case "reflectionEnd":
            case "planningEnd": {
              const agent = event.agent || "default";
              const type = event.type.replace("End", "");
              const key = `${type}:${agent}`;
              if (parentTasks[key]) {
                parentTasks[key].completed = true;
                parentTasks[key].ended = true;
              }
              setStructuredTimeline([...timeline]);
              break;
            }
            case "sources":
              sourcesEventData = event.data;
              let rag_sources = sourcesEventData.rag_sources || {};
              let web_sources = sourcesEventData.web_sources || {};
              // If both are empty, treat as no sources
              if (
                Object.keys(rag_sources).length === 0 &&
                Object.keys(web_sources).length === 0
              ) {
                setSourceCards([]);
                setStreamingSources([]);
                tempSources = [];
                latestSources = [];
                sourcesEventData = null;
                break;
              }
              let cards: any[] = [];
              Object.entries(rag_sources).forEach(([filename, meta]: any) => {
                cards.push({
                  type: "local",
                  ref: refCounter++,
                  url: filename,
                  title: meta.title || filename,
                  description: meta.description || undefined,
                  summary: meta.summary || undefined,
                  icon: "pdf",
                });
              });
              Object.entries(web_sources).forEach(([url, meta]: any) => {
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
              setStreamingSources(cards);
              tempSources = cards;
              latestSources = cards;
              sourcesEventData = null;
              break;
            case "taskEnd":
              setShowTimeline(false);
              setShowSkeleton(true);
              taskEnded = true;
              break;
            case "activeAgents":
              latestAgents = Array.isArray(event.data) ? event.data : [];
              console.log("AGENTS EVENT", latestAgents);
              timeline.push({
                type: "activeAgents",
                data: [...latestAgents],
                label: "Active agents updated",
                timestamp: new Date().toISOString(),
              });
              setStructuredTimeline([...timeline]);
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
              console.log("TIMELINE BEFORE SAVE", timeline);
              setIsStreaming(false);
              setShowTabs(true);
              setStreamingInteraction((prev: any) =>
                prev
                  ? {
                      ...prev,
                      assistant_response: assistantResponse,
                      tasks: [...timeline],
                      sources: [...latestSources],
                      agents: [...latestAgents],
                    }
                  : null
              );
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
                      agents: [...latestAgents],
                    }),
                  });
                  setRefreshInteractions((prev) => prev + 1);
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
            <>
              {/* Show initial loading state when streaming starts but timeline not yet shown */}
              {!showTimeline && !showSkeleton && !streamedAnswer && (
                <div className="w-full my-8 px-4">
                  <div className="mb-2 font-semibold flex items-center gap-2">
                    <Spinner size={16} color="primary" />
                    Starting analysis...
                  </div>
                  <div className="w-full">
                    <Skeleton className="h-8 w-full mb-2" />
                    <Skeleton className="h-8 w-3/4 mb-2" />
                    <Skeleton className="h-8 w-1/2" />
                  </div>
                </div>
              )}
              <StreamingInteraction
                userQuery={streamingInteraction?.user_query || userInput}
                showTimeline={showTimeline}
                taskTimeline={structuredTimeline}
                showSkeleton={showSkeleton}
                streamedAnswer={streamedAnswer}
                sources={streamingSources}
              />
            </>
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
                className={`w-full ${
                  isStreaming ? "cursor-not-allowed" : "cursor-text"
                }`}
                onClick={() =>
                  !isStreaming && inputRef.current && inputRef.current.focus()
                }
              >
                <input
                  ref={inputRef}
                  type="text"
                  className={`w-full bg-transparent outline-none py-2 text-base ${
                    isStreaming
                      ? "placeholder:text-gray-400 text-gray-400"
                      : "placeholder:text-gray-500"
                  }`}
                  placeholder={
                    isStreaming ? "Processing..." : "Type your message..."
                  }
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
                {isStreaming ? (
                  <Spinner size={16} color="primary" />
                ) : (
                  <AudioLines className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
