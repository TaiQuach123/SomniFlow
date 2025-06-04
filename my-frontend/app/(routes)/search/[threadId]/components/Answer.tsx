import React from "react";

export default function Answer({ data }: { data: string }) {
  return <div className="p-4 bg-green-50 rounded">Answer: {data}</div>;
}
