"use client";

import React, { useEffect, useState } from 'react';
import DeepfakeForensics from './DeepfakeForensics';

type IntelIntel = {
  id: string;
  source: string;
  content_preview: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  timestamp: string;
  suspicion_score: number;
};

type TabType = 'heatmap' | 'forensics';

export default function DashboardClient() {
  const [intelFeed, setIntelFeed] = useState<IntelIntel[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('heatmap');

  useEffect(() => {
    const fetchIntel = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/feed/live');
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        setIntelFeed(data.data || []);
      } catch (error) {
        console.error("Failed to fetch TruthLens feed:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchIntel();
    const interval = setInterval(fetchIntel, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Top Navigation Bar */}
      <nav className="border-b border-slate-800 bg-slate-900 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center">
                <svg className="w-4 h-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <span className="text-xl font-semibold tracking-tight text-slate-100">TruthLens</span>
            </div>
            <div className="flex space-x-4">
              <button 
                onClick={() => setActiveTab('heatmap')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${activeTab === 'heatmap' ? 'bg-slate-800 text-slate-200' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Global Heatmap
              </button>
              <span className="px-3 py-1 rounded-md text-sm font-medium text-slate-400 cursor-not-allowed transition-colors">Narrative Streams</span>
              <span className="px-3 py-1 rounded-md text-sm font-medium text-slate-400 cursor-not-allowed transition-colors">Bot Networks</span>
              <button 
                onClick={() => setActiveTab('forensics')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${activeTab === 'forensics' ? 'bg-slate-800 text-slate-200' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Deepfake Forensics
              </button>
            </div>
            <div className="flex items-center gap-2">
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              <span className="text-xs text-slate-400 font-mono">SYSTEM ONLINE</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Dashboard Layout */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'heatmap' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Column - Live Feed */}
            <div className="col-span-1 border border-slate-800 bg-slate-900 rounded-md p-5 max-h-[80vh] overflow-y-auto">
               <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-4 flex items-center gap-2 sticky top-0 bg-slate-900 py-2 z-10 border-b border-slate-800">
                  <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  Live Threat Intelligence
               </h2>
               <div className="space-y-4">
                  {loading ? (
                    <p className="text-sm text-slate-500">Connecting to global OSINT streams...</p>
                  ) : intelFeed.length === 0 ? (
                    <p className="text-sm text-slate-500">No active threats detected in current polling window.</p>
                  ) : (
                    intelFeed.map((item) => (
                      <div key={item.id} className={`border-l-2 pl-4 py-2 cursor-pointer group hover:bg-slate-800/50 ${item.severity === 'Critical' ? 'border-amber-600' : 'border-slate-700'}`}>
                        <div className="flex justify-between items-start mb-1">
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-sm uppercase bg-slate-800 ${item.severity === 'Critical' ? 'text-amber-500' : 'text-slate-400'}`}>
                            {item.severity} (Score: {item.suspicion_score.toFixed(1)})
                          </span>
                          <span className="text-xs text-slate-500 font-mono">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-300 font-medium line-clamp-2">{item.content_preview}</p>
                        <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">Source: {item.source}</p>
                      </div>
                    ))
                  )}
               </div>
            </div>

            {/* Center/Right - Interactive Data vis */}
            <div className="col-span-1 lg:col-span-2 space-y-6">
              
              {/* KPI Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="border border-slate-800 bg-slate-900 rounded-md p-5">
                  <p className="text-xs text-slate-400 uppercase tracking-wide">Claims Analyzed (24H)</p>
                  <h3 className="text-2xl font-medium text-slate-100 mt-1">124,592</h3>
                  <span className="text-xs text-slate-400 mt-2 block">+12% vs prior</span>
                </div>
                <div className="border border-slate-800 bg-slate-900 rounded-md p-5">
                  <p className="text-xs text-slate-400 uppercase tracking-wide">Active Propaganda Nets</p>
                  <h3 className="text-2xl font-medium text-slate-100 mt-1">14</h3>
                  <span className="text-xs text-slate-400 mt-2 block">Tracked globally</span>
                </div>
                <div className="border border-slate-800 bg-slate-900 rounded-md p-5">
                  <p className="text-xs text-slate-400 uppercase tracking-wide">AI Generated Media</p>
                  <h3 className="text-2xl font-medium text-slate-100 mt-1">4.2%</h3>
                  <span className="text-xs text-slate-400 mt-2 block">+0.5% vs prior</span>
                </div>
              </div>

              {/* Main Visualizer Area */}
              <div className="border border-slate-800 bg-slate-900 rounded-md h-96 flex flex-col items-center justify-center">
                <svg className="w-12 h-12 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-base font-medium text-slate-300">Global Narrative Topology</h3>
                <p className="text-sm text-slate-500 mt-1">Awaiting WebGL Vector Rendering Engine Connect...</p>
                
                <button className="mt-6 px-4 py-2 bg-slate-800 border border-slate-700 text-slate-300 rounded text-sm hover:bg-slate-700 transition-colors">
                  Initialize Graph View
                </button>
              </div>
              
            </div>
          </div>
        ) : (
          <DeepfakeForensics />
        )}
      </main>
    </div>
  );
}
