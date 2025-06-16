"use client";
import React, { useState } from "react";
import Image from "next/image";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Atom,
  AudioLines,
  Cpu,
  Globe,
  Paperclip,
  SearchCheck,
} from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "./ui/button";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { mutate } from "swr";

// SWR fetcher for global use
const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function ChatInputBox() {
  const [input, setInput] = useState("");
  const [tab, setTab] = useState("Search");
  const router = useRouter();

  const handleSubmit = (e?: React.FormEvent | React.KeyboardEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const threadId = uuidv4();
    router.push(`/search/${threadId}?query=${encodeURIComponent(input)}`);
    mutate("/api/chats");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-screen items-center justify-center w-full">
      <img
        src="/logo-gray.svg"
        alt="Logo"
        width={160}
        height={160}
        className="mb-8 grayscale brightness-110 mx-auto"
      />
      <h1 className="inline-flex min-h-10.5 items-baseline text-[28px] leading-[34px] font-normal tracking-[0.38px] whitespace-pre-wrap motion-safe:[transition:0.25s_transform_var(--spring-standard),0.2s_opacity_var(--spring-standard),0.3s_visibility_var(--spring-standard)] opacity-100">
        <div className="px-1 text-pretty whitespace-pre-wrap">
          💬 Ask me anything about insomnia — I&apos;m here to help!
        </div>
      </h1>

      <div className="p-2 w-full max-w-2xl border rounded-2xl mt-10">
        <form onSubmit={handleSubmit}>
          <div className="flex items-end justify-between">
            <Tabs defaultValue={tab} className="w-full" onValueChange={setTab}>
              <TabsContent value="Search">
                <textarea
                  placeholder="Ask anything..."
                  className="w-full p-4 rounded-md outline-none resize-none min-h-[48px] max-h-40 overflow-auto"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={1}
                  onKeyDown={handleKeyDown}
                />
              </TabsContent>
              <TabsContent value="Research">
                <textarea
                  placeholder="Research anything..."
                  className="w-full p-4 rounded-md outline-none resize-none min-h-[48px] max-h-40 overflow-auto"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={1}
                  onKeyDown={handleKeyDown}
                />
              </TabsContent>
              <TabsList>
                <TabsTrigger value="Search" className="text-primary">
                  <SearchCheck /> Search
                </TabsTrigger>
                <TabsTrigger value="Research" className="text-primary">
                  {" "}
                  <Atom /> Research
                </TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="flex gap-1 items-center">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost">
                    <Globe className="text-gray-600 h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Gemini-Flash-2.0</DropdownMenuItem>
                  <DropdownMenuItem>Billing</DropdownMenuItem>
                  <DropdownMenuItem>Team</DropdownMenuItem>
                  <DropdownMenuItem>Subscription</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button variant="ghost">
                <Paperclip className="text-gray-500 h-5 w-5" />
              </Button>
              <Button type="submit">
                <AudioLines className="text-white h-5 w-5" />
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
