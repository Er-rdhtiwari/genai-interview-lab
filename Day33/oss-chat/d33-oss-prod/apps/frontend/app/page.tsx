"use client";

import { useMemo, useState } from "react";

type ChatResp = {
  reply: string;
  model: string;
  provider: string;
  request_id: string;
  metrics?: Record<string, unknown> | null;
};

function joinUrl(base: string, path: string) {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!base) return p;               // <--- key
  const b = base.replace(/\/+$/, "");
  return `${b}${p}`;
}


export default function Page() {
  const apiBase = useMemo(() => process.env.NEXT_PUBLIC_API_BASE_URL || "", []);

  const [message, setMessage] = useState("Hello 👋");
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<ChatResp | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    setLoading(true);
    setError(null);
    setResp(null);

    const url = joinUrl(apiBase, "/api/chat");
    const requestId =
      (globalThis.crypto?.randomUUID?.() as string | undefined) ||
      `req-${Date.now()}`;

    try {
      const r = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-request-id": requestId
        },
        body: JSON.stringify({ message })
      });

      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        throw new Error(
          `API ${r.status}: ${typeof data?.detail === "string" ? data.detail : "request_failed"}`
        );
      }

      setResp(data as ChatResp);
    } catch (e: any) {
      setError(e?.message || "unknown_error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2 style={{ marginTop: 0 }}>d33-oss-prod Chat</h2>
      <p style={{ marginTop: 0 }}>
        API Base: <code>{apiBase}</code>
      </p>

      <label>
        <small>Message</small>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
      </label>

      <div style={{ marginTop: 12 }} className="row">
        <button onClick={send} disabled={loading || !message.trim()}>
          {loading ? "Sending..." : "Send"}
        </button>
        <div style={{ alignSelf: "center" }}>
          <small>Calls: {joinUrl(apiBase, "/api/chat")}</small>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: 16 }}>
          <small style={{ color: "crimson" }}>Error: {error}</small>
        </div>
      )}

      {resp && (
        <div style={{ marginTop: 16 }}>
          <h4 style={{ marginBottom: 8 }}>Reply</h4>
          <pre style={{ marginTop: 0 }}>{resp.reply}</pre>
          <small>
            Provider: <b>{resp.provider}</b> | Model: <b>{resp.model}</b> | Request ID:{" "}
            <b>{resp.request_id}</b>
          </small>
        </div>
      )}
    </div>
  );
}
