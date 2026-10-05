"use client";

import { useState, useRef, useEffect } from "react";

type ChatTurn = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [token, setToken] = useState("");
  const [role, setRole] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);

  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatTurn[]>([]);
  const [sending, setSending] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleLogin = async () => {
    setLoginError("");
    setLoggingIn(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.error) {
        setLoginError(data.error);
        return;
      }
      setToken(data.token);
      setRole(data.role);
    } catch {
      setLoginError("Could not reach the server. Is the backend running?");
    } finally {
      setLoggingIn(false);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || sending) return;
    const userTurn: ChatTurn = { role: "user", content: message };
    setHistory((h) => [...h, userTurn]);
    setMessage("");
    setSending(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({ message: userTurn.content }),
      });
      const data = await res.json();
      setHistory((h) => [
        ...h,
        { role: "assistant", content: data.response ?? "No response received." },
      ]);
    } catch {
      setHistory((h) => [
        ...h,
        { role: "assistant", content: "Something went wrong reaching the assistant." },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleLogout = () => {
    setToken("");
    setRole("");
    setEmail("");
    setPassword("");
    setHistory([]);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 mb-4">
              <span className="text-emerald-400 text-lg">◆</span>
            </div>
            <h1 className="text-xl font-medium text-neutral-50">Agentic Ops</h1>
            <p className="text-sm text-neutral-500 mt-1">Sign in to the support console</p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs text-neutral-500 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                placeholder="you@company.com"
                className="w-full rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-600 outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs text-neutral-500 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                placeholder="••••••••"
                className="w-full rounded-md bg-neutral-900 border border-neutral-800 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-600 outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors"
              />
            </div>

            {loginError && (
              <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2">
                {loginError}
              </p>
            )}

            <button
              onClick={handleLogin}
              disabled={loggingIn}
              className="w-full rounded-md bg-emerald-500 hover:bg-emerald-400 disabled:bg-neutral-800 disabled:text-neutral-500 text-neutral-950 text-sm font-medium py-2 transition-colors"
            >
              {loggingIn ? "Signing in…" : "Sign in"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col">
      <header className="border-b border-neutral-900 px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 text-base">◆</span>
          <span className="text-sm font-medium text-neutral-200">Agentic Ops</span>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={
              "text-xs px-2 py-1 rounded-full border " +
              (role === "manager"
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-neutral-800 text-neutral-400 border-neutral-700")
            }
          >
            {role}
          </span>
          <span className="text-sm text-neutral-500">{email}</span>
          <button
            onClick={handleLogout}
            className="text-sm text-neutral-500 hover:text-neutral-200 transition-colors"
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-2xl w-full mx-auto px-5 py-6">
        <div className="flex-1 space-y-4 overflow-y-auto">
          {history.length === 0 && (
            <div className="text-center text-neutral-600 text-sm pt-16">
              Ask about a customer, a policy, or an order's refund status.
            </div>
          )}

          {history.map((turn, i) => (
            <div
              key={i}
              className={"flex " + (turn.role === "user" ? "justify-end" : "justify-start")}
            >
              <div
                className={
                  "max-w-[80%] rounded-lg px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap " +
                  (turn.role === "user"
                    ? "bg-emerald-500 text-neutral-950"
                    : "bg-neutral-900 border border-neutral-800 text-neutral-200")
                }
              >
                {turn.content}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="rounded-lg px-3.5 py-2.5 bg-neutral-900 border border-neutral-800 text-neutral-500 text-sm">
                Thinking…
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="mt-4 flex gap-2">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask something…"
            className="flex-1 rounded-md bg-neutral-900 border border-neutral-800 px-3.5 py-2.5 text-sm text-neutral-100 placeholder:text-neutral-600 outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={sending || !message.trim()}
            className="rounded-md bg-emerald-500 hover:bg-emerald-400 disabled:bg-neutral-800 disabled:text-neutral-600 text-neutral-950 text-sm font-medium px-4 transition-colors"
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}