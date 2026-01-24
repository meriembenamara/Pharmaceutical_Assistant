require('dotenv').config();

module.exports = {
  // Configuration serveur
  port: process.env.PORT || 5000,
  env: process.env.NODE_ENV || 'development',
  
  // URLs des services
  aiServiceURL: process.env.AI_SERVICE_URL || 'http://localhost:8000',
  frontendURL: process.env.FRONTEND_URL || 'http://localhost:3000',
  
  // Clés API et sécurité
  aiServiceApiKey: process.env.AI_SERVICE_API_KEY,
  openaiApiKey: process.env.OPENAI_API_KEY,
  
  // Base de données (si utilisée)
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    name: process.env.DB_NAME || 'pharma_assistant',
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD
  },
  
  // Logging
  logLevel: process.env.LOG_LEVEL || 'info'
};