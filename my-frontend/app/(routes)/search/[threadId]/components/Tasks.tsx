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
                          sx={{
                            fontSize: 12,
                            fontWeight: 500,
                            color: "#374151",
                          }}
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
                              sx={{
                                fontSize: 12,
                                fontWeight: 500,
                                color: "#374151",
                              }}
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
                          sx={{
                            fontSize: 12,
                            fontWeight: 500,
                            color: "#374151",
                          }}
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
                              sx={{
                                fontSize: 12,
                                fontWeight: 500,
                                color: "#374151",
                              }}
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
          })}
        </Timeline>
      </Box>
    </Box>
  );
}
