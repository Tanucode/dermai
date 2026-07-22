/**
 * pages/Home.jsx
 * ----------------
 * The landing page — the first thing users see.
 * 
 * CONCEPT — Framer Motion:
 *   Framer Motion adds smooth animations to React components.
 *   motion.div = a div that can animate.
 *   initial = starting state (invisible, moved down)
 *   animate = final state (visible, normal position)
 *   transition = how long and what easing
 */

import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

// Animation variants — reusable animation presets
const fadeUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: 'easeOut' }
};

const staggerContainer = {
  animate: { transition: { staggerChildren: 0.1 } }
};

function Home() {
  const features = [
    {
      icon: '🔬',
      title: 'AI Skin Detection',
      description: 'Our AI detects dark circles, acne, dark spots, oiliness, wrinkles, and 10+ skin conditions from a single photo.'
    },
    {
      icon: '🧪',
      title: 'Ingredient Science',
      description: 'Get recommended active ingredients like Niacinamide, Retinol, Vitamin C — with exact concentrations and usage.'
    },
    {
      icon: '📋',
      title: 'Custom Routines',
      description: 'Personalized morning & night skincare routines tailored to your specific skin type and concerns.'
    },
    {
      icon: '🥗',
      title: 'Diet & Nutrition',
      description: 'Foods that heal your skin, supplements to take, and foods to avoid — backed by dermatology research.'
    },
    {
      icon: '🛍️',
      title: 'Product Recommendations',
      description: 'Curated product picks with direct buy links to Amazon and Nykaa, matched to your skin needs.'
    },
    {
      icon: '👨‍⚕️',
      title: 'Consultation Guidance',
      description: 'Smart detection of conditions that need professional attention, with booking links to dermatologists.'
    }
  ];

  const steps = [
    { number: '01', title: 'Upload Photo', description: 'Take a selfie or upload a clear face photo' },
    { number: '02', title: 'AI Analyzes', description: 'Gemini Vision AI detects all skin issues' },
    { number: '03', title: 'Get Report', description: 'Detailed report with severity scores' },
    { number: '04', title: 'Follow Plan', description: 'Personalized routine, diet & products' }
  ];

  return (
    <>
      {/* ── Hero Section ──────────────────────────────────── */}
      <section className="hero">
        <div className="hero-particles">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${10 + Math.random() * 10}s`
              }}
            />
          ))}
        </div>

        <motion.div
          className="hero-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div className="hero-badge" {...fadeUp}>
            <span className="hero-badge-dot" />
            Powered by Google Gemini AI
          </motion.div>

          <motion.h1 {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.1 }}>
            Your Skin, <span className="gradient-text">Analyzed by AI</span>
          </motion.h1>

          <motion.p
            className="hero-subtitle"
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.2 }}
          >
            Upload a photo and get an instant AI-powered skin analysis with personalized
            skincare routines, ingredient recommendations, diet plans, and product suggestions.
          </motion.p>

          <motion.div
            className="hero-buttons"
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.3 }}
          >
            <Link to="/analyze" className="btn btn-primary">
              🔬 Analyze My Skin
            </Link>
            <a href="#features" className="btn btn-secondary">
              Learn More ↓
            </a>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Features Section ──────────────────────────────── */}
      <section className="features" id="features">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2>Everything Your Skin <span className="gradient-text">Needs</span></h2>
            <p>Comprehensive skin analysis powered by multimodal AI and dermatology knowledge</p>
          </motion.div>

          <motion.div
            className="features-grid"
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="glass-card feature-card"
                variants={fadeUp}
              >
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────── */}
      <section className="how-it-works">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2>How It <span className="gradient-text">Works</span></h2>
            <p>From photo to personalized skincare plan in under 60 seconds</p>
          </motion.div>

          <motion.div
            className="steps-container"
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
          >
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className="glass-card step-card"
                variants={fadeUp}
              >
                <div className="step-number">{step.number}</div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── CTA Section ───────────────────────────────────── */}
      <section style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 style={{ marginBottom: '16px' }}>
              Ready to Discover Your <span className="gradient-text">Skin Story</span>?
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', fontSize: '1.05rem' }}>
              It takes less than 60 seconds. No signup required.
            </p>
            <Link to="/analyze" className="btn btn-accent" style={{ fontSize: '1.05rem', padding: '16px 40px' }}>
              🧴 Start Free Analysis
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────── */}
      <footer className="footer">
        <div className="container">
          <p>© 2024 DermAI — Built with React, FastAPI, Gemini AI & RAG</p>
          <p style={{ marginTop: '8px', fontSize: '0.75rem' }}>
            Disclaimer: This is an AI-based tool and not a substitute for professional dermatological advice.
          </p>
        </div>
      </footer>
    </>
  );
}

export default Home;
