const dotenv = require('dotenv');
dotenv.config();

module.exports = {
  port: process.env.PORT || 3001,
  mlApiUrl: process.env.ML_API_URL || 'http://localhost:8000/api',
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/pharma_assistant',
  corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW || '15') * 60 * 1000,
    max: parseInt(process.env.RATE_LIMIT_MAX || '100')
  },
  nodeEnv: process.env.NODE_ENV || 'development'
};