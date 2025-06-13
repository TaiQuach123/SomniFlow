import { useEffect, useState } from "react";

interface User {
  id: string;
  email: string;
  username?: string;
  thread_ids: string[];
  avatar_url?: string;
  // Add more fields as needed
}

interface AuthResult {
  user: User | null;
  loading: boolean;
}

function getAccessToken() {
  return typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
}

function emitAuthChange() {
  window.dispatchEvent(new Event("auth-changed"));
}

export function useAuth(): AuthResult {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Helper to check auth state
  const checkAuth = () => {
    const accessToken = getAccessToken();
    if (!accessToken) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
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
  };

  useEffect(() => {
    checkAuth();
    // Listen for storage changes (cross-tab)
    const onStorage = (e: StorageEvent) => {
      if (e.key === "access_token") {
        checkAuth();
      }
    };
    // Listen for custom event (same-tab)
    const onAuthChanged = () => {
      checkAuth();
    };
    window.addEventListener("storage", onStorage);
    window.addEventListener("auth-changed", onAuthChanged);
    return () => {
      window.removeEventListener("storage", onStorage);
      window.removeEventListener("auth-changed", onAuthChanged);
    };
  }, []);

  return { user, loading };
}

// Export emitAuthChange for use in login/logout
export { emitAuthChange }; 