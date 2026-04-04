import React, { useState } from 'react';
import { Search, AlertTriangle, Filter, X } from 'lucide-react';
import { api, type EventResponse } from '../api';
import { formatDistanceToNow } from 'date-fns';
import { Link } from 'react-router-dom';

const SEARCH_TYPES = [
  { label: 'Keyword', value: 'keyword' },
  { label: 'Semantic', value: 'semantic' },
  { label: 'Hybrid', value: 'hybrid' },
];

const CATEGORIES = ['', 'GEOPOLITICS', 'TECHNOLOGY', 'FINANCE', 'ENVIRONMENT', 'HEALTH', 'GENERAL'];

export const Intelligence: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<EventResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchType, setSearchType] = useState('keyword');
  const [minTrust, setMinTrust] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortOrder, setSortOrder] = useState<'significance' | 'trust' | 'recent'>('significance');

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);
    setError(null);
    try {
      const data = await api.search(
        query,
        searchType,
        selectedCategory || undefined,
        minTrust > 0 ? minTrust / 100 : undefined,
      );
      setResults(data);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError('Search query failed. Ensure the backend is running.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setHasSearched(false);
    setError(null);
  };

  const sortedResults = [...results].sort((a, b) => {
    if (sortOrder === 'significance') return b.significance_score - a.significance_score;
    if (sortOrder === 'trust') return b.trust_score - a.trust_score;
    return new Date(b.last_updated_at).getTime() - new Date(a.last_updated_at).getTime();
  });

  return (
    <div className="scrollarea">
      {/* Top Bar */}
      <div className="flex items-center justify-between" style={{ marginBottom: '2rem' }}>
        <h1>Intelligence Search</h1>
        <form onSubmit={handleSearch} style={{ position: 'relative', display: 'flex', gap: '0.5rem' }}>
          <div style={{ position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)', pointerEvents: 'none' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search global news events, entities, or topics..."
              style={{
                padding: '0.625rem 2.5rem 0.625rem 2.5rem',
                borderRadius: '8px',
                border: '1px solid var(--border-light)',
                backgroundColor: 'var(--bg-surface)',
                boxShadow: 'var(--shadow-sm)',
                width: '480px',
                fontSize: '0.875rem',
                color: 'var(--text-primary)',
              }}
            />
            {query && (
              <button
                type="button"
                onClick={clearSearch}
                style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)', padding: 0 }}
              >
                <X size={16} />
              </button>
            )}
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? '...' : 'Search'}
          </button>
        </form>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        {/* Left Filter Sidebar */}
        <div style={{ width: '260px', display: 'flex', flexDirection: 'column', gap: '1.75rem', flexShrink: 0 }}>

          <div>
            <h3 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-tertiary)', letterSpacing: '0.05em', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Filter size={14} /> Intelligence Filters
            </h3>

            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>Search Type</label>
            <div style={{ display: 'flex', gap: '0.375rem', marginBottom: '1.5rem' }}>
              {SEARCH_TYPES.map(t => (
                <button
                  key={t.value}
                  onClick={() => setSearchType(t.value)}
                  style={{
                    padding: '0.375rem 0.75rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border-light)',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    backgroundColor: searchType === t.value ? 'var(--primary)' : 'white',
                    color: searchType === t.value ? 'white' : 'var(--text-secondary)',
                    transition: 'all 0.15s',
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>Event Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid var(--border-light)', backgroundColor: 'var(--bg-app)', marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}
            >
              <option value="">All Categories</option>
              {CATEGORIES.filter(c => c).map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 600 }}>Credibility Floor</label>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--primary)' }}>{minTrust}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={minTrust}
              onChange={(e) => setMinTrust(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--primary)', marginBottom: '0.5rem' }}
            />
            <p className="text-small" style={{ fontStyle: 'italic', marginBottom: '2rem' }}>
              Filters out events below this credibility threshold.
            </p>
          </div>

          {/* Smart Alerts callout */}
          <div className="card" style={{ backgroundColor: 'var(--primary-light)', border: 'none', padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.875rem', color: 'var(--primary)', marginBottom: '0.5rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <AlertTriangle size={16} /> Smart Alerts
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--primary-hover)', marginBottom: '1rem' }}>
              Save this search to receive real-time notifications when new events match these criteria.
            </p>
            <Link to="/alerts" style={{ textDecoration: 'none' }}>
              <button style={{ background: 'none', border: 'none', color: 'var(--primary)', fontWeight: 600, fontSize: '0.75rem', cursor: 'pointer' }}>
                View Active Alerts →
              </button>
            </Link>
          </div>
        </div>

        {/* Search Results */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="flex justify-between items-center" style={{ marginBottom: '0.25rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
              {hasSearched ? `Results for "${query}"` : 'Search Results'}
            </h2>
            {hasSearched && sortedResults.length > 0 && (
              <div className="flex gap-2 items-center text-small">
                Sort by:
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as any)}
                  style={{ border: 'none', backgroundColor: 'transparent', fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)', cursor: 'pointer' }}
                >
                  <option value="significance">Significance</option>
                  <option value="recent">Most Recent</option>
                  <option value="trust">Credibility</option>
                </select>
              </div>
            )}
          </div>

          <p className="text-secondary text-small" style={{ marginBottom: '0.5rem' }}>
            {hasSearched
              ? error
                ? error
                : `Found ${sortedResults.length} intelligence event${sortedResults.length !== 1 ? 's' : ''} matching your query.`
              : 'Enter a search query above. Use keyword search for exact matches or semantic for conceptual search.'}
          </p>

          {loading && (
            <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
              Querying intelligence database...
            </div>
          )}

          {!loading && !hasSearched && (
            <div className="card" style={{ backgroundColor: 'var(--bg-app)', border: '2px dashed var(--border-light)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', textAlign: 'center' }}>
              <Search size={40} color="var(--border-medium)" style={{ marginBottom: '1rem' }} />
              <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Awaiting Query</h3>
              <p style={{ maxWidth: '400px' }}>Search the global intelligence database for events, entities, organizations, and geopolitical developments.</p>
            </div>
          )}

          {!loading && hasSearched && sortedResults.length === 0 && !error && (
            <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📭</div>
              No events matched your search. Try adjusting filters or search type.
            </div>
          )}

          {/* Result Cards */}
          {!loading && sortedResults.map(ev => {
            const credibility = Math.round(ev.trust_score * 100);
            return (
              <div key={ev.id} className="card" style={{ padding: '1.25rem', transition: 'transform 0.15s' }}
                onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)'; }}
                onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'; }}
              >
                <div style={{ display: 'flex', gap: '1rem' }}>
                  {/* Category Badge Block */}
                  <div style={{ width: '60px', height: '60px', backgroundColor: 'var(--primary-light)', borderRadius: '10px', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)', fontSize: '0.65rem', fontWeight: 700, textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.03em', padding: '0.25rem' }}>
                    {ev.category || 'GEN'}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="flex items-center gap-2" style={{ marginBottom: '0.5rem' }}>
                      <span className={credibility >= 70 ? 'badge badge-success' : 'badge badge-warning'}>
                        {credibility >= 70 ? 'HIGH CREDIBILITY' : 'MODERATE CREDIBILITY'}
                      </span>
                      <span className="text-small">{formatDistanceToNow(new Date(ev.first_seen_at), { addSuffix: true })}</span>
                      <span className="badge badge-analysis" style={{ marginLeft: 'auto' }}>{ev.status}</span>
                    </div>

                    <Link to={`/briefing?id=${ev.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <h3 style={{ marginBottom: '0.5rem', fontSize: '1.0625rem', lineHeight: 1.3 }}>{ev.title}</h3>
                    </Link>

                    <p className="text-small text-secondary" style={{ overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', marginBottom: '0.75rem' }}>
                      {ev.summary || 'Summary pending generation.'}
                    </p>

                    <div className="flex items-center gap-4 text-small">
                      <span>{ev.article_count} articles · {ev.source_count} sources</span>
                      <div className="flex items-center gap-1" style={{ color: credibility >= 70 ? 'var(--status-success)' : 'var(--status-warning)', fontWeight: 700 }}>
                        <div className="progress-bar-container" style={{ width: '60px' }}>
                          <div className="progress-bar-fill" style={{ width: `${credibility}%`, backgroundColor: credibility >= 70 ? 'var(--status-success)' : 'var(--status-warning)' }}></div>
                        </div>
                        {credibility}%
                      </div>
                      <Link to={`/briefing?id=${ev.id}`} style={{ textDecoration: 'none', marginLeft: 'auto' }}>
                        <button className="btn btn-secondary" style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}>Read Briefing →</button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
