"use client";

import React, { useEffect, useState } from 'react';

type Narrative = {
    id: string;
    topic: string;
    volume: number;
    growth: number;
    dominant_sentiment: string;
    sources: string[];
    verification_status: string;
    last_active: string;
};

export default function NarrativeStreams() {
    const [narratives, setNarratives] = useState<Narrative[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNarratives = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/v1/narratives/clusters');
                if (!res.ok) throw new Error("Failed to fetch narrative clusters");
                const data = await res.json();
                setNarratives(data.data || []);
            } catch (e) {
                console.error("Error loading narratives:", e);
            } finally {
                setLoading(false);
            }
        };

        fetchNarratives();
        const interval = setInterval(fetchNarratives, 45000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-md p-6 shadow-sm min-h-[70vh]">
            <div className="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    <h2 className="text-lg font-semibold text-slate-200">Semantic Narrative Clusters</h2>
                </div>
                <div className="text-xs text-slate-500 uppercase tracking-widest font-mono">
                    Last Updated: {new Date().toLocaleTimeString()}
                </div>
            </div>

            {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-4"></div>
                    <p className="text-slate-500 text-sm italic">Clustering global info-streams...</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {narratives.map((narrative, idx) => (
                        <div key={narrative.id || idx} className="bg-slate-950 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-colors group">
                            <div className="flex flex-col md:flex-row justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className={`h-2 w-2 rounded-full ${narrative.verification_status.includes('Manipulated') ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]' :
                                                narrative.verification_status.includes('Bot') ? 'bg-amber-500' : 'bg-emerald-500'
                                            }`}></span>
                                        <h3 className="text-md font-medium text-slate-100 group-hover:text-indigo-300 transition-colors">{narrative.topic}</h3>
                                    </div>
                                    <div className="flex flex-wrap gap-2 mt-3">
                                        {narrative.sources.map(s => (
                                            <span key={s} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 uppercase border border-slate-700">
                                                {s}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center gap-8 px-4 border-l border-slate-800">
                                    <div className="text-center">
                                        <p className="text-[10px] text-slate-500 uppercase mb-1">Volume</p>
                                        <p className="text-lg font-mono text-slate-200">{narrative.volume.toLocaleString()}</p>
                                    </div>
                                    <div className="text-center min-w-[60px]">
                                        <p className="text-[10px] text-slate-500 uppercase mb-1">Growth</p>
                                        <p className={`text-sm font-bold ${narrative.growth > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                            {narrative.growth > 0 ? '+' : ''}{narrative.growth}%
                                        </p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-[10px] text-slate-500 uppercase mb-1">Status</p>
                                        <span className={`text-[10px] font-bold px-2 py-1 rounded border ${narrative.verification_status.includes('Manipulated') ? 'border-rose-900 text-rose-500 bg-rose-500/5' :
                                                narrative.verification_status.includes('Bot') ? 'border-amber-900 text-amber-500 bg-amber-500/5' :
                                                    'border-emerald-900 text-emerald-500 bg-emerald-500/5'
                                            }`}>
                                            {narrative.verification_status.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 pt-4 border-t border-slate-900 flex justify-between items-center">
                                <p className="text-xs text-slate-500">
                                    Dominant Sentiment: <span className="text-slate-300 font-medium">{narrative.dominant_sentiment}</span>
                                </p>
                                <button className="text-[10px] text-indigo-400 font-semibold uppercase tracking-widest hover:text-indigo-300 transition-colors">
                                    View Full Tree →
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
