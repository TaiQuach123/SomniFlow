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

interface StreamingInteractionProps {
  userQuery: string;
  showTimeline: boolean;
  taskTimeline: any[];
  showSkeleton: boolean;
  streamedAnswer: string;
  sources: any[];
}

function getIcon(type: string, domain?: string) {
  console.log(type, domain);
  if (type === "local")
    return <AiFillFilePdf className="text-red-600 w-5 h-5" />;
  if (type === "web" && domain) {
    return (
      <img
        src={`https://icon.horse/icon/${domain}`}
        alt={domain}
        className="w-5 h-5 rounded"
        style={{ background: "#fff" }}
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
    if (source && source.url) {
      parts.push(
        <a
          key={"cite-" + refNum + "-" + idx}
          href={source.url}
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
          <Box
            sx={{
              width: "100%",
              my: 8,
              bgcolor: "background.default",
              borderRadius: 2,
              p: 2,
              pl: 0,
            }}
          >
            <Box sx={{ display: "flex", justifyContent: "flex-start" }}>
              <Timeline
                sx={{
                  p: 0,
                  m: 0,
                  pl: 0,
                  ml: 0,
                  position: "static",
                  minWidth: 0,
                }}
              >
                {taskTimeline.map((task, idx) => {
                  const isLast = idx === taskTimeline.length - 1;
                  const subtasks =
                    (Array.isArray(task.searching) &&
                      task.searching.length > 0) ||
                    (Array.isArray(task.reading) && task.reading.length > 0);
                  return (
                    <TimelineItem
                      key={idx}
                      sx={{
                        minHeight: 48,
                        pl: 0,
                        ml: 0,
                        "&:before": { display: "none" },
                      }}
                    >
                      <TimelineSeparator>
                        <TimelineDot color="primary" />
                        {!isLast && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent
                        sx={{ py: 0, minWidth: 0, pl: 0, ml: 0 }}
                      >
                        {task.type === "retrieval" ||
                        task.type === "webSearch" ? (
                          <Box>
                            <Box display="flex" alignItems="center" mb={1}>
                              <Typography
                                variant="subtitle1"
                                fontWeight={600}
                                color="text.primary"
                                sx={{ userSelect: "none" }}
                              >
                                {task.type === "retrieval"
                                  ? "Searching local data"
                                  : "Searching the web"}
                              </Typography>
                              <IconButton
                                size="small"
                                aria-label="Toggle collapse"
                                sx={{ ml: 1 }}
                                onClick={() => toggleCollapse(idx)}
                              >
                                {collapsed[idx] ? (
                                  <ChevronRightIcon fontSize="small" />
                                ) : (
                                  <ExpandMoreIcon fontSize="small" />
                                )}
                              </IconButton>
                            </Box>
                            <Collapse in={!collapsed[idx]}>
                              <Box mb={2} ml={2}>
                                <Typography
                                  variant="body2"
                                  fontWeight={600}
                                  color="text.secondary"
                                >
                                  Searching
                                </Typography>
                                <Stack
                                  direction="column"
                                  spacing={0.5}
                                  mt={0.5}
                                >
                                  {Array.isArray(task.searching) &&
                                  task.searching.length > 0 ? (
                                    task.searching.map(
                                      (query: string, i: number) => (
                                        <Box
                                          key={i}
                                          display="flex"
                                          alignItems="center"
                                          gap={1}
                                        >
                                          <Search
                                            className="w-4 h-4"
                                            style={{ color: "#eab308" }}
                                          />
                                          <Chip
                                            label={query}
                                            size="small"
                                            sx={{
                                              bgcolor: "grey.100",
                                              color: "text.primary",
                                              fontFamily: "monospace",
                                              fontSize: 13,
                                              borderRadius: 2,
                                            }}
                                          />
                                        </Box>
                                      )
                                    )
                                  ) : (
                                    <Typography
                                      variant="body2"
                                      color="text.disabled"
                                    >
                                      No queries
                                    </Typography>
                                  )}
                                </Stack>
                              </Box>
                              <Box ml={2} mb={1.5}>
                                <Typography
                                  variant="body2"
                                  fontWeight={600}
                                  color="text.secondary"
                                >
                                  Reading
                                </Typography>
                                <Stack
                                  direction="row"
                                  spacing={1}
                                  flexWrap="wrap"
                                  mt={1}
                                >
                                  {Array.isArray(task.reading) &&
                                  task.reading.length > 0 ? (
                                    task.reading.map((src: any, i: number) => {
                                      const domain =
                                        src.domain ||
                                        (src.url &&
                                          src.url.match(
                                            /https?:\/\/(www\.)?([^\/]+)/
                                          )?.[2]);
                                      const filename =
                                        src.type === "local"
                                          ? src.url.split("/").pop()
                                          : undefined;
                                      return (
                                        <Box
                                          key={i}
                                          component="span"
                                          sx={{ mb: 1 }}
                                        >
                                          <Chip
                                            component={
                                              src.url &&
                                              src.url.startsWith("http")
                                                ? "a"
                                                : "span"
                                            }
                                            href={
                                              src.url &&
                                              src.url.startsWith("http")
                                                ? src.url
                                                : undefined
                                            }
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            clickable={
                                              !!(
                                                src.url &&
                                                src.url.startsWith("http")
                                              )
                                            }
                                            icon={getIcon(src.type, domain)}
                                            label={
                                              src.type === "local"
                                                ? filename
                                                : domain
                                            }
                                            title={src.title || src.url}
                                            sx={{
                                              bgcolor: "grey.100",
                                              color: "text.primary",
                                              fontWeight: 600,
                                              fontSize: 13,
                                              borderRadius: 2,
                                              maxWidth: 140,
                                              minWidth: 80,
                                              textOverflow: "ellipsis",
                                              overflow: "hidden",
                                            }}
                                          />
                                        </Box>
                                      );
                                    })
                                  ) : (
                                    <Typography
                                      variant="body2"
                                      color="text.disabled"
                                    >
                                      No sources
                                    </Typography>
                                  )}
                                </Stack>
                              </Box>
                            </Collapse>
                          </Box>
                        ) : (
                          <Box ml={2}>
                            <Typography
                              variant="subtitle1"
                              fontWeight={600}
                              color="text.primary"
                            >
                              {typeof task.label === "string"
                                ? task.label
                                : JSON.stringify(task.label)}
                            </Typography>
                          </Box>
                        )}
                      </TimelineContent>
                    </TimelineItem>
                  );
                })}
              </Timeline>
            </Box>
          </Box>
        ) : showSkeleton ? (
          <div className="w-full my-8">
            <div className="mb-2 font-semibold">Preparing answer...</div>
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
