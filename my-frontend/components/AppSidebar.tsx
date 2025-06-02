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
} from "@/components/ui/sidebar";
import {
  Compass,
  GalleryHorizontalEnd,
  LogIn,
  LogOut,
  Search,
  User,
  Settings,
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

export function AppSidebar() {
  const path = usePathname();
  const { user, loading } = useAuth();
  const router = useRouter();

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
    {
      title: "Library",
      icon: GalleryHorizontalEnd,
      path: "/library",
    },
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
            </SidebarMenu>
            {/* Only show Sign Up if not authenticated */}
            {!user && !loading && (
              <Button className="rounded-full mx-4 mt-4" asChild>
                <Link href="/sign-up">Sign Up</Link>
              </Button>
            )}
          </SidebarContent>
        </SidebarGroup>
        <SidebarGroup />
      </SidebarContent>
      <SidebarFooter className="bg-accent">
        <div className="flex items-center gap-4 justify-between w-full">
          <Avatar className="transition-all duration-200 group hover:scale-105 hover:shadow-lg hover:border-2 hover:border-gray-300 hover:bg-gray-200 dark:hover:border-gray-700 dark:hover:bg-gray-700 hover:ring-2 hover:ring-gray-300 dark:hover:ring-gray-700">
            <AvatarImage src="https://ssl.gstatic.com/accounts/ui/avatar_2x.png" />
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
