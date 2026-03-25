import React, { useEffect, useState } from 'react';
import { Settings, SlidersHorizontal, Activity } from 'lucide-react';
import { api, AlertResponse } from '../api';
import { formatDistanceToNow } from 'date-fns';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await api.getAlerts(20);
        setAlerts(data);
      } catch (err) {
        console.error("Failed to load alerts:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="scrollarea">
       {/* Top Bar for Alerts */}
      <div className="flex-col" style={{ marginBottom: '2rem' }}>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
            Intelligence Unit &rsaquo; <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Priority Alerts</span>
        </div>
        <div className="flex items-center justify-between">
            <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                Intelligence Alerts
            </h1>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div className="flex card" style={{ padding: '0.25rem', paddingRight: '0.25rem', gap: '0.25rem', borderRadius: '8px' }}>
                    <button style={{ padding: '0.5rem 1rem', background: 'var(--bg-app)', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.875rem' }}>Active</button>
                    <button style={{ padding: '0.5rem 1rem', background: 'transparent', color: 'var(--text-secondary)', border: 'none', borderRadius: '6px', fontWeight: 500, fontSize: '0.875rem' }}>Archived</button>
                </div>
                <button className="btn btn-secondary"><SlidersHorizontal size={16}/> Filter</button>
            </div>
        </div>
        <p className="text-secondary text-small" style={{ marginTop: '0.25rem' }}>Real-time monitoring of global events, market shifts, and emerging risks curated for your portfolio.</p>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
          {/* Main Alerts List */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
             
             {loading && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Scanning alert streams...</div>}
             
             {!loading && alerts.length === 0 && (
                 <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No priority alerts currently active. Thresholds nominal.</div>
             )}

             {!loading && alerts.map(alert => {
                 const isCritical = alert.severity === 'CRITICAL';
                 const isWarning = alert.severity === 'WARNING';
                 let borderColor = 'var(--primary)';
                 let badgeClass = 'badge-analysis';
                 
                 if (isCritical) {
                     borderColor = 'var(--status-critical)';
                     badgeClass = 'badge-breaking';
                 } else if (isWarning) {
                     borderColor = 'var(--status-warning)';
                     badgeClass = 'badge-warning';
                 }

                 return (
                     <div key={alert.id} className="card" style={{ borderLeft: `4px solid ${borderColor}` }}>
                         <div className="flex items-center justify-between" style={{ marginBottom: '1rem' }}>
                             <div className="flex items-center gap-2">
                                <span className={`badge ${badgeClass}`}>! {alert.severity}</span>
                                <span className="text-small">{formatDistanceToNow(new Date(alert.triggered_at), {addSuffix: true})}</span>
                             </div>
                             <Settings size={16} color="var(--text-tertiary)"/>
                         </div>
                         
                         <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>{alert.title}</h3>
                         <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>{alert.description || "Systemic threshold breached automatically. Details pending."}</p>
                         
                         <div className="flex items-center gap-2 text-small">
                             <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--text-secondary)' }}></div>
                             <span style={{ fontWeight: 600 }}>{alert.alert_type} Monitoring System</span>
                         </div>
                     </div>
                 );
             })}

             <button className="btn btn-secondary" style={{ alignSelf: 'center', marginTop: '1rem' }}>Load Previous Alerts</button>
          </div>

          {/* Right Sidebar widgets */}
          <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* Active Pulse */}
              <div className="card" style={{ backgroundColor: 'var(--bg-app)', border: 'none', padding: '1.5rem' }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
                      <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary)'}}></span>
                          Active Pulse
                      </h3>
                      <span className="text-small" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>REAL-TIME</span>
                  </div>
                  
                  <div className="flex-col gap-4">
                      <div style={{ borderLeft: '2px solid var(--primary)', paddingLeft: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>Tokyo Stock Exchange</div>
                          <div className="text-small text-secondary">Abnormal trading volume detected in tech sector.</div>
                      </div>
                      <div style={{ borderLeft: '2px solid var(--status-critical)', paddingLeft: '1rem' }}>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>Suez Canal Transit</div>
                          <div className="text-small text-secondary">Weather advisory issued for upcoming 24h window.</div>
                      </div>
                  </div>
              </div>

              {/* Risk Exposure */}
              <div className="card" style={{ padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>Risk Exposure</h3>
                  <div style={{ height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-light)', borderRadius: '12px', marginBottom: '1.5rem' }}>
                       {/* Mock Chart Area */}
                       <div style={{ textAlign: 'center' }}>
                           <div style={{ fontSize: '2rem', fontWeight: 700 }}>7.4</div>
                           <div className="text-small text-tertiary">INDEX SCORE</div>
                       </div>
                  </div>

                  <div className="flex-col gap-3">
                      <div>
                          <div className="flex justify-between text-small" style={{ marginBottom: '0.25rem' }}>
                              <span>Logistics</span>
                              <span style={{ color: 'var(--status-critical)' }}>High</span>
                          </div>
                          <div className="progress-bar-container" style={{ width: '100%', height: '4px' }}>
                              <div className="progress-bar-fill" style={{ width: '85%', backgroundColor: 'var(--status-critical)' }}></div>
                          </div>
                      </div>
                      <div>
                          <div className="flex justify-between text-small" style={{ marginBottom: '0.25rem' }}>
                              <span>Regulation</span>
                              <span style={{ color: 'var(--primary)' }}>Moderate</span>
                          </div>
                          <div className="progress-bar-container" style={{ width: '100%', height: '4px' }}>
                              <div className="progress-bar-fill" style={{ width: '45%', backgroundColor: 'var(--primary)' }}></div>
                          </div>
                      </div>
                  </div>
              </div>

               {/* Monitoring Channels */}
               <div className="card" style={{ padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Monitoring Channels</h3>
                  <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                      <span className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>🌍 Geopolitics</span>
                      <span className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>🏛 Finance</span>
                      <span className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', backgroundColor: 'var(--primary-light)', color: 'var(--primary)' }}>💻 Technology</span>
                      <span className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>🌱 Sustainability</span>
                      <span className="badge badge-analysis" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', borderStyle: 'dashed' }}>+ Add Channel</span>
                  </div>
              </div>

          </div>
      </div>
    </div>
  );
};
