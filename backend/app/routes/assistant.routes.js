const express = require('express');
const router = express.Router();
const assistantController = require('../controllers/assistant.controller');

// Validation middleware (exemple avec Joi ou express-validator)
const validateRequest = require('../middlewares/validate.middleware');

// Endpoint pour poser une question médicale
router.post('/ask', 
  // validateRequest(questionSchema), // Validation des données
  assistantController.askQuestion
);

// Endpoint pour rechercher un médicament
router.get('/drugs/search', assistantController.searchDrug);

// Endpoint pour obtenir les interactions médicamenteuses
router.post('/drugs/interactions', assistantController.checkInteractions);

// Endpoint pour l'historique des conversations
router.get('/conversations/:userId', assistantController.getConversationHistory);

module.exports = router;