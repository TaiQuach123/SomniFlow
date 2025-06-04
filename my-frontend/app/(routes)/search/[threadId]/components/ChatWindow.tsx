import { Database, LayoutList, LucideSparkles } from "lucide-react";
import React from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Answer from "./Answer";
import Sources from "./Sources";
import Tasks from "./Tasks";

type Message = {
  role: string;
  content: string;
  [key: string]: any;
};

interface ChatWindowProps {
  messages: Message[];
}
const tabs = [
  { label: "Answer", icon: LucideSparkles },
  { label: "Sources", icon: Database, badge: "10" },
  { label: "Tasks", icon: LayoutList },
];
export default function ChatWindow({ messages }: ChatWindowProps) {
  const firstUserMessage = messages?.find((msg) => msg.role === "user");
  return (
    <div className="w-full flex items-start flex-col">
      {firstUserMessage && (
        <h2 className="font-bold text-2xl text-left mt-16 ml-4">
          {firstUserMessage.content}
        </h2>
      )}
      <div className="w-full px-4 mt-4">
        <Tabs defaultValue="Answer" className="w-full">
          <TabsList>
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.label}
                value={tab.label}
                className="flex items-center gap-2 relative"
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {tab.badge && (
                  <span className="ml-2 bg-gray-200 text-gray-700 rounded-full px-2 py-0.5 text-xs font-semibold">
                    {tab.badge}
                  </span>
                )}
              </TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="Answer">
            <Answer data="This is a dummy answer for demonstration." />
          </TabsContent>
          <TabsContent value="Sources">
            <Sources
              sources={[
                "Source 1: https://example.com",
                "Source 2: https://another.com",
              ]}
            />
          </TabsContent>
          <TabsContent value="Tasks">
            <Tasks
              tasks={[
                "Task 1: Review the answer",
                "Task 2: Check sources",
                "Task 3: Complete follow-up",
              ]}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
