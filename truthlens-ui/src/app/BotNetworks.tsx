"use client";

import React, { useEffect, useState, useRef, useCallback } from 'react';
import dynamic from 'next/dynamic';

// Force Graph requires browser 'window' to render canvas
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

type GraphData = {
    nodes: { id: string; group: string; radius: number; color: string }[];
    links: { source: string; target: string; value: number }[];
};

export default function BotNetworks() {
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height: 500 });

    useEffect(() => {
        // Make graph responsive
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };

        window.addEventListener('resize', updateDimensions);
        updateDimensions();

        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    useEffect(() => {
        const fetchGraph = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/v1/campaigns/detected');
                if (!res.ok) throw new Error("Failed to fetch campaign graph");
                const data = await res.json();

                // Setup initial graph data
                if (data.status === 'success') {
                    setGraphData(data.graph_data);
                    setMetrics(data.metrics);
                }
            } catch (e) {
                console.error("Error loading graph:", e);
            } finally {
                setLoading(false);
            }
        };

        fetchGraph();
    }, []);

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-md p-6 shadow-sm min-h-[70vh] flex flex-col">
            <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <h2 className="text-lg font-semibold text-slate-200">Bot Network Operations Command</h2>
                </div>

                {metrics && (
                    <div className="flex gap-4">
                        <div className="bg-slate-800 px-3 py-1.5 rounded-md flex items-center gap-2">
                            <span className="text-xs text-slate-400 uppercase">Nodes</span>
                            <span className="text-sm font-mono text-slate-200">{metrics.total_nodes}</span>
                        </div>
                        <div className="bg-slate-800 px-3 py-1.5 rounded-md flex items-center gap-2">
                            <span className="text-xs text-slate-400 uppercase">Edges</span>
                            <span className="text-sm font-mono text-slate-200">{metrics.total_edges}</span>
                        </div>
                        <div className="bg-rose-950/30 border border-rose-900 px-3 py-1.5 rounded-md flex items-center gap-2">
                            <span className="text-xs text-rose-500 uppercase">Threat</span>
                            <span className="text-sm font-bold text-rose-400 uppercase">{metrics.threat_level}</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="flex-1 border border-slate-800 bg-slate-950 rounded-md relative overflow-hidden" ref={containerRef}>
                {loading ? (
                    <div className="absolute inset-0 flex flex-col justify-center items-center">
                        <svg className="animate-spin h-8 w-8 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p className="text-slate-500 text-sm animate-pulse uppercase tracking-widest">Querying Neo4j Graph DB...</p>
                    </div>
                ) : graphData ? (
                    <ForceGraph2D
                        width={dimensions.width}
                        height={dimensions.height}
                        graphData={graphData}
                        nodeLabel="group"
                        nodeColor="color"
                        nodeRelSize={1}
                        nodeVal="radius"
                        linkColor={() => "rgba(71, 85, 105, 0.4)"}
                        linkWidth={1}
                        d3AlphaDecay={0.02}
                        d3VelocityDecay={0.3}
                        cooldownTicks={100}
                        backgroundColor="#020617" // tailwind slate-950
                    />
                ) : (
                    <div className="absolute inset-0 flex justify-center items-center">
                        <p className="text-slate-500">Failed to load network topology.</p>
                    </div>
                )}

                {/* Legend Overlay */}
                <div className="absolute bottom-4 left-4 bg-slate-900/80 border border-slate-800 rounded-md p-3 backdrop-blur-sm pointer-events-none">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2 border-b border-slate-700 pb-1">Topology Legend</h4>
                    <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                            <span className="text-xs text-slate-300">Command Center</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-orange-400"></span>
                            <span className="text-xs text-slate-300">Sub-Controller</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-3 h-3 rounded-full bg-sky-400"></span>
                            <span className="text-xs text-slate-300">Amplifier Bot</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
