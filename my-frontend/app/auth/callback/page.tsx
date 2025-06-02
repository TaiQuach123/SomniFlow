// app/auth/callback/page.tsx
"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    // Optionally: const refreshToken = searchParams.get("refresh_token");
    if (accessToken) {
      localStorage.setItem("access_token", accessToken);
      // Optionally: localStorage.setItem("refresh_token", refreshToken);
      router.replace("/"); // Redirect to home or dashboard
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-white">
      <div className="bg-white shadow-lg rounded-xl px-8 py-10 flex flex-col items-center w-full max-w-md">
        <div className="mb-6">
          <svg
            className="animate-spin text-blue-600"
            width="48"
            height="48"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="24"
              cy="24"
              r="20"
              stroke="#cbd5e1"
              strokeWidth="4"
              opacity="0.3"
            />
            <path
              d="M44 24c0-11.046-8.954-20-20-20"
              stroke="#1976d2"
              strokeWidth="4"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="text-xl font-semibold mb-2 text-gray-800 text-center">
          Connecting your account…
        </div>
        <div className="text-gray-500 mb-6 text-center">
          Please wait while we securely log you in. You'll be redirected in a
          moment.
        </div>
        <a
          href="/"
          className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm font-medium shadow"
        >
          Not redirected? Click here
        </a>
      </div>
    </div>
  );
}
