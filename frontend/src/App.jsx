import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Search, 
  Link as LinkIcon, 
  FileText,
  Activity,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Image as ImageIcon,
  BarChart2,
  Rss,
  Globe
} from 'lucide-react';

export default function SaaS_Dashboard() {
  const [activeTab, setActiveTab] = useState('analyze');
  
  return (
    <div className="saas-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="saas-main">
        <header className="saas-topbar">
          <div className="user-profile">
            <span className="status-dot"></span> System Online
          </div>
        </header>

        <div className="saas-content">
          {activeTab === 'analyze' && <AnalyzeView />}
          {activeTab === 'multimodal' && <MultimodalView />}
          {activeTab === 'feed' && <LiveFeedView />}
          {activeTab === 'stats' && <StatsView />}
        </div>
      </main>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────
// SIDEBAR
// ────────────────────────────────────────────────────────────────────────
function Sidebar({ activeTab, setActiveTab }) {
  const menus = [
    { id: 'analyze', icon: <Search size={22} />, label: 'Deep Analysis' },
    { id: 'multimodal', icon: <ImageIcon size={22} />, label: 'Multimodal AI' },
    { id: 'feed', icon: <Rss size={22} />, label: 'Live Intel Feed' },
    { id: 'stats', icon: <BarChart2 size={22} />, label: 'Platform Stats' }
  ];

  return (
    <nav className="saas-sidebar glass fade-in">
      <div className="sidebar-brand">
        <Activity color="var(--accent-cyan)" size={28} />
        <h1 className="logo-display" style={{fontSize: '1.4rem'}}>VeritasAI</h1>
      </div>
      <ul className="sidebar-menu">
        {menus.map(m => (
          <li key={m.id}>
            <button 
              className={activeTab === m.id ? 'active' : ''}
              onClick={() => setActiveTab(m.id)}
            >
              {m.icon} <span>{m.label}</span>
            </button>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">
        <p>Enterprise SaaS Edition</p>
        <p>v2.0 Model Runtime</p>
      </div>
    </nav>
  );
}

// ────────────────────────────────────────────────────────────────────────
// ANALYZE VIEW
// ────────────────────────────────────────────────────────────────────────
function AnalyzeView() {
  const [inputType, setInputType] = useState('text'); // 'text' or 'url'
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);

  const handleAnalyze = async () => {
    if (!inputValue.trim()) return;
    setLoading(true); setError(null); setReport(null);
    try {
      const endpoint = inputType === 'url' ? '/api/v1/analyze-url' : '/api/v1/analyze';
      const payload = inputType === 'url' ? { url: inputValue } : { text: inputValue };
      const response = await axios.post(endpoint, payload);
      setReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (score) => {
    if (score >= 75) return 'high';
    if (score >= 50) return 'mid';
    return 'low';
  };

  const renderHighlightedText = () => {
    if (!report?.explanations?.attention?.token_importances) return null;
    return report.explanations.attention.token_importances.map((item, i) => {
      const word = item.token.replace(/[^a-zA-Z0-9.,!?'-]/g, '');
      if (!word) return <span key={i}> </span>;
      const opacity = item.suspicious ? Math.min(0.2 + (item.score * 5), 0.9) : 0;
      return (
        <span key={i}>
          <span 
            className="word-highlight"
            style={{ 
              backgroundColor: opacity > 0 ? `rgba(239, 68, 68, ${opacity})` : 'transparent',
              color: opacity > 0.5 ? '#fff' : 'inherit'
            }}
          >
            {word}
          </span>{' '}
        </span>
      );
    });
  };

  return (
    <div className="dashboard-grid fade-in">
      <section className="glass input-section">
        <h2 className="section-title">Scan Content / URL</h2>
        
        <div className="input-toggle">
          <button className={inputType === 'text' ? 'active' : ''} onClick={() => setInputType('text')}>
            <FileText size={16} /> Raw Text
          </button>
          <button className={inputType === 'url' ? 'active' : ''} onClick={() => setInputType('url')}>
            <LinkIcon size={16} /> Article URL
          </button>
        </div>

        {inputType === 'text' ? (
          <textarea 
            placeholder="Paste text here... (min 20 chars)"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
        ) : (
          <input 
            type="text" 
            placeholder="https://example.com/article"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
        )}

        <button className="btn-primary" onClick={handleAnalyze} disabled={loading || inputValue.length < 5}>
          {loading ? <Loader2 className="loader" size={24} /> : 'Run Transformer Model Pipeline'}
        </button>
        {error && <div className="error-box"><strong>Error:</strong> {error}</div>}
      </section>

      <section className="results-section">
        {!report && !loading && (
          <div className="glass score-card" style={{ opacity: 0.5 }}>
            <ShieldCheck size={64} color="var(--border-color)" style={{ margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-secondary)' }}>Awaiting content injection.</p>
          </div>
        )}
        {loading && (
           <div className="glass score-card">
             <Loader2 className="loader slide-up" size={48} color="var(--accent-cyan)" style={{ margin: '0 auto 1rem' }} />
             <h3 className="verdict" style={{ color: 'var(--accent-cyan)' }}>Corroborating Evidence...</h3>
           </div>
        )}
        {report && !loading && (
          <>
            <div className="glass score-card slide-up" data-status={getStatusClass(report.credibility.score)}>
              <div className="score-circle">
                <div className="score-value">{Math.round(report.credibility.score)}</div>
                <div className="score-label">Trust Score</div>
              </div>
              
              <h3 className="verdict" style={{ color: `var(--score-${getStatusClass(report.credibility.score)})` }}>
                {report.credibility.verdict}
              </h3>
              
              <ul className="reasons-list">
                {report.credibility.reasons.map((reason, idx) => (
                  <li key={idx}>
                    <CheckCircle2 size={18} /> <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="details-grid slide-up" style={{ animationDelay: '0.1s' }}>
              <div className="glass detail-card">
                <h3>Signal Map</h3>
                <div className="metric-row"><span>NLP Classification</span><span className="metric-value">{report.credibility.component_scores.model_prediction}%</span></div>
                <div className="metric-row"><span>Source Domain</span><span className="metric-value">{report.credibility.component_scores.source_credibility}%</span></div>
                <div className="metric-row"><span>Language Integrity</span><span className="metric-value">{report.credibility.component_scores.language_patterns}%</span></div>
                <div className="metric-row"><span>Evidence Depth</span><span className="metric-value">{report.credibility.component_scores.evidence_support}%</span></div>
              </div>

              <div className="glass detail-card" style={{gridColumn: '1 / -1'}}>
                <h3>AI Explainability Tokens</h3>
                <div className="attention-text">{renderHighlightedText()}</div>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────
// MULTIMODAL VIEW
// ────────────────────────────────────────────────────────────────────────
function MultimodalView() {
  const [text, setText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const runMultimodal = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/analyze-multimodal', { text, image_url: imageUrl });
      setResult(response.data);
    } catch (e) {
      alert("Error running Multimodal AI limit. Check server logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-grid fade-in">
       <div className="glass input-section">
         <h2 className="section-title"><ImageIcon size={20} color="var(--accent-blue)"/> Deep Fake & Context Verifier</h2>
         <p style={{color: 'var(--text-secondary)', marginBottom: '1rem'}}>Cross-verify an image against a claim to detect manipulated or out-of-context media usage.</p>
         
         <label>Associated Claim or Caption (Text)</label>
         <textarea 
            placeholder="e.g. Flood situation in Houston Texas today" style={{minHeight:"100px"}}
            value={text} onChange={(e) => setText(e.target.value)} />
            
         <label>Image Evidence (URL Link)</label>
         <input type="text" placeholder="https://..." value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} />
         
         <button className="btn-primary" onClick={runMultimodal} disabled={loading || !text || !imageUrl}>
          {loading ? "Waking up Vision-Language Model..." : "Run Image-Text Consistency Check"}
         </button>
       </div>
       
       <div className="results-section">
         {imageUrl && <img src={imageUrl} alt="preview" className="glass preview-image" />}
         {result && (
           <div className="glass score-card slide-up" data-status={result.is_consistent ? 'high' : 'low'}>
             <h3 className="verdict" style={{ color: `var(--score-${result.is_consistent ? 'high' : 'low'})` }}>
               {result.is_consistent ? 'Image Context Verified' : 'Image Manipulation / Out Of Context Detected'}
             </h3>
             <p>{result.explanation}</p>
             <p style={{marginTop:'1rem', fontSize:'2rem', fontWeight:'bold'}}>
               {result.consistency_score.toFixed(1)}% Match
             </p>
           </div>
         )}
       </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────
// LIVE FEED VIEW
// ────────────────────────────────────────────────────────────────────────
function LiveFeedView() {
  const [feed, setFeed] = useState([]);
  
  useEffect(() => {
    const fetchFeed = async () => {
      try {
        const res = await axios.get('/api/v1/dashboard/feed');
        setFeed(res.data);
      } catch(e) {}
    };
    fetchFeed();
    const interval = setInterval(fetchFeed, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fade-in glass p-2">
      <h2 className="section-title" style={{padding: '1.5rem'}}><Globe size={20} color="var(--accent-purple)" /> Auto-Monitored Sources Feed</h2>
      <div className="feed-list">
        {feed.length === 0 && <p style={{padding: '1.5rem', color: 'var(--text-secondary)'}}>No background fetches yet. APScheduler might be idling.</p>}
        {feed.map(item => (
          <div key={item.id} className="feed-item slide-up">
            <div className={`status-bar ${item.verdict === 'Likely Credible' ? 'high' : item.verdict.includes('Mixed') ? 'mid' : 'low'}`}></div>
            <div className="feed-content">
              <h4>{item.title}</h4>
              <p className="feed-meta">{new Date(item.scraped_at).toLocaleString()} • {item.source}</p>
              <div className="feed-score">Score: <strong>{item.credibility_score.toFixed(1)}</strong></div>
            </div>
            {item.image_url && <img src={item.image_url} alt="thumbnail" className="feed-thumb" />}
          </div>
        ))}
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────
// STATS VIEW
// ────────────────────────────────────────────────────────────────────────
function StatsView() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get('/api/v1/dashboard/stats').then(r => setStats(r.data)).catch(() => {});
  }, []);

  if (!stats) return <p className="glass p-2">Loading intel footprint...</p>;

  return (
    <div className="fade-in details-grid">
      <div className="glass detail-card" style={{gridColumn: '1/-1', textAlign:'center'}}>
        <h2>Total Monitored Operations</h2>
        <div style={{fontSize: '4rem', fontWeight: '800', background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
          {stats.total_articles_monitored}
        </div>
      </div>
      
      <div className="glass detail-card">
        <ShieldCheck size={40} color="var(--score-high)"/>
        <h3>Credible Intels</h3>
        <p style={{fontSize:'2rem', fontWeight:'bold'}}>{stats.verdict_distribution.credible}</p>
      </div>

      <div className="glass detail-card">
        <ShieldAlert size={40} color="var(--score-low)"/>
        <h3>Disinformation Threats</h3>
        <p style={{fontSize:'2rem', fontWeight:'bold'}}>{stats.verdict_distribution.fake}</p>
      </div>
    </div>
  );
}
