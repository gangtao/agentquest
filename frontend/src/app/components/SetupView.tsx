import { useState } from "react";

export default function SetupView({ onGenerated }: { onGenerated: () => void }) {
    const [seed, setSeed] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!seed.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const res = await fetch("http://127.0.0.1:8000/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ seed }),
            });

            if (!res.ok) {
                throw new Error(await res.text());
            }

            onGenerated();
        } catch (err: any) {
            setError(err.message || "Failed to generate world");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
            <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 p-8 rounded-xl shadow-2xl">
                <div className="mb-8 text-center">
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-orange-400 to-red-600 mb-2">
                        Forge a New World
                    </h2>
                    <p className="text-zinc-400 text-sm">
                        Enter a seed prompt to generate the setting, factions, and quests for your adventure.
                    </p>
                </div>

                <form onSubmit={handleGenerate} className="flex flex-col gap-4">
                    <div>
                        <label htmlFor="seed" className="block text-sm font-medium text-zinc-300 mb-1">
                            World Seed
                        </label>
                        <textarea
                            id="seed"
                            value={seed}
                            onChange={(e) => setSeed(e.target.value)}
                            className="w-full h-32 px-3 py-2 bg-zinc-950 border border-zinc-700 rounded-md text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                            placeholder="e.g. A cyberpunk city floating on an ocean of liquid methane, ruled by rival AI syndicates..."
                            required
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-red-900/30 border border-red-800 rounded-md text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading || !seed.trim()}
                        className="w-full py-3 px-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-bold rounded-md transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(234,88,12,0.3)] hover:shadow-[0_0_25px_rgba(234,88,12,0.5)]"
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Forging World... (This takes a few minutes)</span>
                            </>
                        ) : (
                            "Generate World"
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
