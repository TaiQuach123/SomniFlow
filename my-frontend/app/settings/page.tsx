"use client";
import Settings from "@/components/Settings";
import React, { useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SettingPage() {
  const router = useRouter();
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      router.back();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-md"
      onClick={handleBackdropClick}
      style={{ minHeight: "100vh" }}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-lg p-8 relative z-60 min-w-[320px] max-w-full"
      >
        <Settings />
      </div>
    </div>
  );
}
