import ChatWindow from "@/components/ChatWindow";
import { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = {
  title: "Multi-Agent Chatbot System for Insomnia",
  description:
    "Multi-Agent Chatbot System for Insomnia with RAG and Web Search capabilities",
};

const Home = () => {
  return (
    <div>
      <Suspense>
        <ChatWindow />
      </Suspense>
    </div>
  );
};

export default Home;
