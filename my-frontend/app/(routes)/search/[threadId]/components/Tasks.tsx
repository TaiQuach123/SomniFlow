import React, { useState } from "react";
import { Search } from "lucide-react";
import { AiFillFilePdf } from "react-icons/ai";
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
  Tooltip,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import ExtensionIcon from "@mui/icons-material/Extension";
import ShieldIcon from "@mui/icons-material/Shield";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

// Agent UI mapping
const agentUI = {
  suggestion: {
    color: "#e0f2fe",
    textColor: "#0369a1",
    icon: <LightbulbIcon fontSize="small" sx={{ color: "#0369a1" }} />,
    label: "Suggestion",
    description: "Suggests improvements",
  },
  factor: {
    color: "#dcfce7",
    textColor: "#166534",
    icon: <ExtensionIcon fontSize="small" sx={{ color: "#166534" }} />,
    label: "Factor",
    description: "Analyzes contributing factors",
  },
  harm: {
    color: "#fee2e2",
    textColor: "#b91c1c",
    icon: <ShieldIcon fontSize="small" sx={{ color: "#b91c1c" }} />,
    label: "Harm",
    description: "Checks for harm or risk",
  },
};

// Utility to normalize tasks by agent, preserving timeline order
function normalizeTimeline(tasks: any[], activeAgents: string[] = []) {
  // Find the latest activeAgents if not provided
  let agentsList = activeAgents;
  if (!agentsList.length) {
    for (let i = tasks.length - 1; i >= 0; i--) {
      if (tasks[i].type === "activeAgents" && Array.isArray(tasks[i].data)) {
        agentsList = tasks[i].data;
        break;
      }
    }
  }
  // Map to keep track of agent sections and their order of first appearance
  const agentSections: {
    [agent: string]: { type: "agent"; agent: string; tasks: any[] };
  } = {};
  const timeline: any[] = [];
  for (const task of tasks) {
    if (task.type === "activeAgents") continue;
    if (!task.agent || task.agent === "supervisor") {
      timeline.push(task);
      continue;
    }
    // If this is the first time we see this agent, create a section
    if (!agentSections[task.agent]) {
      agentSections[task.agent] = {
        type: "agent",
        agent: task.agent,
        tasks: [],
      };
      timeline.push(agentSections[task.agent]);
    }
    agentSections[task.agent].tasks.push(task);
  }
  return { timeline, agentsList };
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

function hasSubtasks(task: any) {
  return (
    (Array.isArray(task.searching) && task.searching.length > 0) ||
    (Array.isArray(task.reading) && task.reading.length > 0)
  );
}

export default function Tasks({
  tasks,
  activeAgents,
}: {
  tasks: any[];
  activeAgents?: string[];
}) {
  // Normalize timeline
  const { timeline, agentsList } = normalizeTimeline(tasks, activeAgents);
  // Collapsed state for agent sections and for subtasks
  const [collapsedAgents, setCollapsedAgents] = useState<{
    [k: string]: boolean;
  }>({});
  const [collapsed, setCollapsed] = useState<{ [k: string]: boolean }>({});
  const toggleAgentCollapse = (agent: string) => {
    setCollapsedAgents((prev) => ({ ...prev, [agent]: !prev[agent] }));
  };
  const toggleCollapse = (key: string) => {
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  function renderTask(
    task: any,
    idx: number,
    parentKey?: string,
    isLast?: boolean
  ) {
    const subtasks = hasSubtasks(task);
    const key = parentKey ? `${parentKey}-${idx}` : `${idx}`;
    return (
      <TimelineItem
        key={key}
        sx={{ minHeight: 48, pl: 0, ml: 0, "&:before": { display: "none" } }}
      >
        <TimelineSeparator>
          <TimelineDot
            color="grey"
            sx={{
              width: 8,
              height: 8,
              minWidth: 8,
              minHeight: 8,
              boxShadow: "none",
              padding: 0,
              borderWidth: 1,
              boxSizing: "border-box",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          />
          {!isLast && <TimelineConnector sx={{ width: 1.5 }} />}
        </TimelineSeparator>
        <TimelineContent sx={{ py: 0, minWidth: 0, pl: 0, ml: 2 }}>
          <Box
            display="flex"
            alignItems="center"
            mb={subtasks ? 0.5 : 0}
            mt={0.5}
            sx={
              task.type === "retrieval" || task.type === "webSearch"
                ? { mt: "-0px" }
                : {}
            }
          >
            <Typography
              variant="subtitle1"
              sx={{
                userSelect: "none",
                fontSize: 14,
                fontWeight: 500,
                color: "#374151",
              }}
            >
              {task.type === "retrieval"
                ? "Searching local storage"
                : task.type === "webSearch"
                ? "Searching the web"
                : typeof task.label === "string"
                ? task.label
                : JSON.stringify(task.label)}
            </Typography>
            {subtasks && (
              <IconButton
                size="small"
                aria-label="Toggle collapse"
                onClick={() => toggleCollapse(key)}
                sx={{ ml: 1 }}
              >
                {collapsed[key] ? (
                  <ChevronRightIcon fontSize="small" />
                ) : (
                  <ExpandMoreIcon fontSize="small" />
                )}
              </IconButton>
            )}
          </Box>
          {subtasks ? (
            <Collapse in={!collapsed[key]}>
              {/* Searching */}
              <Box mb={1} ml={2}>
                <Typography
                  variant="body2"
                  sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                >
                  Searching
                </Typography>
                <Stack direction="column" spacing={0.5} mt={0.5}>
                  {Array.isArray(task.searching) &&
                  task.searching.length > 0 ? (
                    task.searching.map((query: string, i: number) => (
                      <Box key={i} display="flex" alignItems="center" gap={1}>
                        <Chip
                          icon={
                            <Search
                              className="w-4 h-4"
                              style={{ color: "#1a1a1a" }}
                            />
                          }
                          label={query}
                          size="small"
                          sx={{
                            bgcolor: "grey.100",
                            color: "text.primary",
                            fontFamily: "monospace",
                            fontSize: 12,
                            borderRadius: 2,
                            height: 24,
                          }}
                        />
                      </Box>
                    ))
                  ) : (
                    <Typography
                      variant="body2"
                      sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                    >
                      No queries
                    </Typography>
                  )}
                </Stack>
              </Box>
              {/* Reading */}
              <Box ml={2} mb={1.5}>
                <Typography
                  variant="body2"
                  sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                >
                  Reading
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" mt={1}>
                  {Array.isArray(task.reading) && task.reading.length > 0 ? (
                    task.reading.map((src: any, i: number) => {
                      const domain =
                        src.domain ||
                        (src.url &&
                          src.url.match(/https?:\/\/(www\.)?([^\/]+)/)?.[2]);
                      const filename =
                        src.type === "local"
                          ? src.url.split("/").pop()
                          : undefined;
                      return (
                        <Box key={i} component="span" sx={{ mb: 1 }}>
                          <Chip
                            component={
                              src.url && src.url.startsWith("http")
                                ? "a"
                                : "span"
                            }
                            href={
                              src.url && src.url.startsWith("http")
                                ? src.url
                                : undefined
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                            clickable={
                              !!(src.url && src.url.startsWith("http"))
                            }
                            icon={getIcon(src.type, domain)}
                            label={src.type === "local" ? filename : domain}
                            title={src.title || src.url}
                            sx={{
                              bgcolor: "grey.100",
                              color: "text.primary",
                              fontWeight: 600,
                              fontSize: 12,
                              borderRadius: 2,
                              maxWidth: 140,
                              minWidth: 80,
                              textOverflow: "ellipsis",
                              overflow: "hidden",
                              height: 24,
                            }}
                          />
                        </Box>
                      );
                    })
                  ) : (
                    <Typography
                      variant="body2"
                      sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                    >
                      No sources
                    </Typography>
                  )}
                </Stack>
              </Box>
            </Collapse>
          ) : null}
        </TimelineContent>
      </TimelineItem>
    );
  }

  return (
    <Box sx={{ bgcolor: "background.default", borderRadius: 2, p: 2, pl: 0 }}>
      <Box sx={{ display: "flex", justifyContent: "flex-start" }}>
        <Timeline
          sx={{ p: 0, m: 0, pl: 0, ml: 0, position: "static", minWidth: 0 }}
        >
          {timeline.map((item, idx) => {
            const isLastTopLevel = idx === timeline.length - 1;
            if (item.type === "agent") {
              const agent = String(item.agent);
              const ui = (agentUI as any)[agent] || {
                color: "#f3f4f6",
                textColor: "#374151",
                icon: (
                  <InfoOutlinedIcon
                    fontSize="small"
                    sx={{ color: "#374151" }}
                  />
                ),
                label: agent,
                description: "Agent",
              };
              return (
                <React.Fragment key={agent}>
                  <TimelineItem
                    sx={{
                      minHeight: 48,
                      pl: 0,
                      ml: 0,
                      "&:before": { display: "none" },
                    }}
                  >
                    <TimelineSeparator>
                      <TimelineDot
                        color="primary"
                        sx={{
                          width: 12,
                          height: 12,
                          minWidth: 12,
                          minHeight: 12,
                          boxShadow: "none",
                          padding: 0,
                          borderWidth: 2,
                          boxSizing: "border-box",
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      />
                      {!isLastTopLevel && (
                        <TimelineConnector sx={{ width: 1.5 }} />
                      )}
                    </TimelineSeparator>
                    <TimelineContent sx={{ py: 0, minWidth: 0, pl: 0, ml: 2 }}>
                      <Box display="flex" alignItems="center" mb={0.5} mt={0.5}>
                        <Tooltip title={ui.description} arrow>
                          <Chip
                            icon={ui.icon}
                            label={ui.label}
                            sx={{
                              bgcolor: ui.color,
                              color: ui.textColor,
                              fontWeight: 700,
                              fontSize: 15,
                              height: 32,
                              mr: 1,
                            }}
                          />
                        </Tooltip>
                        <IconButton
                          size="small"
                          aria-label="Toggle agent collapse"
                          onClick={() => toggleAgentCollapse(agent)}
                          sx={{ ml: 1 }}
                        >
                          {collapsedAgents[agent] ? (
                            <ChevronRightIcon fontSize="small" />
                          ) : (
                            <ExpandMoreIcon fontSize="small" />
                          )}
                        </IconButton>
                      </Box>
                      <Collapse in={!collapsedAgents[agent]}>
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
                          {item.tasks.length === 0 ? (
                            <TimelineItem>
                              <TimelineContent
                                sx={{ py: 0, minWidth: 0, pl: 0, ml: 2 }}
                              >
                                <Typography
                                  variant="body2"
                                  sx={{ color: "#64748b", fontStyle: "italic" }}
                                >
                                  No tasks yet
                                </Typography>
                              </TimelineContent>
                            </TimelineItem>
                          ) : (
                            item.tasks.map((task: any, tidx: number) => {
                              const isLastSub = tidx === item.tasks.length - 1;
                              return renderTask(
                                task,
                                tidx,
                                item.agent,
                                isLastSub
                              );
                            })
                          )}
                        </Timeline>
                      </Collapse>
                    </TimelineContent>
                  </TimelineItem>
                </React.Fragment>
              );
            } else {
              // Render single task (no agent or supervisor)
              return renderTask(item, idx, "ungrouped", isLastTopLevel);
            }
          })}
        </Timeline>
      </Box>
    </Box>
  );
}
