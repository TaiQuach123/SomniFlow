import React, { ElementType } from "react";
import ReactMarkdown from "react-markdown";

interface Source {
  ref?: number;
  url?: string;
  [key: string]: any;
}

function renderWithCitations(text: string, sources: Source[]) {
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
    const source = sources.find((s) => s.ref === refNum);
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
  sources: Source[]
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

export default function Answer({
  data,
  sources = [],
}: {
  data: string;
  sources?: Source[];
}) {
  return (
    <div className="bg-white dark:bg-neutral-900 rounded pb-8">
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
        {data}
      </ReactMarkdown>
    </div>
  );
}
