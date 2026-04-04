import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const MOCK_LOGS = [
  "[SYS] Initializing TruthLens Core...",
  "[DAT] Connecting to global stream (748 sources active)",
  "[VRF] Verifying cross-reference node 192.168.x...",
  "[ANL] Processing semantic anomalies...",
  "[WRN] Detected synthetic signature in current stream",
  "[SYS] Threat score elevated. Recalibrating node trust...",
  "[OK]  Credibility baseline established.",
];

export const Landing: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  
  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < MOCK_LOGS.length) {
        setLogs(prev => [...prev, MOCK_LOGS[currentIndex]]);
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="landing-container">
      {/* Background with the generated image and an overlay pattern */}
      <div className="bg-texture"></div>
      
      <div className="landing-content">
        <header className="landing-header">
          <div className="logo-brutalist">TRUTHLENS_</div>
          <nav className="header-nav">
            <Link to="/feed" className="btn-brutal btn-outline">ACCESS TERMINAL</Link>
          </nav>
        </header>

        <main className="hero-section">
          <div className="hero-grid">
            {/* Left Col: Messaging */}
            <div className="hero-text">
              <h1 className="headline">SEE THROUGH<br/>THE NOISE.</h1>
              <div className="problem-statement box-brutal">
                <span className="label-stark">STATUS: CRITICAL</span>
                <p>The internet is deeply poisoned by bot farms, synthetic media, and low-fidelity narratives.</p>
              </div>
              
              <div className="solution-statement">
                <p>TruthLens cross-checks live events against raw global data to calculate definitive credibility scores in real-time. Verifiable intelligence, no generated fluff.</p>
              </div>
              
              <Link to="/feed" className="btn-brutal btn-primary" style={{ marginTop: '2rem' }}>
                INITIALIZE SENSOR ARRAY <span className="arrow">→</span>
              </Link>
            </div>

            {/* Right Col: Unique Interactive Element (Data Terminal) */}
            <div className="hero-visual">
              <div className="terminal box-brutal">
                <div className="terminal-header">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="terminal-title">TL_CORE_PROCESS</span>
                </div>
                <div className="terminal-body" style={{fontFamily: 'monospace', fontSize: '0.875rem', lineHeight: 1.6, color: '#10b981'}}>
                  {logs.map((log, i) => (
                    <div key={i} className="log-line">{log}</div>
                  ))}
                  <div className="cursor-blink">_</div>
                </div>
              </div>
            </div>
          </div>
          
          <section className="features-grid">
             <div className="feature-block box-brutal">
               <h3 className="feature-title">// REAL-TIME INGESTION</h3>
               <p>Scraping over 500+ unverified streams simultaneously.</p>
             </div>
             <div className="feature-block box-brutal">
               <h3 className="feature-title">// CROSS-VALIDATION</h3>
               <p>Semantic analysis filters out known synthetic fingerprints.</p>
             </div>
             <div className="feature-block box-brutal">
               <h3 className="feature-title">// IMMUTABLE SCORING</h3>
               <p>A rigid logic engine calculates risk. No AI hallucination.</p>
             </div>
          </section>
        </main>
        
        <footer className="landing-footer">
           <div className="footer-content">
             <span>TRUTHLENS SYSTEM / BUILD v2.0.4</span>
             <span>INTELLIGENCE VERIFIED</span>
           </div>
        </footer>
      </div>
    </div>
  );
};
