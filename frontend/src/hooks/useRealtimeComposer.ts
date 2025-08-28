import { useEffect, useRef, useState } from "react";

interface SubscriptionOptions {
  topics: string[];
  token: string;
  onEvent?: (evt: any) => void;
  reconnect?: boolean;
}

interface RealtimeState {
  connected: boolean;
  lastEventTs?: number;
  errors: number;
}

export function useRealtimeComposer(opts: SubscriptionOptions) {
  const { topics, token, onEvent, reconnect = true } = opts;
  const [state, setState] = useState<RealtimeState>({ connected: false, errors: 0 });
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);

  useEffect(() => {
    let closedByUser = false;
    function connect() {
      const url = new URL("/ws", location.origin.replace("http", "ws"));
      url.searchParams.set("topics", topics.join(","));
      url.searchParams.set("access_token", token);
      const ws = new WebSocket(url.toString());
      wsRef.current = ws;

      ws.onopen = () => {
        backoffRef.current = 1000;
        setState((s) => ({ ...s, connected: true }));
      };
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "event" || msg.type === "stream") {
            onEvent && onEvent(msg);
            setState((s) => ({ ...s, lastEventTs: Date.now() }));
          }
        } catch (e) {
          console.warn("Realtime parse error", e);
        }
      };
      ws.onclose = () => {
        setState((s) => ({ ...s, connected: false }));
        if (!closedByUser && reconnect) {
          setTimeout(connect, backoffRef.current);
          backoffRef.current = Math.min(backoffRef.current * 2, 15000);
        }
      };
      ws.onerror = () => {
        setState((s) => ({ ...s, errors: s.errors + 1 }));
      };
    }
    connect();
    return () => {
      closedByUser = true;
      wsRef.current?.close();
    };
  }, [topics.join(","), token]);

  return state;
}