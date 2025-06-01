import React from "react";
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

export default function ChatInputBox() {
  return (
    <div className="flex flex-col h-screen items-center justify-center w-full">
      <h1 className="inline-flex min-h-10.5 items-baseline text-[28px] leading-[34px] font-normal tracking-[0.38px] whitespace-pre-wrap motion-safe:[transition:0.25s_transform_var(--spring-standard),0.2s_opacity_var(--spring-standard),0.3s_visibility_var(--spring-standard)] opacity-100">
        <div className="px-1 text-pretty whitespace-pre-wrap">
          💬 Ask me anything about insomnia — I&apos;m here to help!
        </div>
      </h1>

      <div className="p-2 w-full max-w-2xl border rounded-2xl mt-10">
        <div className="flex items-end justify-between">
          <Tabs defaultValue="Search" className="w-[400px]">
            <TabsContent value="Search">
              <input
                type="text"
                placeholder="Ask anything..."
                className="w-full p-4 rounded-md outline-none"
              />
            </TabsContent>
            <TabsContent value="Research">
              <input
                type="text"
                placeholder="Research anything..."
                className="w-full p-4 rounded-md outline-none"
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
            <Button>
              <AudioLines className="text-white h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
