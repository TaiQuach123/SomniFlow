import React, { useState, ElementType } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Search } from "lucide-react";
import { AiFillFilePdf } from "react-icons/ai";
import Sources from "./Sources";
import ReactMarkdown from "react-markdown";
import Timeline from "@mui/lab/Timeline";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import {
  IconButton,
  Collapse,
  Chip,
  Box,
  Typography,
  Stack,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import Tasks from "./Tasks";
import { Spinner } from "@/components/ui/spinner";

interface StreamingInteractionProps {
  userQuery: string;
  showTimeline: boolean;
  taskTimeline: any[];
  showSkeleton: boolean;
  streamedAnswer: string;
  sources: any[];
}

function getIcon(type: string, domain?: string) {
  if (type === "local")
    return <AiFillFilePdf className="text-red-600 w-5 h-5" />;
  if (type === "web" && domain) {
    return (
      <img
        src={`https://icon.horse/icon/${domain}`}
        alt={domain}
        className="w-5 h-5 rounded-full bg-white"
        style={{ minWidth: 20, minHeight: 20 }}
        onError={(e) => {
          (e.target as HTMLImageElement).src = "/favicon.ico";
        }}
      />
    );
  }
  return (
    <span role="img" aria-label="file">
      📁
    </span>
  );
}

// Function to get the proper URL for a source
function getSourceUrl(src: any) {
  if (src.type === "web") {
    return src.url;
  } else if (src.type === "local") {
    // For local PDF files, remove database/ prefix if it exists to avoid duplication
    let cleanUrl = src.url;
    if (cleanUrl.startsWith("database/")) {
      cleanUrl = cleanUrl.substring(9); // Remove "database/" prefix
    }
    return `/database/${cleanUrl}`;
  }
  return undefined;
}

function hasSubtasks(task: any) {
  return (
    (Array.isArray(task.searching) && task.searching.length > 0) ||
    (Array.isArray(task.reading) && task.reading.length > 0)
  );
}

function renderWithCitations(text: string, sources: any[]) {
  const citationRegex = /\[(\d+)\]/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;
  while ((match = citationRegex.exec(text)) !== null) {
    const idx = match.index;
    const refNum = parseInt(match[1], 10);
    if (idx > lastIndex) {
      parts.push(text.slice(lastIndex, idx));
    }
    const source = sources.find((s: any) => s.ref === refNum);
    if (source) {
      const sourceUrl = getSourceUrl(source);
      if (sourceUrl) {
        parts.push(
          <a
            key={"cite-" + refNum + "-" + idx}
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center w-5 h-5 mx-0.5 rounded bg-neutral-200 text-neutral-700 text-xs font-medium shadow-sm"
          >
            {refNum}
          </a>
        );
      } else {
        parts.push(match[0]);
      }
    } else {
      parts.push(match[0]);
    }
    lastIndex = idx + match[0].length;
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  return parts;
}

function makeCitationRenderer(
  Tag: ElementType,
  sources: any[]
): React.FunctionComponent<{ children?: React.ReactNode }> {
  return function Comp({ children }) {
    return (
      <Tag className="mb-2 leading-relaxed">
        {React.Children.map(children, (child, i) =>
          typeof child === "string"
            ? renderWithCitations(child, sources)
            : child
        )}
      </Tag>
    );
  };
}

export default function StreamingInteraction({
  userQuery,
  showTimeline,
  taskTimeline,
  showSkeleton,
  streamedAnswer,
  sources,
}: StreamingInteractionProps) {
  // Collapsed state for each parent task
  const [collapsed, setCollapsed] = useState<{ [k: number]: boolean }>({});

  const toggleCollapse = (idx: number) => {
    setCollapsed((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="mb-4 w-full">
      <h2 className="font-bold text-2xl text-left mt-4 ml-4">{userQuery}</h2>
      <div className="w-full px-4 mt-4">
        {showTimeline ? (
          <Tasks tasks={taskTimeline} />
        ) : showSkeleton ? (
          <div className="w-full my-8">
            <div className="mb-2 font-semibold flex items-center gap-2">
              <Spinner size={16} color="primary" />
              Preparing answer...
            </div>
            <div className="w-full">
              <Skeleton className="h-8 w-full mb-2" />
              <Skeleton className="h-8 w-5/6 mb-2" />
              <Skeleton className="h-8 w-2/3" />
            </div>
          </div>
        ) : streamedAnswer ? (
          <div className="w-full my-8">
            <Sources sources={sources || []} />
            <div className="bg-white dark:bg-neutral-900 rounded">
              <ReactMarkdown
                components={{
                  p: makeCitationRenderer("p", sources),
                  li: makeCitationRenderer("li", sources),
                  h1: makeCitationRenderer("h1", sources),
                  h2: makeCitationRenderer("h2", sources),
                  h3: makeCitationRenderer("h3", sources),
                  h4: makeCitationRenderer("h4", sources),
                  h5: makeCitationRenderer("h5", sources),
                  h6: makeCitationRenderer("h6", sources),
                }}
              >
                {streamedAnswer}
              </ReactMarkdown>
              <span className="animate-pulse text-gray-400 ml-2">|</span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
