import { useEffect, useState } from "react";
import type { DemoSession } from "../../types";
import { loadCurrentSession, login, logout } from "./sessionApi";

type SessionStatus = "loading" | "authenticated" | "anonymous";

export function useSession() {
  const [session, setSession] = useState<DemoSession | null>(null);
  const [status, setStatus] = useState<SessionStatus>("loading");

  useEffect(() => {
    let cancelled = false;

    loadCurrentSession()
      .then((currentSession) => {
        if (cancelled) {
          return;
        }
        setSession(currentSession);
        setStatus("authenticated");
      })
      .catch(() => {
        if (cancelled) {
          return;
        }
        setSession(null);
        setStatus("anonymous");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function loginWithPassword(email: string, password: string) {
    const nextSession = await login({ email, password });
    setSession(nextSession);
    setStatus("authenticated");
    return nextSession;
  }

  async function logoutCurrentSession() {
    try {
      await logout();
    } finally {
      setSession(null);
      setStatus("anonymous");
    }
  }

  return {
    session,
    status,
    loginWithPassword,
    logoutCurrentSession,
  };
}
