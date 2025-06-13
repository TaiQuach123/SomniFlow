import { Database, LayoutList, LucideSparkles } from "lucide-react";
import React from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Answer from "./Answer";
import Sources from "./Sources";
import Tasks from "./Tasks";

interface Interaction {
  id: string;
  thread_id: string;
  user_query: string;
  tasks?: any[];
  sources?: any[];
  assistant_response: string;
  created_at: string;
}

interface ChatWindowProps {
  interactions: Interaction[];
}

export default function ChatWindow({ interactions }: ChatWindowProps) {
  return (
    <div className="w-full flex items-start flex-col">
      {interactions.map((interaction, idx) => (
        <div key={interaction.id} className="mb-4 w-full">
          {idx > 0 && (
            <div className="border-b border-gray-200 dark:border-neutral-700 mb-4" />
          )}
          <h2 className="font-bold text-2xl text-left mt-4 ml-4">
            {interaction.user_query}
          </h2>
          <div className="w-full px-4 mt-4">
            <Tabs defaultValue="Answer" className="w-full">
              <TabsList>
                <TabsTrigger
                  value="Answer"
                  className="flex items-center gap-2 relative"
                >
                  <LucideSparkles className="w-4 h-4" />
                  Answer
                </TabsTrigger>
                <TabsTrigger
                  value="Sources"
                  className="flex items-center gap-2 relative"
                >
                  <Database className="w-4 h-4" />
                  Sources
                  <span className="mx-0 text-gray-400">&middot;</span>
                  <span className="inline-flex items-center justify-center px-1 py-0.5 text-xs font-medium rounded-full bg-gray-200 text-gray-700 min-w-[20px] h-5">
                    {interaction.sources ? interaction.sources.length : 0}
                  </span>
                </TabsTrigger>
                <TabsTrigger
                  value="Tasks"
                  className="flex items-center gap-2 relative"
                >
                  <LayoutList className="w-4 h-4" />
                  Tasks
                </TabsTrigger>
              </TabsList>
              <TabsContent value="Answer">
                <Sources
                  sources={interaction.sources || []}
                  variant="horizontal"
                />
                <Answer
                  data={interaction.assistant_response}
                  sources={interaction.sources || []}
                />
              </TabsContent>
              <TabsContent value="Sources">
                <Sources
                  sources={interaction.sources || []}
                  variant="vertical"
                />
              </TabsContent>
              <TabsContent value="Tasks">
                <Tasks tasks={interaction.tasks || []} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      ))}
    </div>
  );
}
