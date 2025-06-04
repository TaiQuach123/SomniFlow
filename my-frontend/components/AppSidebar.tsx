"use client";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
} from "@/components/ui/sidebar";
import {
  Compass,
  GalleryHorizontalEnd,
  LogIn,
  LogOut,
  Search,
  User,
  Settings,
  ChevronDown,
  ChevronUp,
  ChevronRight,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "./ui/button";
import { useAuth } from "@/hooks/useAuth";
import { emitAuthChange } from "@/hooks/useAuth";
import { useEffect, useState } from "react";

export function AppSidebar() {
  const path = usePathname();
  const { user, loading } = useAuth();
  const router = useRouter();

  // State for Library collapse
  const [libraryOpen, setLibraryOpen] = useState(true);
  // State for chat sessions
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setSessionsLoading(true);
      const accessToken =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;
      fetch("/api/chats", {
        credentials: "include",
        headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      })
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            // Sort by last_updated descending
            data.sort((a, b) => {
              if (!a.last_updated) return 1;
              if (!b.last_updated) return -1;
              return (
                new Date(b.last_updated).getTime() -
                new Date(a.last_updated).getTime()
              );
            });
            setSessions(data.slice(0, 3));
          } else {
            setSessions([]);
          }
        })
        .catch(() => setSessions([]))
        .finally(() => setSessionsLoading(false));
    } else {
      setSessions([]);
    }
  }, [user]);

  const handleLogout = async () => {
    try {
      await fetch("/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      // Optionally handle error
    } finally {
      localStorage.removeItem("access_token");
      emitAuthChange();
      router.refresh(); // reloads the current route
    }
  };

  const menuOptions = [
    {
      title: "Home",
      icon: Search,
      path: "/",
    },
    {
      title: "Discover",
      icon: Compass,
      path: "/discover",
    },
    // Library will be handled separately
    // Only show Sign In if not authenticated
    ...(!user && !loading
      ? [
          {
            title: "Sign In",
            icon: LogIn,
            path: "/login",
          },
        ]
      : []),
  ];
  return (
    <Sidebar>
      <SidebarHeader className="bg-accent flex items-center py-5">
        <Image src="/logo2.png" alt="logo" width={100} height={50} />
      </SidebarHeader>
      <SidebarContent className="bg-accent">
        {/* <SidebarGroupLabel>Menu</SidebarGroupLabel> */}
        <SidebarGroup>
          <SidebarContent>
            <SidebarMenu>
              {menuOptions.map((menu, index) => {
                return (
                  <SidebarMenuItem key={index}>
                    <SidebarMenuButton
                      asChild
                      className={`p-5 py-6 hover:bg-gray-200 dark:hover:bg-gray-700 hover:font-bold transition-transform duration-150 hover:scale-105 hover:shadow-md ${
                        (menu.path === "/" && path === "/") ||
                        (menu.path !== "/" && path?.includes(menu.path))
                          ? "font-bold"
                          : ""
                      }`}
                    >
                      <Link href={menu.path}>
                        <menu.icon className="h-8 w-8" />
                        <span className="text-lg">{menu.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
              {/* Library collapsible menu item */}
              <SidebarMenuItem>
                <div className="flex flex-col w-full">
                  <button
                    className={`flex items-center w-full p-5 py-3 hover:bg-gray-200 dark:hover:bg-gray-700 hover:font-bold transition-transform duration-150 hover:scale-105 hover:shadow-md font-bold focus:outline-none text-base`}
                    onClick={user ? () => setLibraryOpen((v) => !v) : undefined}
                    aria-expanded={user ? libraryOpen : undefined}
                    style={{ minHeight: 56 }}
                    disabled={!user}
                  >
                    <GalleryHorizontalEnd className="h-8 w-8 mr-2" />
                    <span className="flex-1 text-left">Library</span>
                    {user &&
                      (libraryOpen ? (
                        <ChevronDown className="h-5 w-5 ml-2" />
                      ) : (
                        <ChevronRight className="h-5 w-5 ml-2" />
                      ))}
                  </button>
                  {user && libraryOpen && (
                    <SidebarMenuSub
                      className="mt-1 !border-l-0"
                      style={{ borderLeft: "none" }}
                    >
                      <div className="relative pl-4">
                        {sessions.length > 0 && (
                          <span
                            className="absolute left-2 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"
                            style={{ borderRadius: 2 }}
                            aria-hidden="true"
                          />
                        )}
                        {sessionsLoading ? (
                          <SidebarMenuSubItem>
                            <span className="text-xs text-gray-500">
                              Loading...
                            </span>
                          </SidebarMenuSubItem>
                        ) : sessions.length === 0 ? (
                          <SidebarMenuSubItem>
                            <span className="text-xs text-gray-500">
                              No sessions
                            </span>
                          </SidebarMenuSubItem>
                        ) : (
                          sessions.map((session) => {
                            const isActive = path?.includes(session.thread_id);
                            return (
                              <SidebarMenuSubItem
                                key={session.thread_id}
                                className="min-w-0 group"
                              >
                                <SidebarMenuSubButton
                                  asChild
                                  isActive={isActive}
                                  className="min-w-0 p-0"
                                  style={{ maxWidth: 180, overflow: "hidden" }}
                                >
                                  <Link
                                    href={`/search/${session.thread_id}`}
                                    className={`
                                      truncate min-w-0 max-w-[120px] overflow-hidden whitespace-nowrap font-medium text-gray-500 !text-gray-500 text-xs
                                      flex items-center h-7 px-2 rounded-md
                                      ${
                                        isActive
                                          ? "!bg-gray-300 dark:!bg-gray-800"
                                          : "hover:!bg-gray-200 dark:hover:!bg-gray-700"
                                      }
                                      transition-colors duration-150
                                    `}
                                    title={session.title || "Untitled"}
                                  >
                                    {session.title || "Untitled"}
                                  </Link>
                                </SidebarMenuSubButton>
                              </SidebarMenuSubItem>
                            );
                          })
                        )}
                      </div>
                    </SidebarMenuSub>
                  )}
                </div>
              </SidebarMenuItem>
            </SidebarMenu>
            {/* Only show Sign Up if not authenticated */}
            {!user && !loading && (
              <Button className="rounded-full mx-4 mt-4" asChild>
                <Link href="/register">Sign Up</Link>
              </Button>
            )}
          </SidebarContent>
        </SidebarGroup>
        <SidebarGroup />
      </SidebarContent>
      <SidebarFooter className="bg-accent">
        <div className="flex items-center gap-4 justify-between w-full">
          <Avatar className="transition-all duration-200 group hover:scale-105 hover:shadow-lg hover:border-2 hover:border-gray-300 hover:bg-gray-200 dark:hover:border-gray-700 dark:hover:bg-gray-700 hover:ring-2 hover:ring-gray-300 dark:hover:ring-gray-700">
            <AvatarImage
              src={
                user && user.avatar_url
                  ? user.avatar_url
                  : "https://ssl.gstatic.com/accounts/ui/avatar_2x.png"
              }
            />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
          {!loading && (
            <Tooltip>
              <TooltipTrigger asChild>
                <h3 className="text-base font-medium truncate max-w-[120px] cursor-pointer">
                  {user ? user.username || user.email : "Guest"}
                </h3>
              </TooltipTrigger>
              <TooltipContent side="top" align="center">
                {user ? user.username || user.email : "Guest"}
              </TooltipContent>
            </Tooltip>
          )}

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <span className="rounded-full bg-gray-100 dark:bg-gray-800 transition-all duration-200 p-1 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-700 hover:ring-2 hover:ring-gray-300 dark:hover:ring-gray-700">
                  <Settings className="cursor-pointer text-inherit transition-all duration-200 hover:rotate-12 hover:scale-110" />
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="start">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuGroup>
                  <DropdownMenuItem>
                    Profile
                    <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    Billing
                    <DropdownMenuShortcut>⌘B</DropdownMenuShortcut>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    Settings
                    <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    Keyboard shortcuts
                    <DropdownMenuShortcut>⌘K</DropdownMenuShortcut>
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem>Team</DropdownMenuItem>
                  <DropdownMenuSub>
                    <DropdownMenuSubTrigger>
                      Invite users
                    </DropdownMenuSubTrigger>
                    <DropdownMenuPortal>
                      <DropdownMenuSubContent>
                        <DropdownMenuItem>Email</DropdownMenuItem>
                        <DropdownMenuItem>Message</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>More...</DropdownMenuItem>
                      </DropdownMenuSubContent>
                    </DropdownMenuPortal>
                  </DropdownMenuSub>
                  <DropdownMenuItem>
                    New Team
                    <DropdownMenuShortcut>⌘+T</DropdownMenuShortcut>
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuItem>GitHub</DropdownMenuItem>
                <DropdownMenuItem>Support</DropdownMenuItem>
                <DropdownMenuItem disabled>API</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  Log out
                  <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <span className="rounded-full bg-gray-100 dark:bg-gray-800 transition-all duration-200 p-1 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-700 hover:ring-2 hover:ring-gray-300 dark:hover:ring-gray-700">
                  <User className="cursor-pointer text-inherit transition-all duration-200 hover:scale-110" />
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-44" align="start">
                <DropdownMenuLabel>Welcome</DropdownMenuLabel>
                <DropdownMenuItem asChild>
                  <Link href="/login">Sign In</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/sign-up">Sign Up</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
