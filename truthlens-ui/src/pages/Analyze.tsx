import React, { useState } from 'react';
import { api, type AnalyzeResult } from '../api';
import { ShieldCheck, FileText, Link as LinkIcon, Loader } from 'lucide-react';

export const Analyze: React.FC = () => {
  const [mode, setMode] = useState<'text' | 'url'>('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === 'text' && !text.trim()) return;
    if (mode === 'url' && !url.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.analyze(
        mode === 'text' ? text : undefined,
        mode === 'url' ? url : undefined,
      );
      if (res.result) {
        setResult(res.result);
      } else {
        setError('Analysis returned no result. Try again.');
      }
    } catch (err: any) {
      console.error('Analysis failed:', err);
      setError(err?.response?.data?.detail || 'Analysis failed. Check if the backend NLP pipeline is operational.');
    } finally {
      setLoading(false);
    }
  };

  const trustPct = result ? Math.round(result.trust_score * 100) : 0;
  const trustColor = trustPct >= 70 ? 'var(--status-success)' : trustPct >= 50 ? 'var(--status-warning)' : 'var(--status-critical)';

  return (
    <div className="scrollarea">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldCheck size={24} color="var(--primary)" /> Article Analyzer
        </h1>
        <p className="text-secondary" style={{ marginTop: '0.5rem' }}>
          Submit article text or a URL to run our NLP credibility pipeline — sentiment analysis, bias detection, entity extraction, and trust scoring.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        {/* Input Panel */}
        <div style={{ flex: 1 }}>
          <form onSubmit={handleAnalyze}>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              {/* Mode Toggle */}
              <div className="flex gap-2" style={{ marginBottom: '1.5rem' }}>
                <button
                  type="button"
                  onClick={() => setMode('text')}
                  className="btn"
                  style={{ backgroundColor: mode === 'text' ? 'var(--primary)' : 'white', color: mode === 'text' ? 'white' : 'var(--text-secondary)', border: '1px solid var(--border-light)', gap: '0.5rem' }}
                >
                  <FileText size={16} /> Paste Text
                </button>
                <button
                  type="button"
                  onClick={() => setMode('url')}
                  className="btn"
                  style={{ backgroundColor: mode === 'url' ? 'var(--primary)' : 'white', color: mode === 'url' ? 'white' : 'var(--text-secondary)', border: '1px solid var(--border-light)', gap: '0.5rem' }}
                >
                  <LinkIcon size={16} /> Enter URL
                </button>
              </div>

              {mode === 'text' ? (
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Article Text</label>
                  <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste the full article text here for credibility analysis..."
                    rows={10}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border-light)',
                      backgroundColor: 'var(--bg-app)',
                      fontSize: '0.875rem',
                      color: 'var(--text-primary)',
                      resize: 'vertical',
                      lineHeight: 1.6,
                      fontFamily: 'inherit',
                    }}
                  />
                  <div className="text-small" style={{ marginTop: '0.5rem', textAlign: 'right' }}>{text.length} characters</div>
                </div>
              ) : (
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Article URL</label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com/news-article"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border-light)',
                      backgroundColor: 'var(--bg-app)',
                      fontSize: '0.875rem',
                      color: 'var(--text-primary)',
                    }}
                  />
                  <p className="text-small" style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>
                    Note: URL scraping may be limited. Pasting text directly gives more accurate results.
                  </p>
                </div>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || (mode === 'text' ? !text.trim() : !url.trim())}
              style={{ padding: '0.875rem 2rem', fontSize: '1rem', width: '100%' }}
            >
              {loading ? (
                <><Loader size={18} style={{ animation: 'spin 1s linear infinite' }} /> Analyzing...</>
              ) : (
                <><ShieldCheck size={18} /> Run Credibility Analysis</>
              )}
            </button>
          </form>

          {error && (
            <div className="card" style={{ borderLeft: '4px solid var(--status-critical)', padding: '1rem 1.5rem', marginTop: '1.5rem' }}>
              <p style={{ color: 'var(--status-critical)', fontWeight: 600, margin: 0 }}>⚠ Analysis Failed</p>
              <p style={{ margin: '0.25rem 0 0' }}>{error}</p>
            </div>
          )}

          {/* Results */}
          {result && (
            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Trust Score Hero */}
              <div className="card" style={{ textAlign: 'center', padding: '2rem', borderTop: `4px solid ${trustColor}` }}>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>Overall Trust Score</div>
                <div style={{ fontSize: '4rem', fontWeight: 700, color: trustColor, lineHeight: 1 }}>{trustPct}%</div>
                <div style={{ marginTop: '0.5rem' }}>
                  <span className={`badge ${trustPct >= 70 ? 'badge-success' : trustPct >= 50 ? 'badge-warning' : 'badge-breaking'}`} style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}>
                    {trustPct >= 70 ? '✅ HIGH CREDIBILITY' : trustPct >= 50 ? '⚠ MODERATE CREDIBILITY' : '❌ LOW CREDIBILITY'}
                  </span>
                </div>
                <div className="progress-bar-container" style={{ width: '100%', height: '8px', marginTop: '1.5rem' }}>
                  <div className="progress-bar-fill" style={{ width: `${trustPct}%`, backgroundColor: trustColor }}></div>
                </div>
              </div>

              {/* Signal Breakdown */}
              {result.breakdown && Object.keys(result.breakdown).length > 0 && (
                <div className="card">
                  <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Signal Breakdown</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                    {Object.entries(result.breakdown).map(([signal, data]: [string, any]) => {
                      const score = typeof data === 'object' ? (data.score ?? data.value ?? null) : null;
                      const pct = score !== null ? Math.round(score * 100) : null;
                      const color = pct !== null ? (pct >= 70 ? 'var(--status-success)' : pct >= 50 ? 'var(--status-warning)' : 'var(--status-critical)') : 'var(--primary)';
                      return (
                        <div key={signal}>
                          <div className="flex justify-between text-small" style={{ marginBottom: '0.375rem' }}>
                            <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{signal.replace(/_/g, ' ')}</span>
                            {pct !== null && <span style={{ color, fontWeight: 700 }}>{pct}%</span>}
                          </div>
                          {pct !== null && (
                            <div className="progress-bar-container" style={{ width: '100%', height: '4px' }}>
                              <div className="progress-bar-fill" style={{ width: `${pct}%`, backgroundColor: color }}></div>
                            </div>
                          )}
                          {typeof data === 'object' && data.reason && (
                            <p className="text-small" style={{ marginTop: '0.25rem', fontStyle: 'italic' }}>{data.reason}</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Sentiment & Bias */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="card" style={{ textAlign: 'center' }}>
                  <div className="text-small" style={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Sentiment</div>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: result.sentiment > 0 ? 'var(--status-success)' : result.sentiment < -0.1 ? 'var(--status-critical)' : 'var(--text-secondary)' }}>
                    {result.sentiment > 0.1 ? '😊' : result.sentiment < -0.1 ? '😠' : '😐'}
                  </div>
                  <div style={{ fontWeight: 700, marginTop: '0.25rem', color: result.sentiment > 0 ? 'var(--status-success)' : result.sentiment < -0.1 ? 'var(--status-critical)' : 'var(--text-secondary)' }}>
                    {result.sentiment > 0.1 ? 'Positive' : result.sentiment < -0.1 ? 'Negative' : 'Neutral'}
                  </div>
                  <div className="text-small">Score: {result.sentiment.toFixed(2)}</div>
                </div>
                <div className="card" style={{ textAlign: 'center' }}>
                  <div className="text-small" style={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Bias</div>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: result.bias > 0.5 ? 'var(--status-critical)' : result.bias > 0.3 ? 'var(--status-warning)' : 'var(--status-success)' }}>
                    {result.bias > 0.5 ? '⚠' : result.bias > 0.3 ? '🟡' : '✅'}
                  </div>
                  <div style={{ fontWeight: 700, marginTop: '0.25rem', color: result.bias > 0.5 ? 'var(--status-critical)' : result.bias > 0.3 ? 'var(--status-warning)' : 'var(--status-success)' }}>
                    {result.bias > 0.5 ? 'High Bias' : result.bias > 0.3 ? 'Some Bias' : 'Low Bias'}
                  </div>
                  <div className="text-small">Score: {result.bias.toFixed(2)}</div>
                </div>
              </div>

              {/* Summary */}
              {result.summary && (
                <div className="card" style={{ backgroundColor: 'var(--primary-light)', border: 'none' }}>
                  <h3 style={{ color: 'var(--primary)', marginBottom: '0.75rem', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>📝 AI-Generated Summary</h3>
                  <p style={{ color: 'var(--primary-hover)', lineHeight: 1.7, margin: 0 }}>{result.summary}</p>
                </div>
              )}

              {/* Entities */}
              {result.entities && result.entities.length > 0 && (
                <div className="card">
                  <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Detected Entities</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {result.entities.map((ent, i) => (
                      <span key={i} className="badge badge-analysis" style={{ padding: '0.375rem 0.75rem', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', border: 'none' }}>
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Info Sidebar */}
        <div style={{ width: '280px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card" style={{ backgroundColor: 'var(--bg-app)', border: 'none', padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>How It Works</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { step: '1', title: 'NLP Pipeline', desc: 'Text is cleaned, tokenized and summarized using our NLP models.' },
                { step: '2', title: 'Bias Detection', desc: 'Linguistic patterns are scanned for loaded language and framing.' },
                { step: '3', title: 'Sentiment Analysis', desc: 'Emotional tone is extracted across positive/negative/neutral axes.' },
                { step: '4', title: 'Trust Scoring', desc: 'A composite credibility score is computed across all signals.' },
              ].map(s => (
                <div key={s.step} style={{ display: 'flex', gap: '0.75rem' }}>
                  <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, flexShrink: 0 }}>{s.step}</div>
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.125rem' }}>{s.title}</div>
                    <div className="text-small">{s.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ backgroundColor: 'var(--primary)', color: 'white', border: 'none', padding: '1.25rem' }}>
            <h3 style={{ color: 'white', marginBottom: '0.5rem', fontSize: '0.875rem' }}>💡 Best Results</h3>
            <p style={{ color: 'var(--primary-light)', fontSize: '0.8rem', margin: 0, lineHeight: 1.6 }}>
              Paste the full article text (300+ words) for the most accurate credibility analysis. Short snippets may give lower accuracy scores.
            </p>
          </div>

          <div className="card" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>Trust Score Guide</h3>
            {[
              { range: '70–100%', label: 'High Credibility', color: 'var(--status-success)' },
              { range: '50–69%', label: 'Moderate', color: 'var(--status-warning)' },
              { range: '30–49%', label: 'Low Credibility', color: 'var(--status-critical)' },
              { range: '0–29%', label: 'Very Low / Misleading', color: '#dc2626' },
            ].map(g => (
              <div key={g.range} className="flex justify-between" style={{ padding: '0.375rem 0', borderBottom: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: g.color }}>{g.range}</span>
                <span className="text-small">{g.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
