const config = require('../config/config');

const errorMiddleware = (err, req, res, next) => {
  console.error('❌ Erreur:', err.message);
  console.error('Stack:', err.stack);

  // Définition du statut par défaut
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Une erreur interne est survenue';

  // Structure de réponse d'erreur standardisée
  const errorResponse = {
    error: {
      message: message,
      code: err.code || 'INTERNAL_ERROR',
      timestamp: new Date().toISOString(),
      path: req.originalUrl
    }
  };

  // En développement, ajouter la stack trace
  if (config.nodeEnv === 'development' && err.stack) {
    errorResponse.error.stack = err.stack;
  }

  // Gestion des erreurs spécifiques
  if (err.name === 'ValidationError') {
    errorResponse.error.code = 'VALIDATION_ERROR';
    errorResponse.error.details = err.details || {};
  }

  if (err.name === 'AxiosError') {
    errorResponse.error.code = 'EXTERNAL_SERVICE_ERROR';
    errorResponse.error.service = 'ML_API';
  }

  res.status(statusCode).json(errorResponse);
};

module.exports = errorMiddleware;