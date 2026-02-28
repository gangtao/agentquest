"use client";

import { useState, useEffect } from "react";
import SetupView from "./components/SetupView";
import LobbyView from "./components/LobbyView";
import GameView from "./components/GameView";

export default function Home() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/status");
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error(e);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950 text-white">
        <p className="text-zinc-500 animate-pulse">Connecting to AgentQuest Core...</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950 text-white flex-col gap-4">
        <h1 className="text-2xl font-bold text-red-500">FastAPI Not Running</h1>
        <p className="text-zinc-400">Please start the backend with `uv run uvicorn agentquest.server:app`</p>
        <button onClick={fetchStatus} className="px-4 py-2 bg-zinc-800 rounded hover:bg-zinc-700">Retry</button>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 font-sans">
      <header className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900 sticky top-0 z-10">
        <h1 className="text-xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-600">
          AgentQuest
        </h1>
        <div className="flex gap-4 text-xs font-mono text-zinc-500">
          <span>World: {status.world_generated ? "✅" : "❌"}</span>
          <span>Game: {status.game_in_progress ? "✅" : "❌"}</span>
        </div>
      </header>

      {status.game_in_progress ? (
        <GameView onRefresh={fetchStatus} />
      ) : status.world_generated ? (
        <LobbyView onStart={fetchStatus} />
      ) : (
        <SetupView onGenerated={fetchStatus} />
      )}
    </main>
  );
}
