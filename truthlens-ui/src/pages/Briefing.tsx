import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api, EventDetail } from '../api';
import { formatDistanceToNow } from 'date-fns';

export const Briefing: React.FC = () => {
  const [searchParams] = useSearchParams();
  const eventId = searchParams.get('id');
  
  const [eventData, setEventData] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!eventId) {
        setLoading(false);
        return;
    }
    
    const fetchEvent = async () => {
      try {
        const data = await api.getEventDetail(eventId);
        setEventData(data);
      } catch (err) {
        console.error("Failed to load briefing:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvent();
  }, [eventId]);

  if (loading) return <div className="scrollarea"><div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Compiling intelligence briefing...</div></div>;
  if (!eventId || !eventData) return <div className="scrollarea"><div style={{ padding: '2rem', textAlign: 'center', color: 'var(--status-critical)' }}>Briefing not found or tracking ID missing.</div></div>;

  return (
    <div className="scrollarea">
       {/* Top Identifier */}
      <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
        <span className="badge badge-analysis" style={{ backgroundColor: 'var(--primary-light)', color: 'var(--primary)', border: 'none' }}>
            {eventData.status === 'BREAKING' ? 'CRITICAL EVENT' : 'ACTIVE EVENT'}
        </span>
        <span className="text-small text-tertiary">Updated {formatDistanceToNow(new Date(eventData.last_updated_at), {addSuffix: true})}</span>
      </div>

      <h1 style={{ fontSize: '2.5rem', lineHeight: 1.2, fontWeight: 700, marginBottom: '1.5rem', maxWidth: '800px' }}>
        {eventData.title}
      </h1>
      
      <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '3rem', maxWidth: '800px' }}>
        {eventData.summary || "Summary generation in progress..."}
      </p>

      <div style={{ display: 'flex', gap: '3rem' }}>
          
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              
              {/* Consensus Block */}
              <div className="card flex-col gap-4">
                  <div className="flex justify-between items-center">
                      <h2 style={{ fontSize: '1.25rem' }}>Consensus & Credibility</h2>
                      <span className={eventData.trust_score > 0.8 ? "badge badge-success" : "badge badge-warning"}>
                          {eventData.trust_score > 0.8 ? "HIGH CONFIDENCE" : "MODERATE CONFIDENCE"}
                      </span>
                  </div>
                  
                  <div className="progress-bar-container" style={{ width: '100%', height: '8px', backgroundColor: 'var(--bg-app)', marginTop: '0.5rem' }}>
                      <div className="progress-bar-fill" style={{ width: `${Math.round(eventData.trust_score * 100)}%`, backgroundColor: 'var(--primary)', borderRadius: '9999px 0 0 9999px' }}></div>
                  </div>
                  
                  <div className="flex justify-between text-small" style={{ color: 'var(--text-secondary)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary)'}}></span> {Math.round(eventData.trust_score * 100)}% Verified Facts</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--status-info)'}}></span> Extracted Claims: {eventData.claims?.length || 0}</span>
                  </div>
              </div>

              {/* Timeline Block */}
              {eventData.timeline && eventData.timeline.length > 0 && (
                  <>
                      <h2 style={{ fontSize: '1.25rem', marginTop: '1rem', marginBottom: '0.5rem' }}>Intelligence Timeline</h2>
                      <div style={{ position: 'relative', paddingLeft: '1.5rem', borderLeft: '2px solid var(--border-light)', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                          {eventData.timeline.sort((a,b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 5).map(entry => (
                              <div key={entry.id} style={{ position: 'relative' }}>
                                  <span style={{ position: 'absolute', left: '-1.825rem', top: '0.25rem', display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: entry.significance > 0.8 ? 'var(--primary)' : 'var(--border-medium)', border: '2px solid white'}}></span>
                                  <div className={`text-small ${entry.significance > 0.8 ? 'text-primary' : 'text-tertiary'}`} style={{ fontWeight: 700, marginBottom: '0.25rem' }}>
                                      {new Date(entry.timestamp).toLocaleString()}
                                  </div>
                                  <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>{entry.entry_type} Signal Detected</h3>
                                  <p className="text-secondary text-medium">{entry.description}</p>
                              </div>
                          ))}
                      </div>
                  </>
              )}

              {/* Sources */}
              {eventData.articles && eventData.articles.length > 0 && (
                  <>
                      <h2 style={{ fontSize: '1.25rem', marginTop: '1rem' }}>Key Sources & Reports</h2>
                      <div className="flex-col gap-3">
                          {eventData.articles.slice(0, 5).map(article => (
                              <a href={article.url} target="_blank" rel="noreferrer" key={article.id} style={{ textDecoration: 'none', color: 'inherit' }}>
                                  <div className="card flex items-center gap-4" style={{ backgroundColor: 'var(--bg-app)', border: 'none', padding: '1rem', transition: 'background-color 0.2s', cursor: 'pointer' }}>
                                      <div style={{ width: '40px', height: '40px', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                                          {article.source_name.substring(0,2).toUpperCase() || "SRC"}
                                      </div>
                                      <div style={{ flex: 1 }}>
                                          <div className="flex justify-between items-center" style={{ marginBottom: '0.25rem' }}>
                                              <h4 style={{ fontWeight: 600 }}>{article.source_name || article.source_domain}</h4>
                                              <span className="badge badge-analysis">{article.language.toUpperCase()}</span>
                                          </div>
                                          <p className="text-small text-secondary" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '400px' }}>
                                              {article.title}
                                          </p>
                                      </div>
                                  </div>
                              </a>
                          ))}
                      </div>
                  </>
              )}
          </div>

          {/* Right Sidebar */}
          <div style={{ width: '340px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* Entities */}
              {eventData.primary_entities && eventData.primary_entities.length > 0 && (
                  <div className="card" style={{ backgroundColor: 'var(--bg-app)', border: 'none' }}>
                      <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-tertiary)', letterSpacing: '0.05em', marginBottom: '1rem' }}>Key Entities</h3>
                      <div className="flex flex-wrap gap-2">
                          {eventData.primary_entities.slice(0, 10).map((v, i) => (
                               <span key={i} className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', backgroundColor: 'white' }}>
                                   {v.type === 'GPE' ? '🌍' : v.type === 'ORG' ? '🏢' : v.type === 'PERSON' ? '👤' : '📍'} {v.text}
                               </span>
                          ))}
                      </div>
                  </div>
              )}

              {/* Status Banner */}
              <div className="card flex items-center gap-2" style={{ backgroundColor: 'var(--primary-light)', border: 'none', padding: '1rem' }}>
                  <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary)'}}></span>
                  <span style={{ fontSize: '0.875rem', color: 'var(--primary)', fontWeight: 600 }}>Live Signal Monitoring Active ({eventData.article_count} sources)</span>
              </div>

              <button className="btn btn-primary w-full" style={{ padding: '1rem', fontSize: '1rem' }}>Export Full Analyst Report</button>
          </div>
      </div>
    </div>
  );
};
