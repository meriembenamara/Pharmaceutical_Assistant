// app.js : Configuration principale Express
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// Import des routes
const assistantRoutes = require('./routes/assistant.routes');

// Import des middlewares
const errorMiddleware = require('./middlewares/error.middleware');

// Configuration
const app = express();

// Middlewares de sécurité
app.use(helmet()); // Sécurité HTTP headers
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Limiteur de requêtes (anti-DDoS)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // 100 requêtes par IP
});
app.use('/api/', limiter);

// Middlewares de parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes API
app.use('/api/assistant', assistantRoutes);

// Route de santé
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Gestion des erreurs
app.use(errorMiddleware);

module.exports = app;