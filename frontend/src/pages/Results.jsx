/**
 * pages/Results.jsx
 * -------------------
 * Displays the full skin analysis report.
 * 
 * CONCEPT — sessionStorage:
 *   We store the analysis result in sessionStorage (temporary browser storage).
 *   When user navigates to /results, we read it from there.
 *   sessionStorage is cleared when the browser tab closes.
 *   (localStorage persists forever — we use that for auth tokens)
 * 
 * CONCEPT — Conditional Rendering:
 *   {result.consultation_needed && <Banner />}
 *   The && operator: if left side is true, render right side.
 *   This is how React conditionally shows/hides UI elements.
 */

import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
};

function Results() {
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const stored = sessionStorage.getItem('dermai_result');
    if (stored) {
      setResult(JSON.parse(stored));
    } else {
      navigate('/analyze');
    }
  }, [navigate]);

  if (!result) return null;

  const getScoreClass = (score) => {
    if (score >= 7) return 'score-good';
    if (score >= 4) return 'score-mid';
    return 'score-bad';
  };

  const getSeverityClass = (severity) => {
    if (severity <= 3) return 'low';
    if (severity <= 6) return 'medium';
    return 'high';
  };

  return (
    <div className="results-page">
      <div className="container">
        {/* ── Header with Score ──────────────────────────── */}
        <motion.div className="results-header" {...fadeUp}>
          <div className={`score-circle ${getScoreClass(result.overall_score)}`}>
            <span className="score-number">{result.overall_score}</span>
            <span className="score-label">out of 10</span>
          </div>

          <h1 style={{ marginBottom: '16px' }}>
            Your <span className="gradient-text">Skin Report</span>
          </h1>

          <div className="skin-info-badges">
            <span className="skin-badge">🧬 {result.skin_type} skin</span>
            <span className="skin-badge">📅 Est. skin age: {result.skin_age_estimate}</span>
          </div>

          {result.top_concerns && result.top_concerns.length > 0 && (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Top concerns: {result.top_concerns.join(' · ')}
            </p>
          )}
        </motion.div>

        {/* ── Results Grid ──────────────────────────────── */}
        <div className="results-grid">

          {/* 1. Detected Issues */}
          {result.issues && result.issues.length > 0 && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🔍</span>
                Detected Issues
              </div>
              {result.issues.map((issue, i) => (
                <div key={i} className="issue-item">
                  <div className="issue-icon">{issue.icon || '⚠️'}</div>
                  <div className="issue-info">
                    <div className="issue-name">{issue.name}</div>
                    <div className="issue-desc">{issue.description}</div>
                  </div>
                  <div className="issue-severity">
                    <div className="severity-bar">
                      <div
                        className={`severity-fill ${getSeverityClass(issue.severity)}`}
                        style={{ width: `${issue.severity * 10}%` }}
                      />
                    </div>
                    <span className="severity-text">{issue.severity}/10</span>
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {/* 2. Recommended Ingredients */}
          {result.ingredients && result.ingredients.length > 0 && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🧪</span>
                Recommended Ingredients
              </div>
              {result.ingredients.map((ing, i) => (
                <div key={i} className="ingredient-item">
                  <div className="ingredient-name">{ing.name}</div>
                  <div className="ingredient-benefit">{ing.benefit}</div>
                  <div className="ingredient-meta">
                    <span>💧 {ing.concentration}</span>
                    <span>📝 {ing.how_to_use}</span>
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {/* 3. Morning Routine */}
          {result.morning_routine && result.morning_routine.length > 0 && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🌅</span>
                Morning Routine
              </div>
              {result.morning_routine.map((step, i) => (
                <div key={i} className="routine-step">
                  <div className="routine-step-number">{step.step_number}</div>
                  <div className="routine-step-content">
                    <div className="routine-product-type">{step.product_type}</div>
                    <div className="routine-description">{step.description}</div>
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {/* 4. Night Routine */}
          {result.night_routine && result.night_routine.length > 0 && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🌙</span>
                Night Routine
              </div>
              {result.night_routine.map((step, i) => (
                <div key={i} className="routine-step">
                  <div className="routine-step-number">{step.step_number}</div>
                  <div className="routine-step-content">
                    <div className="routine-product-type">{step.product_type}</div>
                    <div className="routine-description">{step.description}</div>
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {/* 5. Diet Plan */}
          {result.diet_plan && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🥗</span>
                Diet & Nutrition Plan
              </div>

              {result.diet_plan.foods_to_eat && (
                <div className="diet-category">
                  <div className="diet-category-title">✅ Foods to Eat</div>
                  <div className="diet-items">
                    {result.diet_plan.foods_to_eat.map((food, i) => (
                      <span key={i} className="diet-item eat">{food}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.diet_plan.foods_to_avoid && (
                <div className="diet-category">
                  <div className="diet-category-title">❌ Foods to Avoid</div>
                  <div className="diet-items">
                    {result.diet_plan.foods_to_avoid.map((food, i) => (
                      <span key={i} className="diet-item avoid">{food}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.diet_plan.supplements && (
                <div className="diet-category">
                  <div className="diet-category-title">💊 Supplements</div>
                  <div className="diet-items">
                    {result.diet_plan.supplements.map((sup, i) => (
                      <span key={i} className="diet-item supplement">{sup}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.diet_plan.hydration_tip && (
                <div className="diet-tip">
                  💧 {result.diet_plan.hydration_tip}
                </div>
              )}
            </motion.div>
          )}

          {/* 6. Product Recommendations */}
          {result.products && result.products.length > 0 && (
            <motion.div
              className="glass-card result-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <div className="result-section-title">
                <span className="result-section-icon">🛍️</span>
                Recommended Products
              </div>
              {result.products.map((product, i) => (
                <div key={i} className="product-item">
                  <div className="product-info">
                    <div className="product-name">{product.name}</div>
                    <div className="product-brand">{product.brand}</div>
                    <div className="product-reason">{product.why_recommended}</div>
                    <div className="product-price">{product.price_range}</div>
                  </div>
                  <a
                    href={product.buy_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="product-buy-btn"
                  >
                    Buy Now →
                  </a>
                </div>
              ))}
            </motion.div>
          )}
        </div>

        {/* ── Consultation Banner ────────────────────────── */}
        {result.consultation_needed && (
          <motion.div
            className="glass-card consultation-banner"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <h3>👨‍⚕️ Professional Consultation Recommended</h3>
            <p>{result.consultation_reason || 'Based on the analysis, we recommend seeing a dermatologist for personalized treatment.'}</p>
            <a
              href="https://www.practo.com/dermatologist"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-accent"
            >
              Book a Dermatologist →
            </a>
          </motion.div>
        )}

        {/* ── Bottom Actions ─────────────────────────────── */}
        <motion.div
          style={{ textAlign: 'center', marginTop: '48px', display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <Link to="/analyze" className="btn btn-primary">
            🔬 Analyze Again
          </Link>
          <Link to="/history" className="btn btn-secondary">
            📜 View History
          </Link>
        </motion.div>
      </div>
    </div>
  );
}

export default Results;
