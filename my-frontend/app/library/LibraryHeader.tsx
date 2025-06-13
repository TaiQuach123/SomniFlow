import { LayoutList, Search } from "lucide-react";

export default function LibraryHeader({
  search,
  onSearchChange,
}: {
  search: string;
  onSearchChange: (v: string) => void;
}) {
  return (
    <div className="sticky top-0 z-40 w-full bg-white flex flex-col gap-0 px-4 py-0">
      <div className="flex items-center justify-between h-20 min-h-0 py-0 max-w-2xl mx-auto w-full">
        <div className="flex items-center gap-2">
          <LayoutList className="w-7 h-7 text-green-950" />
          <h1 className="text-2xl font-bold text-green-950">Library</h1>
        </div>
        <div className="relative w-96">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Search className="w-5 h-5" />
          </span>
          <input
            type="text"
            placeholder="Search your threads..."
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-100 bg-white text-gray-700"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
      </div>
      <hr className="border-t border-gray-200 w-full" />
    </div>
  );
}
