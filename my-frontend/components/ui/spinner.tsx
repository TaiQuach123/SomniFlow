import React from "react";
import { CircularProgress } from "@mui/material";

interface SpinnerProps {
  /** Size of the spinner in pixels */
  size?: number;
  /** Color theme of the spinner */
  color?: "primary" | "secondary" | "error" | "info" | "success" | "warning";
  /** Additional CSS classes */
  className?: string;
}

/**
 * Spinner component for showing loading states
 * Uses Material-UI's CircularProgress with rounded stroke caps
 */
export function Spinner({
  size = 16,
  color = "primary",
  className = "",
}: SpinnerProps) {
  return (
    <CircularProgress
      size={size}
      color={color}
      className={className}
      sx={{
        "& .MuiCircularProgress-circle": {
          strokeLinecap: "round",
        },
      }}
    />
  );
}

export default Spinner;
