import { useEffect, useState } from "react";

interface User {
  id: string;
  email: string;
  username?: string;
  // Add more fields as needed
}

interface AuthResult {
  user: User | null;
  loading: boolean;
}

export function useAuth(): AuthResult {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const accessToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!accessToken) {
      setUser(null);
      setLoading(false);
      return;
    }
    fetch("http://localhost:8000/auth/me", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then((data) => {
        if (data.authenticated) {
          setUser(data.user);
        } else {
          setUser(null);
        }
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return { user, loading };
} 