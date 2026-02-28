import { useState, useEffect } from "react";

export default function LobbyView({ onStart }: { onStart: () => void }) {
    const [worldState, setWorldState] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchWorld = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/state");
                const data = await res.json();
                setWorldState(data.world_state);
            } catch (e) {
                console.error("Failed to fetch world state", e);
            }
        };
        fetchWorld();
    }, []);

    const handleStart = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch("http://127.0.0.1:8000/api/play/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resume: true }),
            });

            if (!res.ok) {
                throw new Error(await res.text());
            }

            onStart();
        } catch (err: any) {
            setError(err.message || "Failed to start game");
            setLoading(false);
        }
    };

    if (!worldState) {
        return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading world data...</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-lg">
                    <h2 className="text-2xl font-bold text-orange-400 mb-2">Setting</h2>
                    <p className="text-zinc-300 leading-relaxed mb-4">{worldState.setting}</p>

                    <h3 className="text-xl font-bold text-orange-400/80 mb-2 mt-6">Lore</h3>
                    <p className="text-zinc-400 italic leading-relaxed">{worldState.lore}</p>
                </div>

                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-lg">
                    <h3 className="text-xl font-bold text-red-500 mb-4 flex items-center gap-2">
                        <span>The Main Quest</span>
                    </h3>
                    <div className="bg-black/30 p-4 rounded-lg border border-red-900/30">
                        <h4 className="text-lg font-bold text-zinc-100">{worldState.main_quest?.title}</h4>
                        <p className="text-zinc-400 mt-2">{worldState.main_quest?.description}</p>
                    </div>
                </div>
            </div>

            <div className="space-y-6">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-lg sticky top-24">
                    <h3 className="text-xl font-bold text-zinc-100 mb-4 border-b border-zinc-800 pb-2">Ready to Play?</h3>
                    <p className="text-zinc-400 text-sm mb-6">
                        The world is prepared. The players configuration from <code className="text-orange-400 bg-orange-400/10 px-1 rounded">examples/players.yaml</code> will be used.
                    </p>

                    {error && (
                        <div className="p-3 mb-4 bg-red-900/30 border border-red-800 rounded-md text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        onClick={handleStart}
                        disabled={loading}
                        className="w-full py-4 bg-gradient-to-r from-red-600 to-red-800 hover:from-red-500 hover:to-red-700 text-white font-bold text-lg rounded-md transition-all disabled:opacity-50 shadow-[0_0_20px_rgba(220,38,38,0.4)] hover:shadow-[0_0_30px_rgba(220,38,38,0.6)]"
                    >
                        {loading ? "Initializing Crew..." : "Begin the Campaign"}
                    </button>
                </div>

                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-lg">
                    <h3 className="text-sm font-bold text-zinc-500 uppercase tracking-wider mb-3">Factions</h3>
                    <ul className="space-y-2">
                        {worldState.factions?.map((faction: string, i: number) => (
                            <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                <span className="text-orange-500 mt-0.5">•</span>
                                <span>{faction}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}
