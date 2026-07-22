/**
 * App.jsx
 * --------
 * The root component of our React app.
 * 
 * CONCEPT — React Router:
 *   In a traditional website, clicking a link reloads the whole page.
 *   React Router makes it a "Single Page Application" (SPA) —
 *   only the content area changes, the navbar stays.
 *   This feels instant and smooth.
 * 
 *   Routes map URLs to components:
 *   /          → Home page
 *   /analyze   → Upload & analyze page
 *   /results   → Results page
 *   /history   → Past analyses
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Analyze from './pages/Analyze';
import Results from './pages/Results';
import History from './pages/History';

function App() {
  return (
    <Router>
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/results" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </AnimatePresence>
    </Router>
  );
}

export default App;
