"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import crypto from "crypto";
import { useParams, useSearchParams } from "next/navigation";
import { Settings } from "lucide-react";
import Link from "next/link";
import NextError from "next/error";
import Navbar from "@/components/Navbar";
import Chat from "@/components/Chat";
import EmptyChat from "@/components/EmptyChat";

export interface Source {
  metadata: {
    title: string;
    url: string;
  };
  pageContent: string;
}

export type Message = {
  messageId: string;
  threadId: string;
  content: string;
  role: "user" | "assistant";
  createdAt: Date;
  sources?: Source[];
};

const loadMessages = async (
  threadId: string,
  setMessages: (messages: Message[]) => void,
  setIsMessagesLoaded: (loaded: boolean) => void,
  setChatHistory: (history: [string, string][]) => void,
  setNotFound: (notFound: boolean) => void
) => {
  const res = await fetch(`/api/chats/${threadId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (res.status === 404) {
    setNotFound(true);
    setIsMessagesLoaded(true);
    return;
  }

  const data = await res.json();

  const messages = data.messages.map((msg: any) => {
    return {
      ...msg,
      ...JSON.parse(msg.metadata),
      messageId: msg.messageId || crypto.randomBytes(7).toString("hex"),
    };
  }) as Message[];

  setMessages(messages);
  console.log("Loaded Messages:", messages);
  const history = messages.map((msg) => {
    return [msg.role, msg.content];
  }) as [string, string][];

  console.debug(new Date(), "app:messages_loaded");

  document.title = messages[0].content;

  setChatHistory(history);
  setIsMessagesLoaded(true);
};

const ChatWindow = ({ id }: { id?: string }) => {
  const searchParams = useSearchParams();
  const initialMessage = searchParams.get("q");

  const [threadId, setThreadId] = useState<string | undefined>(id);
  const [newChatCreated, setNewChatCreated] = useState(false);

  const [loading, setLoading] = useState(false);
  const [messageAppeared, setMessageAppeared] = useState(false);

  const [chatHistory, setChatHistory] = useState<[string, string][]>([]); // ('role', 'content')
  const [messages, setMessages] = useState<Message[]>([]);

  const [isMessagesLoaded, setIsMessagesLoaded] = useState(false);

  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (
      threadId &&
      !newChatCreated &&
      !isMessagesLoaded &&
      messages.length === 0
    ) {
      loadMessages(
        threadId,
        setMessages,
        setIsMessagesLoaded,
        setChatHistory,
        setNotFound
      );
    } else if (!threadId) {
      setNewChatCreated(true);
      setIsMessagesLoaded(true);
      setThreadId(crypto.randomBytes(20).toString("hex"));
    }
  }, []);

  const messagesRef = useRef<Message[]>([]);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const sendMessage = async (message: string, messageId?: string) => {
    if (loading) return;

    setLoading(true);
    setMessageAppeared(false);

    let sources: Source[] | undefined = undefined;
    let receivedMessage = "";
    let added = false;

    messageId = messageId ?? crypto.randomBytes(7).toString("hex");

    setMessages((prevMessages) => [
      ...prevMessages,
      {
        messageId: messageId,
        threadId: threadId!,
        content: message,
        role: "user",
        createdAt: new Date(),
      },
    ]);

    const messageHandler = async (data: any) => {
      if (data.type === "error") {
        toast.error(data.data);
        setLoading(false);
        return;
      }

      if (data.type === "sources") {
        sources = data.data;
        if (!added) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              content: "",
              messageId: data.messageId,
              threadId: threadId!,
              role: "assistant",
              createdAt: new Date(),
              sources: sources,
            },
          ]);
          added = true;
        }
        setMessageAppeared(true);
      }

      if (data.type === "message") {
        if (!added) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              messageId: data.messageId,
              threadId: threadId!,
              content: data.data,
              role: "assistant",
              createdAt: new Date(),
              sources: sources,
            },
          ]);
          added = true;
        }

        setMessages((prev) =>
          prev.map((message) => {
            console.log(message, data);
            if (message.messageId === data.messageId) {
              return { ...message, content: message.content + data.data };
            }
            return message;
          })
        );

        receivedMessage += data.data;
        setMessageAppeared(true);
      }

      if (data.type === "messageEnd") {
        setChatHistory((prevHistory) => [
          ...prevHistory,
          ["human", message],
          ["assistant", receivedMessage],
        ]);

        setLoading(false);

        const lastMsg = messagesRef.current[messagesRef.current.length - 1];
      }
    };

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_input: message, thread_id: threadId }),
    });

    if (!res.body) {
      throw new Error("No response body");
    }

    const reader = res.body?.getReader();
    const decoder = new TextDecoder("utf-8");

    let partialChunk = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      console.log("Value:", value);

      partialChunk += decoder.decode(value, { stream: true });

      console.log("Partial Chunk:", partialChunk);

      try {
        const messages = partialChunk.split("\n");
        for (const msg of messages) {
          console.log("MSG:", msg);
          if (!msg.trim()) continue;
          const json = JSON.parse(msg);
          messageHandler(json);
        }
        partialChunk = "";
      } catch (error) {
        console.warn("Incomplete JSON, waiting for next chunk...");
      }
    }
  };

  const rewrite = (messageId: string) => {
    const index = messages.findIndex((msg) => msg.messageId === messageId);

    if (index === -1) return;

    const message = messages[index - 1];

    setMessages((prev) => {
      return [...prev.slice(0, messages.length > 2 ? index - 1 : 0)];
    });
    setChatHistory((prev) => {
      return [...prev.slice(0, messages.length > 2 ? index - 1 : 0)];
    });

    sendMessage(message.content, message.messageId);
  };

  useEffect(() => {
    if (initialMessage) {
      sendMessage(initialMessage);
    }
  }, [initialMessage]);

  return true ? (
    notFound ? (
      <NextError statusCode={404} />
    ) : (
      <div>
        {messages.length > 0 ? (
          <>
            <Navbar threadId={threadId!} messages={messages} />
            <Chat
              loading={loading}
              messages={messages}
              sendMessage={sendMessage}
              messageAppeared={messageAppeared}
              rewrite={rewrite}
            />
          </>
        ) : (
          <EmptyChat sendMessage={sendMessage} />
        )}
      </div>
    )
  ) : (
    <div className="flex flex-row items-center justify-center min-h-screen">
      <svg
        aria-hidden="true"
        className="w-8 h-8 text-light-200 fill-light-secondary dark:text-[#202020] animate-spin dark:fill-[#ffffff3b]"
        viewBox="0 0 100 101"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M100 50.5908C100.003 78.2051 78.1951 100.003 50.5908 100C22.9765 99.9972 0.997224 78.018 1 50.4037C1.00281 22.7993 22.8108 0.997224 50.4251 1C78.0395 1.00281 100.018 22.8108 100 50.4251ZM9.08164 50.594C9.06312 73.3997 27.7909 92.1272 50.5966 92.1457C73.4023 92.1642 92.1298 73.4365 92.1483 50.6308C92.1669 27.8251 73.4392 9.0973 50.6335 9.07878C27.8278 9.06026 9.10003 27.787 9.08164 50.594Z"
          fill="currentColor"
        />
        <path
          d="M93.9676 39.0409C96.393 38.4037 97.8624 35.9116 96.9801 33.5533C95.1945 28.8227 92.871 24.3692 90.0681 20.348C85.6237 14.1775 79.4473 9.36872 72.0454 6.45794C64.6435 3.54717 56.3134 2.65431 48.3133 3.89319C45.869 4.27179 44.3768 6.77534 45.014 9.20079C45.6512 11.6262 48.1343 13.0956 50.5786 12.717C56.5073 11.8281 62.5542 12.5399 68.0406 14.7911C73.527 17.0422 78.2187 20.7487 81.5841 25.4923C83.7976 28.5886 85.4467 32.059 86.4416 35.7474C87.1273 38.1189 89.5423 39.6781 91.9676 39.0409Z"
          fill="currentFill"
        />
      </svg>
    </div>
  );
};

export default ChatWindow;
