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
import AssessmentIcon from "@mui/icons-material/Assessment";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import PsychologyIcon from "@mui/icons-material/Psychology";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ChatIcon from "@mui/icons-material/Chat";
import { Spinner } from "@/components/ui/spinner";

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

// Function to get task-specific icon
function getTaskIcon(taskType: string, taskData?: string, taskLabel?: string) {
  // Special case for "Finished" step - check both data and label
  if (
    taskType === "step" &&
    (taskData === "Finished" || taskLabel === "Finished")
  ) {
    return <CheckCircleIcon fontSize="small" sx={{ color: "#10b981" }} />;
  }

  switch (taskType) {
    case "retrieval":
      return <Search className="w-4 h-4" style={{ color: "#1a1a1a" }} />;
    case "webSearch":
      return <Search className="w-4 h-4" style={{ color: "#1a1a1a" }} />;
    case "evaluation":
      return <AssessmentIcon fontSize="small" sx={{ color: "#374151" }} />;
    case "contextExtraction":
      return <AutoStoriesIcon fontSize="small" sx={{ color: "#374151" }} />;
    case "reflection":
      return <PsychologyIcon fontSize="small" sx={{ color: "#374151" }} />;
    case "step":
      // Handle other step tasks based on their data/label
      return <InfoOutlinedIcon fontSize="small" sx={{ color: "#374151" }} />;
    case "planning":
      return <LightbulbIcon fontSize="small" sx={{ color: "#374151" }} />;
    default:
      return <InfoOutlinedIcon fontSize="small" sx={{ color: "#374151" }} />;
  }
}

// Function to determine if a task is currently running
function isTaskRunning(task: any) {
  // A task is running if it has a type but hasn't been marked as ended
  if (!task || task === null) return false;

  // Check if the task has been explicitly marked as completed or ended
  if (task.completed || task.ended) {
    return false;
  }

  // Check if this is a retrieval or webSearch task
  if (task.type === "retrieval" || task.type === "webSearch") {
    // These tasks are running if they haven't been marked as completed
    return true;
  }

  // Check if this is a step task that might be running
  if (task.type === "step") {
    // Step tasks are typically completed when they appear in the timeline
    // since they represent completed steps
    return false;
  }

  // Check for new task types that have start/end events
  if (
    task.type === "evaluation" ||
    task.type === "contextExtraction" ||
    task.type === "reflection" ||
    task.type === "planning"
  ) {
    // These tasks are running if they haven't been marked as completed
    return true;
  }

  return false;
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
            color={isTaskRunning(task) ? "primary" : "grey"}
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
              ...(isTaskRunning(task) && {
                animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "@keyframes pulse": {
                  "0%, 100%": {
                    opacity: 1,
                    transform: "scale(1)",
                  },
                  "50%": {
                    opacity: 0.7,
                    transform: "scale(1.1)",
                  },
                },
              }),
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
            {/* Show spinner for running tasks */}
            {isTaskRunning(task) && (
              <Box sx={{ mr: 1, display: "flex", alignItems: "center" }}>
                <Spinner size={14} color="primary" />
              </Box>
            )}
            {/* Show completion indicator for finished tasks */}
            {!isTaskRunning(task) && (task.completed || task.ended) && (
              <Box sx={{ mr: 1, display: "flex", alignItems: "center" }}>
                <CheckCircleIcon fontSize="small" sx={{ color: "#10b981" }} />
              </Box>
            )}
            {/* Show task-specific icon only when task is not running */}
            {!isTaskRunning(task) && (
              <Box sx={{ mr: 1, display: "flex", alignItems: "center" }}>
                {getTaskIcon(task.type, task.data, task.label)}
              </Box>
            )}
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
                : task.type === "evaluation"
                ? "Evaluating Local Retrieval"
                : task.type === "contextExtraction"
                ? "Analyzing Retrieved Content"
                : task.type === "reflection"
                ? "Quality Assessment"
                : task.type === "planning"
                ? "Planning"
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
                <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                  <Typography
                    variant="body2"
                    sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                  >
                    Searching
                  </Typography>
                  {/* Show spinner if task is running but no queries yet */}
                  {isTaskRunning(task) &&
                    (!Array.isArray(task.searching) ||
                      task.searching.length === 0) && (
                      <Spinner size={12} color="primary" />
                    )}
                </Box>
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
                      {isTaskRunning(task)
                        ? "Processing queries..."
                        : "No queries"}
                    </Typography>
                  )}
                </Stack>
              </Box>
              {/* Reading */}
              <Box ml={2} mb={1.5}>
                <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                  <Typography
                    variant="body2"
                    sx={{ fontSize: 12, fontWeight: 500, color: "#374151" }}
                  >
                    Reading
                  </Typography>
                  {/* Show spinner if task is running but no sources yet */}
                  {isTaskRunning(task) &&
                    (!Array.isArray(task.reading) ||
                      task.reading.length === 0) && (
                      <Spinner size={12} color="primary" />
                    )}
                </Box>
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
                      const sourceUrl = getSourceUrl(src);
                      return (
                        <Box key={i} component="span" sx={{ mb: 1 }}>
                          <Chip
                            component={sourceUrl ? "a" : "span"}
                            href={sourceUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            clickable={!!sourceUrl}
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
                      {isTaskRunning(task)
                        ? "Processing sources..."
                        : "No sources"}
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
                          ...(item.tasks.some((task: any) =>
                            isTaskRunning(task)
                          ) && {
                            animation:
                              "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                            "@keyframes pulse": {
                              "0%, 100%": {
                                opacity: 1,
                                transform: "scale(1)",
                              },
                              "50%": {
                                opacity: 0.7,
                                transform: "scale(1.1)",
                              },
                            },
                          }),
                        }}
                      />
                      {!isLastTopLevel && (
                        <TimelineConnector sx={{ width: 1.5 }} />
                      )}
                    </TimelineSeparator>
                    <TimelineContent sx={{ py: 0, minWidth: 0, pl: 0, ml: 2 }}>
                      <Box display="flex" alignItems="center" mb={0.5} mt={0.5}>
                        {/* Show spinner for agent if it has running tasks */}
                        {item.tasks.some((task: any) =>
                          isTaskRunning(task)
                        ) && (
                          <Box
                            sx={{
                              mr: 1,
                              display: "flex",
                              alignItems: "center",
                            }}
                          >
                            <Spinner size={16} color="primary" />
                          </Box>
                        )}
                        {/* Show completion indicator for agent if all tasks are done */}
                        {!item.tasks.some((task: any) => isTaskRunning(task)) &&
                          item.tasks.some(
                            (task: any) => task.completed || task.ended
                          ) && (
                            <Box
                              sx={{
                                mr: 1,
                                display: "flex",
                                alignItems: "center",
                              }}
                            >
                              <CheckCircleIcon
                                fontSize="small"
                                sx={{ color: "#10b981" }}
                              />
                            </Box>
                          )}
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
