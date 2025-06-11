import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Clock, MoreVertical, Trash } from "lucide-react";
import { timeAgo } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

interface HeaderProps {
  avatarUrl: string;
  userMessageTime: string;
}

export default function Header({ avatarUrl, userMessageTime }: HeaderProps) {
  return (
    <div className="sticky top-0 z-40 w-full bg-white dark:bg-neutral-900 flex flex-col gap-0 px-4 py-0">
      <div className="flex items-center gap-2 h-12 min-h-0 py-0">
        <Avatar className="w-8 h-8">
          <AvatarImage src={avatarUrl} alt="User avatar" />
          <AvatarFallback>U</AvatarFallback>
        </Avatar>
        <Clock className="text-gray-500" size={18} />
        <span className="text-gray-500 text-sm leading-none">
          {userMessageTime ? timeAgo(userMessageTime) : ""}
        </span>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="fixed top-2 right-2 rounded-full p-2 hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
              aria-label="More options"
              style={{ lineHeight: 0 }}
            >
              <MoreVertical className="text-gray-500" size={20} />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Trash className="w-4 h-4 mr-2" /> Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <hr className="mt-2 border-t border-gray-200 w-full" />
    </div>
  );
}
