"use client";

import React, { useState } from 'react';

export default function DeepfakeForensics() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [caption, setCaption] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (caption) {
      formData.append('contextual_caption', caption);
    }

    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze/multimodal', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
      } else {
        console.error("Analysis failed:", data);
        alert(data.detail || "Analysis failed due to a server error.");
      }
    } catch (error) {
      console.error("Network error during analysis:", error);
      alert("Network error. Make sure the backend is running.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-md p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-4">
        <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h2 className="text-lg font-semibold text-slate-200">Deepfake & Visual Forensics Engine</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Upload Column */}
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Target Image Evidence</label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-700 border-dashed rounded-md hover:border-slate-500 transition-colors bg-slate-800/50">
              <div className="space-y-1 text-center">
                <svg className="mx-auto h-12 w-12 text-slate-500" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="flex text-sm text-slate-400 justify-center">
                  <label htmlFor="file-upload" className="relative cursor-pointer bg-slate-800 rounded-md font-medium text-cyan-400 hover:text-cyan-300 focus-within:outline-none px-2 py-1">
                    <span>Upload a file</span>
                    <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleFileChange} />
                  </label>
                </div>
                <p className="text-xs text-slate-500">PNG, JPG, GIF up to 10MB</p>
                {selectedFile && <p className="text-sm font-medium text-emerald-400 mt-2 truncate max-w-[250px] mx-auto">{selectedFile.name}</p>}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Contextual Claim / Social Media Caption</label>
            <textarea 
              rows={3} 
              className="w-full bg-slate-800 border border-slate-700 rounded-md p-3 text-sm text-slate-200 placeholder-slate-500 focus:ring-slate-500 focus:border-slate-500"
              placeholder="e.g., 'Look at this recent flood in Paris!'"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
            />
          </div>

          <button 
            type="button"
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            className={`w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-slate-700 hover:bg-slate-600 focus:outline-none transition-colors ${!selectedFile ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isAnalyzing ? (
               <span className="flex items-center gap-2">
                 <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                   <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                   <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                 </svg>
                 Running Fast-ResNet Pipeline...
               </span>
            ) : "Execute Forensics Scan"}
          </button>
        </div>

        {/* Results Column */}
        <div className="bg-slate-950/30 rounded-md border border-slate-800 p-6 flex flex-col h-full">
          {!result && !isAnalyzing && (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-600 space-y-3">
              <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm">Awaiting media input for structural analysis...</p>
            </div>
          )}

          {isAnalyzing && (
             <div className="flex-1 flex flex-col items-center justify-center text-slate-500 space-y-4">
                 <div className="h-1.5 w-48 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-slate-500 w-1/2 animate-[ping_1.5s_ease-in-out_infinite]"></div>
                 </div>
                 <p className="text-xs uppercase tracking-widest animate-pulse text-slate-400">Computing Artifact Signatures...</p>
             </div>
          )}

          {result && result.status === 'success' && (
            <div className="space-y-6 animate-in fade-in duration-500">
               <div>
                 <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-widest mb-1 border-b border-slate-800 pb-2">Forensic Verdict</h3>
                 
                 <div className="mt-4 flex items-center gap-4">
                    <div className={`text-4xl font-light ${result.analysis.is_authentic ? 'text-emerald-400' : 'text-rose-500'}`}>
                       {result.analysis.is_authentic ? 'Authentic' : 'Manipulated'}
                    </div>
                 </div>
               </div>

               <div className="space-y-3">
                 <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-4">Structural Analysis</h3>
                 
                 <div className="bg-slate-800/40 rounded p-3 border border-slate-800 flex justify-between items-center">
                   <span className="text-sm text-slate-300">AI Generation Probability</span>
                   <span className="text-sm font-mono text-slate-100 dark:text-amber-400 ml-2">
                     {(result.analysis.deepfake_analysis.ai_generated_probability * 100).toFixed(1)}%
                   </span>
                 </div>

                 <div className="bg-slate-800/40 rounded p-3 border border-slate-800 flex justify-between items-center">
                   <span className="text-sm text-slate-300">Pixel Manipulation Score</span>
                   <span className="text-sm font-mono text-slate-100 ml-2">
                     {(result.analysis.deepfake_analysis.manipulation_probability * 100).toFixed(1)}%
                   </span>
                 </div>

                 <div className="bg-slate-800/40 rounded p-3 border border-slate-800 flex justify-between items-center">
                   <span className="text-sm text-slate-300">Caption-Image Consistency</span>
                   <span className="text-sm font-mono text-slate-100 ml-2">
                     {result.analysis.consistency_score.toFixed(1)}%
                   </span>
                 </div>
               </div>

               <div>
                 <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-4">VLM Reasoning</h3>
                 <p className="text-sm text-slate-300 mt-2 bg-slate-800/40 p-3 rounded border border-slate-800 italic leading-relaxed">
                   "{result.analysis.explanation}"
                 </p>
               </div>
               
               <p className="text-[10px] text-slate-600 font-mono text-right pt-2">TX_ID: {result.transaction_id}</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
