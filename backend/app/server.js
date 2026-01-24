//server.js : Lancement du serveur
const app = require('./app');
const config = require('./config/config');

const PORT = config.port || 5000;

// Démarrer le serveur
const server = app.listen(PORT, () => {
  console.log(`✅ Serveur backend démarré sur le port ${PORT}`);
  console.log(`📡 Environnement: ${config.env}`);
  console.log(`🔗 URL: http://localhost:${PORT}`);
});

// Gestion propre de l'arrêt
process.on('SIGTERM', () => {
  console.log('SIGTERM reçu, arrêt du serveur...');
  server.close(() => {
    console.log('Serveur arrêté');
    process.exit(0);
  });
});