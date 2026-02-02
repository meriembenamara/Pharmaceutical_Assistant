const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const config = require('./config/config');
const assistantRoutes = require('./routes/assistant.routes');
const errorMiddleware = require('./middlewares/error.middleware');

const app = express();

// Sécurité
app.use(helmet());

// CORS
app.use(cors({
  origin: config.corsOrigin,
  credentials: true
}));

// Limite de requêtes
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.max,
  message: 'Trop de requêtes, veuillez réessayer plus tard.'
});
app.use('/api/', limiter);

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/assistant', assistantRoutes);

// Route de santé
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    service: 'Pharma Assistant API'
  });
});

// Route 404
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route non trouvée',
    path: req.originalUrl
  });
});

// Middleware d'erreur global
app.use(errorMiddleware);

module.exports = app;