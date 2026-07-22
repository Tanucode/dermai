/**
 * pages/History.jsx
 * -------------------
 * Shows past skin analyses.
 * 
 * CONCEPT — useEffect:
 *   useEffect runs code AFTER the component renders.
 *   The empty dependency array [] means "run only once on mount".
 *   We use it to fetch data from the API when the page loads.
 * 
 *   useEffect(() => { fetchData() }, [])
 *                                     ↑ empty = run once
 *   useEffect(() => { ... }, [count])
 *                              ↑ run when 'count' changes
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getHistory, getHistoryItem } from '../services/api';

function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getHistory(20);
      setAnalyses(data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Could not load history. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const viewAnalysis = async (analysisId) => {
    try {
      const result = await getHistoryItem(analysisId);
      sessionStorage.setItem('dermai_result', JSON.stringify(result));
      navigate('/results');
    } catch (err) {
      console.error('Failed to load analysis:', err);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 7) return 'var(--success)';
    if (score >= 4) return 'var(--warning)';
    return 'var(--accent)';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown date';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="history-page">
      <div className="container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1>Analysis <span className="gradient-text">History</span></h1>
          <p>Review your past skin analyses and track your progress</p>
        </motion.div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div className="analyzing-spinner" style={{ margin: '0 auto 16px' }} />
            <p style={{ color: 'var(--text-secondary)' }}>Loading history...</p>
          </div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              padding: '14px 20px',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--accent-light)',
              fontSize: '0.9rem',
              textAlign: 'center',
              maxWidth: '600px',
              margin: '0 auto'
            }}
          >
            ⚠️ {error}
          </motion.div>
        )}

        {!loading && !error && analyses.length === 0 && (
          <motion.div
            className="empty-state"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="empty-state-icon">🔬</div>
            <h3>No analyses yet</h3>
            <p>Start your first skin analysis to see results here</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/analyze')}
            >
              🧴 Analyze My Skin
            </button>
          </motion.div>
        )}

        {!loading && analyses.length > 0 && (
          <div className="history-list">
            {analyses.map((item, index) => (
              <motion.div
                key={item.analysis_id}
                className="glass-card history-item"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => viewAnalysis(item.analysis_id)}
              >
                <div className="history-item-left">
                  <div
                    className="history-score"
                    style={{ borderColor: getScoreColor(item.overall_score), color: getScoreColor(item.overall_score) }}
                  >
                    {item.overall_score}
                  </div>
                  <div className="history-info">
                    <h3>{item.skin_type ? `${item.skin_type.charAt(0).toUpperCase() + item.skin_type.slice(1)} Skin` : 'Analysis'}</h3>
                    <p className="history-concerns">{item.top_concerns || 'No concerns detected'}</p>
                  </div>
                </div>
                <span className="history-date">
                  {formatDate(item.created_at)}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default History;
