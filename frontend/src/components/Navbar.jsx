/**
 * components/Navbar.jsx
 * ----------------------
 * The navigation bar — always visible at the top.
 * 
 * CONCEPT — NavLink:
 *   NavLink is like <a> but for React Router.
 *   It adds an 'active' class to the current page's link.
 */

import { NavLink, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

function Navbar() {
  return (
    <motion.nav
      className="navbar"
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="navbar-content">
        <Link to="/" className="navbar-logo">
          <div className="navbar-logo-icon">🧬</div>
          DermAI
        </Link>

        <ul className="navbar-links">
          <li>
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
              Home
            </NavLink>
          </li>
          <li>
            <NavLink to="/analyze" className={({ isActive }) => isActive ? 'active' : ''}>
              Analyze
            </NavLink>
          </li>
          <li>
            <NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>
              History
            </NavLink>
          </li>
          <li>
            <Link to="/analyze" className="btn btn-primary" style={{ padding: '10px 24px', fontSize: '0.85rem' }}>
              Start Scan
            </Link>
          </li>
        </ul>
      </div>
    </motion.nav>
  );
}

export default Navbar;
