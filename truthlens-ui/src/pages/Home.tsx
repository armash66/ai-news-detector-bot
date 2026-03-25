import React, { useEffect, useState } from 'react';
import { api, EventResponse } from '../api';
import { formatDistanceToNow } from 'date-fns';
import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await api.getEvents(20, 'significance_score');
        setEvents(data);
      } catch (err) {
        console.error("Failed to load events:", err);
      } finally {
        setLoading(false);
      }
    };
    loadEvents();
  }, []);

  return (
    <div className="scrollarea">
      <div className="flex items-center justify-between" style={{ marginBottom: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          Event Feed
          <span className="badge badge-success" style={{ backgroundColor: 'transparent', color: 'var(--primary)', border: '1px solid var(--primary)' }}>
            <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--primary)', marginRight: '6px' }}></span>
            LIVE UPDATES
          </span>
        </h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <input 
              type="text" 
              placeholder="Search events, entities, or regions..." 
              style={{
                padding: '0.5rem 1rem', 
                borderRadius: '8px', 
                border: '1px solid var(--border-light)',
                backgroundColor: 'var(--bg-app)',
                width: '300px',
                fontSize: '0.875rem'
              }}
            />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2" style={{ marginBottom: '2rem' }}>
        <button className="badge" style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--primary)', color: 'white', border: 'none' }}>All Events</button>
        <button className="badge badge-analysis" style={{ padding: '0.5rem 1rem' }}>Geopolitics</button>
        <button className="badge badge-analysis" style={{ padding: '0.5rem 1rem' }}>Tech & Markets</button>
        <button className="badge badge-analysis" style={{ padding: '0.5rem 1rem' }}>Environment</button>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {loading && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Gathering Intelligence...</div>}
            
            {!loading && events.length === 0 && (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No live events detected currently. Check backend ingestion.</div>
            )}

            {!loading && events.map((ev, index) => {
                const isCritical = ev.significance_score > 0.8 || ev.status === 'BREAKING';
                const borderColor = isCritical ? 'var(--status-critical)' : 'var(--primary)';
                const badgeClass = isCritical ? 'badge-breaking' : 'badge-trending';
                const label = isCritical ? 'BREAKING' : 'TRENDING';
                
                return (
                    <div key={ev.id} className="card" style={{ borderLeft: `4px solid ${borderColor}`, position: 'relative' }}>
                        <div className="flex items-center gap-2" style={{ marginBottom: '1rem' }}>
                            <span className={`badge ${badgeClass}`}>{label}</span>
                            <span className="text-small">{formatDistanceToNow(new Date(ev.first_seen_at), {addSuffix: true})}</span>
                            {ev.category !== 'GENERAL' && (
                                <span className="badge badge-analysis" style={{ marginLeft: 'auto' }}>{ev.category}</span>
                            )}
                        </div>
                        
                        <Link to={`/briefing?id=${ev.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                            <h2 style={{ marginBottom: '0.75rem' }}>{ev.title}</h2>
                        </Link>
                        
                        <p style={{ marginBottom: '1.5rem', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {ev.summary || "Incoming intelligence report currently processing. Summary generation pending."}
                        </p>
                        
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-2 text-small">
                                <div className="flex" style={{ marginLeft: '0.5rem' }}>
                                    {/* Mock Avatars */}
                                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--primary)', border: '2px solid white', marginLeft: '-0.5rem' }}></div>
                                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--status-info)', border: '2px solid white', marginLeft: '-0.5rem' }}></div>
                                </div>
                                {ev.article_count} Articles Tracked
                            </div>
                            <div className="flex items-center gap-2 text-small font-bold" style={{ fontWeight: 700, color: 'var(--primary)' }}>
                                CREDIBILITY 
                                <div className="progress-bar-container">
                                    <div className="progress-bar-fill" style={{ width: `${Math.round(ev.trust_score * 100)}%` }}></div>
                                </div>
                                {Math.round(ev.trust_score * 100)}%
                            </div>
                        </div>
                    </div>
                );
            })}
            
            <button className="btn btn-secondary" style={{ alignSelf: 'center', marginTop: '1rem' }}>Load More Intelligence</button>
        </div>

        {/* Right Sidebar */}
        <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div>
                <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-tertiary)', letterSpacing: '0.05em', marginBottom: '1rem' }}>Global Hotspots</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="flex items-center justify-between">
                        <span className="text-medium text-primary">Southeast Asia</span>
                        <span className="badge badge-breaking" style={{ fontSize: '0.6rem' }}>High Activity</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-medium text-primary">Central Europe</span>
                        <span className="badge badge-analysis" style={{ fontSize: '0.6rem', color: 'var(--primary)', borderColor: 'var(--primary-light)' }}>Normal</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-medium text-primary">Middle East</span>
                        <span className="badge badge-warning" style={{ fontSize: '0.6rem' }}>Developing</span>
                    </div>
                </div>
            </div>

            <div className="card" style={{ backgroundColor: 'var(--primary)', color: 'white', border: 'none' }}>
                <h3 style={{ color: 'white', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                     Pro-Tip: Advanced Filtering
                </h3>
                <p style={{ color: 'var(--primary-light)', marginBottom: '1.5rem', fontSize: '0.8rem' }}>
                    Combine "Entity" tags with "Geopolitics" to create custom alerts for specific corporate competitors.
                </p>
                <button className="btn w-full" style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', border: 'none' }}>
                    VIEW TUTORIAL
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};
