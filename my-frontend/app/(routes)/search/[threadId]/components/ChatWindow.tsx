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
        <div key={interaction.id} className="mb-8 w-full">
          <h2 className="font-bold text-2xl text-left mt-16 ml-4">
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
                <Answer data={interaction.assistant_response} />
              </TabsContent>
              <TabsContent value="Sources">
                <Sources sources={interaction.sources || []} />
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
