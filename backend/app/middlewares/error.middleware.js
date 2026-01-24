//error.middleware.js : Gestion d'erreurs
/**
 * Middleware global de gestion d'erreurs
 */
function errorMiddleware(err, req, res, next) {
  console.error(`[${new Date().toISOString()}] Erreur:`, {
    message: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    path: req.path,
    method: req.method
  });

  // Erreurs de validation
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Erreur de validation',
      details: err.errors
    });
  }

  // Erreurs JWT/auth
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({
      error: 'Non autorisé',
      code: 'UNAUTHORIZED'
    });
  }

  // Erreur service externe
  if (err.message.includes('Service AI indisponible')) {
    return res.status(503).json({
      error: 'Service d\'IA temporairement indisponible',
      code: 'SERVICE_UNAVAILABLE'
    });
  }

  // Erreur par défaut
  const statusCode = err.statusCode || 500;
  const message = process.env.NODE_ENV === 'production' 
    ? 'Une erreur interne est survenue' 
    : err.message;

  res.status(statusCode).json({
    error: message,
    code: err.code || 'INTERNAL_ERROR',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
}

module.exports = errorMiddleware;