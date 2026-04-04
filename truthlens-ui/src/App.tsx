import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Landing } from './pages/Landing';
import { Feed } from './pages/Feed';
import { Intelligence } from './pages/Intelligence';
import { Alerts } from './pages/Alerts';
import { Analytics } from './pages/Analytics';
import { Briefing } from './pages/Briefing';
import { Analyze } from './pages/Analyze';

export const App: React.FC = () => {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  return (
    <div className="app-container">
      {!isLanding && <Sidebar />}
      <main className="main-content" style={{ overflowY: isLanding ? 'auto' : 'hidden' }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/intelligence" element={<Intelligence />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/briefing" element={<Briefing />} />
          <Route path="/analyze" element={<Analyze />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
