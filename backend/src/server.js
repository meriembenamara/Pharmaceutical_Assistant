const app = require('./app');
const config = require('./config/config');
const mongoose = require('mongoose');

// Connexion MongoDB (optionnel)
const connectDB = async () => {
  try {
    if (config.mongodbUri) {
      await mongoose.connect(config.mongodbUri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      });
      console.log('MongoDB connecté');
    }
  } catch (error) {
    console.error(' Erreur connexion MongoDB:', error.message);
    // L'application peut fonctionner sans MongoDB pour l'instant
  }
};

const startServer = () => {
  const server = app.listen(config.port, () => {
    console.log(` Serveur backend lancé sur http://localhost:${config.port}`);
    console.log(` ML Service: ${config.mlApiUrl}`);
    console.log(` Environnement: ${config.nodeEnv}`);
  });

  // Gestion propre de l'arrêt
  const shutdown = () => {
    console.log('\n Arrêt du serveur...');
    server.close(() => {
      mongoose.connection.close(false, () => {
        console.log(' Serveur arrêté proprement');
        process.exit(0);
      });
    });
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);

  return server;
};

// Démarrage
(async () => {
  await connectDB();
  startServer();
})();