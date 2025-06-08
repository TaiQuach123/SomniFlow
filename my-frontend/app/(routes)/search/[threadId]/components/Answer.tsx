import React from "react";

interface Source {
  ref?: number;
  url?: string;
  [key: string]: any;
}

export default function Answer({
  data,
  sources = [],
}: {
  data: string;
  sources?: Source[];
}) {
  // Replace [n] with clickable links if ref matches a source
  const citationRegex = /\[(\d+)\]/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;
  while ((match = citationRegex.exec(data)) !== null) {
    const idx = match.index;
    const refNum = parseInt(match[1], 10);
    // Push text before the citation
    if (idx > lastIndex) {
      parts.push(data.slice(lastIndex, idx));
    }
    // Find the source with this ref
    const source = sources.find((s) => s.ref === refNum);
    if (source && source.url) {
      parts.push(
        <a
          key={"cite-" + refNum + "-" + idx}
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block align-baseline mx-1 px-2 py-0.5 rounded bg-neutral-800 text-white text-xs font-bold"
        >
          {refNum}
        </a>
      );
    } else {
      parts.push(match[0]);
    }
    lastIndex = idx + match[0].length;
  }
  // Push any remaining text
  if (lastIndex < data.length) {
    parts.push(data.slice(lastIndex));
  }
  return <div className="p-4 bg-green-50 rounded">{parts}</div>;
}
