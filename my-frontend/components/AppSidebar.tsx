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
import useSWR from "swr";

export function AppSidebar() {
  const path = usePathname();
  const { user, loading } = useAuth();
  const router = useRouter();

  // State for Library collapse
  const [libraryOpen, setLibraryOpen] = useState(true);
  // Use SWR for chat sessions
  const {
    data: sessions = [],
    isLoading: sessionsLoading,
    mutate,
  } = useSWR(
    user ? "/api/chats" : null,
    (url) =>
      fetch(url, {
        credentials: "include",
        headers:
          typeof window !== "undefined" && localStorage.getItem("access_token")
            ? {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
              }
            : {},
      }).then((res) => res.json()),
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

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
    // Sign In will be rendered below Library
  ];
  return (
    <Sidebar className="bg-gray-100 text-gray-900">
      <SidebarHeader className="!flex-row items-center w-full gap-3 py-5 bg-gray-100">
        <Image src="/logo.svg" alt="logo" width={56} height={56} />
        <span className="text-2xl font-bold tracking-tight text-gray-900 flex items-center h-[56px]">
          SomniFlow
        </span>
      </SidebarHeader>
      <SidebarContent className="bg-gray-100">
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
                  <div
                    className="flex items-center w-full p-5 py-3 hover:bg-gray-200 dark:hover:bg-gray-700 hover:font-bold transition-transform duration-150 hover:scale-105 hover:shadow-md font-bold focus:outline-none text-base"
                    style={{ minHeight: 56 }}
                  >
                    <Link
                      href="/library"
                      className="flex items-center flex-1 min-w-0"
                      tabIndex={user ? 0 : -1}
                      aria-disabled={!user}
                      style={{
                        pointerEvents: user ? "auto" : "none",
                        opacity: user ? 1 : 0.5,
                      }}
                    >
                      <GalleryHorizontalEnd className="h-8 w-8 mr-2" />
                      <span className="text-left">Library</span>
                    </Link>
                    {user && (
                      <button
                        type="button"
                        className="ml-2 p-1 rounded hover:bg-gray-300 dark:hover:bg-gray-800"
                        aria-label={
                          libraryOpen ? "Collapse sessions" : "Expand sessions"
                        }
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setLibraryOpen((v) => !v);
                        }}
                        tabIndex={0}
                      >
                        {libraryOpen ? (
                          <ChevronDown className="h-5 w-5" />
                        ) : (
                          <ChevronRight className="h-5 w-5" />
                        )}
                      </button>
                    )}
                  </div>
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
                          [...sessions]
                            .sort((a: any, b: any) => {
                              if (!a.last_updated) return 1;
                              if (!b.last_updated) return -1;
                              return (
                                new Date(b.last_updated).getTime() -
                                new Date(a.last_updated).getTime()
                              );
                            })
                            .slice(0, 3)
                            .map((session: any) => {
                              const isActive = path?.includes(
                                session.thread_id
                              );
                              return (
                                <SidebarMenuSubItem
                                  key={session.thread_id}
                                  className="min-w-0 group"
                                >
                                  <SidebarMenuSubButton
                                    asChild
                                    isActive={isActive}
                                    className="min-w-0 p-0"
                                    style={{
                                      maxWidth: 180,
                                      overflow: "hidden",
                                    }}
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
              {/* Move Sign In below Library */}
              {!user && !loading && (
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    className={`p-5 py-6 hover:bg-gray-200 dark:hover:bg-gray-700 hover:font-bold transition-transform duration-150 hover:scale-105 hover:shadow-md ${
                      path === "/login" ? "font-bold" : ""
                    }`}
                  >
                    <Link href="/login">
                      <LogIn className="h-8 w-8" />
                      <span className="text-lg">Sign In</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              )}
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
      <SidebarFooter className="bg-gray-100">
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
