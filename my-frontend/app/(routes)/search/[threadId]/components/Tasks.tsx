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
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";

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

export default function Tasks({ tasks }: { tasks: any[] }) {
  const [collapsed, setCollapsed] = useState<{ [k: number]: boolean }>({});
  const toggleCollapse = (idx: number) => {
    setCollapsed((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <Box sx={{ bgcolor: "background.default", borderRadius: 2, p: 2, pl: 0 }}>
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
          {tasks.map((task, idx) => {
            const isLast = idx === tasks.length - 1;
            const subtasks = hasSubtasks(task);
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
                <TimelineContent sx={{ py: 0, minWidth: 0, pl: 0, ml: 0 }}>
                  <Box
                    display="flex"
                    alignItems="center"
                    mb={subtasks ? 0.5 : 0}
                    mt={0.5}
                  >
                    <Typography
                      variant="subtitle1"
                      fontWeight={600}
                      color="text.primary"
                      sx={{ userSelect: "none" }}
                    >
                      {task.type === "retrieval"
                        ? "Searching local data"
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
                        onClick={() => toggleCollapse(idx)}
                        sx={{ ml: 1 }}
                      >
                        {collapsed[idx] ? (
                          <ChevronRightIcon fontSize="small" />
                        ) : (
                          <ExpandMoreIcon fontSize="small" />
                        )}
                      </IconButton>
                    )}
                  </Box>
                  {subtasks ? (
                    <Collapse in={!collapsed[idx]}>
                      {/* Searching */}
                      <Box mb={1} ml={2}>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          color="text.secondary"
                        >
                          Searching
                        </Typography>
                        <Stack direction="column" spacing={0.5} mt={0.5}>
                          {Array.isArray(task.searching) &&
                          task.searching.length > 0 ? (
                            task.searching.map((query: string, i: number) => (
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
                            ))
                          ) : (
                            <Typography variant="body2" color="text.disabled">
                              No queries
                            </Typography>
                          )}
                        </Stack>
                      </Box>
                      {/* Reading */}
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
                                    label={
                                      src.type === "local" ? filename : domain
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
                            <Typography variant="body2" color="text.disabled">
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
          })}
        </Timeline>
      </Box>
    </Box>
  );
}
