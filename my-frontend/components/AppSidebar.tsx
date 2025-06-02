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

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "./ui/button";
export function AppSidebar() {
  const path = usePathname();
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
    {
      title: "Sign In",
      icon: LogIn,
      path: "/sign-in",
    },
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
                      className={`p-5 py-6 hover:bg-transparent hover:font-bold ${
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
            <Button className="rounded-full mx-4 mt-4">Sign Up</Button>
          </SidebarContent>
        </SidebarGroup>
        <SidebarGroup />
      </SidebarContent>
      <SidebarFooter className="bg-accent">
        <div className="flex items-center gap-4 justify-between">
          <Avatar>
            <AvatarImage src="https://ssl.gstatic.com/accounts/ui/avatar_2x.png" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
          <h3 className="text-lg font-bold">Guest</h3>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Settings />
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
                  <DropdownMenuSubTrigger>Invite users</DropdownMenuSubTrigger>
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
              <DropdownMenuItem>
                Log out
                <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
