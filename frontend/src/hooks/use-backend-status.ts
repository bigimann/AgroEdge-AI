"use client";

import { useEffect, useState } from "react";
import { checkBackendHealth } from "../lib/api";

export type ConnectionStatus = "checking" | "connected" | "offline";

const POLL_INTERVAL_MS = 15000;

export function useBackendStatus(): ConnectionStatus {
  const [status, setStatus] = useState<ConnectionStatus>("checking");

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const healthy = await checkBackendHealth();
      if (!cancelled) {
        setStatus(healthy ? "connected" : "offline");
      }
    }

    poll();
    const interval = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return status;
}
