"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { LogIn } from "lucide-react";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Registration failed");
        setLoading(false);
        return;
      }
      const data = await res.json();
      setSuccess("Registration successful! Redirecting to login...");
      setLoading(false);
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError("An error occurred. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-lg min-h-[42rem]">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold">
            Create your account
          </CardTitle>
          <CardDescription className="text-center text-sm">
            Enter your email and password to sign up
          </CardDescription>
          {/* <CardAction>
            <Button variant="link">Sign Up</Button>
          </CardAction> */}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                />
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  {/* <a
                    href="#"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a> */}
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                />
              </div>
              {error && (
                <div className="text-red-500 text-sm text-center">{error}</div>
              )}
              {success && (
                <div className="text-green-600 text-sm text-center">
                  {success}
                </div>
              )}
            </div>
            <Button
              type="submit"
              className="w-full flex items-center justify-center gap-2 mt-6"
              disabled={loading}
            >
              {loading ? (
                "Signing up..."
              ) : (
                <>
                  Sign up
                  <LogIn className="w-4 h-4 mr-2" />
                </>
              )}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex-col gap-2">
          <div className="flex items-center w-full my-4">
            <div className="flex-grow border-t border-gray-200"></div>
            <span className="mx-4 text-gray-400 font-normal">or</span>
            <div className="flex-grow border-t border-gray-200"></div>
          </div>
          <Button
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
            onClick={() => {
              window.location.href = "http://127.0.0.1:8000/auth/google/login";
            }}
            disabled={loading}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 48 48"
              className="mr-2"
            >
              <g>
                <path
                  fill="#4285F4"
                  d="M43.6 20.5h-1.9V20H24v8h11.3c-1.6 4.3-5.7 7-11.3 7-6.6 0-12-5.4-12-12s5.4-12 12-12c2.7 0 5.2.9 7.2 2.4l6-6C34.5 5.1 29.5 3 24 3 12.9 3 4 11.9 4 23s8.9 20 20 20c11 0 19.7-8 19.7-20 0-1.3-.1-2.7-.3-4z"
                />
                <path
                  fill="#34A853"
                  d="M6.3 14.7l6.6 4.8C14.5 16.1 18.9 13 24 13c2.7 0 5.2.9 7.2 2.4l6-6C34.5 5.1 29.5 3 24 3 15.3 3 7.9 8.7 6.3 14.7z"
                />
                <path
                  fill="#FBBC05"
                  d="M24 43c5.3 0 10.1-1.8 13.8-4.9l-6.4-5.2C29.2 34.5 26.7 35.5 24 35.5c-5.5 0-10.1-3.7-11.7-8.7l-6.6 5.1C7.9 39.3 15.3 43 24 43z"
                />
                <path
                  fill="#EA4335"
                  d="M43.6 20.5h-1.9V20H24v8h11.3c-1.1 3-3.6 5.2-6.3 6.3l6.4 5.2C40.7 36.1 44 30.5 44 24c0-1.3-.1-2.7-.4-3.5z"
                />
              </g>
            </svg>
            Continue with Google
          </Button>

          <div className="text-center text-sm mt-6 pt-4 border-t border-gray-100">
            Already have an account?{" "}
            <Link href="/login" className="text-blue-500 font-bold">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
