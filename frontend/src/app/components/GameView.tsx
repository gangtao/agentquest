import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

export default function GameView({ onRefresh }: { onRefresh: () => void }) {
    const [gameState, setGameState] = useState<any>(null);
    const [worldState, setWorldState] = useState<any>(null);
    const [transcript, setTranscript] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const transcriptEndRef = useRef<HTMLDivElement>(null);

    const fetchState = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/api/state");
            const data = await res.json();
            setGameState(data.game_state);
            setWorldState(data.world_state);
            setTranscript(data.transcript || "");
        } catch (e) {
            console.error("Failed to fetch game state", e);
        }
    };

    useEffect(() => {
        fetchState();
    }, []);

    useEffect(() => {
        // Scroll transcript to bottom on update
        transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [transcript]);

    const handleNextRound = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch("http://127.0.0.1:8000/api/play/step", {
                method: "POST",
            });

            if (!res.ok) {
                throw new Error(await res.text());
            }

            if (!res.body) throw new Error("No readable stream");

            const reader = res.body.getReader();
            const decoder = new TextDecoder();

            // Add a small spacer if we already have transcript content
            if (transcript.trim().length > 0) {
                setTranscript(prev => prev + "\n\n---\n\n");
            }

            let done = false;
            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                // Round complete
                            } else if (data.startsWith('[STATE] ')) {
                                const stateJson = JSON.parse(data.slice(8));
                                setGameState(stateJson.game_state);
                                if (!stateJson.game_continues) {
                                    alert("Game Over!");
                                    onRefresh();
                                }
                            } else if (data.startsWith('[ERROR] ')) {
                                setError(data.slice(8));
                            } else {
                                // Restore newlines
                                const textChunk = data.replace(/\\n/g, '\n');
                                setTranscript((prev) => prev + textChunk);
                            }
                        }
                    }
                }
            }
        } catch (err: any) {
            setError(err.message || "Failed to step game");
        } finally {
            setLoading(false);
        }
    };

    if (!gameState || !worldState) {
        return <div className="p-8 text-center text-zinc-500 animate-pulse">Loading campaign data...</div>;
    }

    const currentLocation = worldState.locations?.find((loc: any) => loc.name === gameState.current_location);

    return (
        <div className="h-[calc(100vh-60px)] flex flex-col md:flex-row overflow-hidden bg-zinc-950">

            {/* Left Panel - Context & Environment */}
            <div className="w-full md:w-1/4 min-w-[300px] border-r border-zinc-800 bg-zinc-900/50 flex flex-col overflow-y-auto">
                <div className="p-4 border-b border-zinc-800">
                    <h2 className="text-xs uppercase font-bold tracking-wider text-zinc-500 mb-1">Current Location</h2>
                    <h3 className="text-xl font-bold text-orange-400">{gameState.current_location}</h3>
                    {currentLocation && (
                        <p className="text-sm text-zinc-400 mt-2 line-clamp-4">{currentLocation.description}</p>
                    )}
                </div>

                <div className="p-4 border-b border-zinc-800">
                    <h2 className="text-xs uppercase font-bold tracking-wider text-zinc-500 mb-3">Quest Progress</h2>
                    <div className="space-y-3">
                        <div className="text-sm">
                            <div className="text-zinc-300 font-medium mb-1 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                                Main Quest
                            </div>
                            <div className="text-zinc-500 pl-4">{worldState.main_quest?.title}</div>
                        </div>
                    </div>
                </div>

                <div className="p-4 flex-1">
                    <h2 className="text-xs uppercase font-bold tracking-wider text-zinc-500 mb-3">Round Information</h2>
                    <div className="text-4xl font-black text-zinc-800">
                        {gameState.round_number}
                    </div>
                </div>
            </div>

            {/* Center Panel - Transcript */}
            <div className="flex-1 flex flex-col min-w-[400px] relative">
                <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
                    {transcript ? (
                        <div className="max-w-3xl mx-auto space-y-4 text-zinc-300 leading-relaxed">
                            <ReactMarkdown>{transcript}</ReactMarkdown>
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center text-zinc-600 italic">
                            The story has not yet begun...
                        </div>
                    )}
                    <div ref={transcriptEndRef} />
                </div>

                {/* Action Bar */}
                <div className="bg-zinc-900/80 backdrop-blur border-t border-zinc-800 p-4">
                    <div className="max-w-3xl mx-auto flex items-center gap-4">
                        {error && <div className="text-red-400 text-sm flex-1">{error}</div>}

                        <button
                            onClick={handleNextRound}
                            disabled={loading}
                            className="ml-auto px-8 py-3 bg-white text-black hover:bg-zinc-200 font-bold rounded-full transition-all disabled:opacity-50 flex items-center gap-2 shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:shadow-[0_0_20px_rgba(255,255,255,0.2)]"
                        >
                            {loading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                    <span>Agents Thinking...</span>
                                </>
                            ) : (
                                "Advance to Next Round ➔"
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Right Panel - Characters */}
            <div className="w-full md:w-1/4 min-w-[300px] border-l border-zinc-800 bg-zinc-900/50 overflow-y-auto">
                <div className="p-4 sticky top-0 bg-zinc-900/80 backdrop-blur border-b border-zinc-800 z-10">
                    <h2 className="text-xs uppercase font-bold tracking-wider text-zinc-500">The Party</h2>
                </div>

                <div className="p-4 space-y-4">
                    {gameState.characters?.map((char: any, i: number) => (
                        <div key={i} className="bg-black/40 border border-zinc-800 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-zinc-100">{char.name}</h3>
                                <div className="text-xs px-2 py-1 rounded bg-zinc-800 text-zinc-300">
                                    HP: {char.hp}/{char.max_hp}
                                </div>
                            </div>

                            {/* HP Bar */}
                            <div className="w-full h-1.5 bg-zinc-800 rounded-full mb-4 overflow-hidden">
                                <div
                                    className={`h-full ${char.hp / char.max_hp > 0.5 ? 'bg-green-500' : char.hp / char.max_hp > 0.2 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                    style={{ width: `${Math.max(0, Math.min(100, (char.hp / char.max_hp) * 100))}%` }}
                                />
                            </div>

                            {char.inventory?.length > 0 && (
                                <div>
                                    <h4 className="text-[10px] uppercase text-zinc-500 mb-1">Inventory</h4>
                                    <ul className="text-xs text-zinc-400 space-y-1">
                                        {char.inventory.map((item: string, j: number) => (
                                            <li key={j} className="truncate">• {item}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
