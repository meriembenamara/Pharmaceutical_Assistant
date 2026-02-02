const express = require('express');
const router = express.Router();
const assistantController = require('../controllers/assistant.controller');
const validateRequest = require('../utils/validation');

// Schémas de validation
const drugQuerySchema = {
  drugName: { type: 'string', required: true, maxLength: 100 },
  lang: { type: 'string', optional: true, default: 'fr' }
};

const interactionSchema = {
  drugs: { 
    type: 'array', 
    required: true, 
    minItems: 1,
    maxItems: 10,
    items: { type: 'string', maxLength: 100 }
  },
  lang: { type: 'string', optional: true, default: 'fr' }
};

// Routes
router.post('/drug-info', validateRequest(drugQuerySchema), assistantController.getDrugInfo);
router.post('/check-interactions', validateRequest(interactionSchema), assistantController.checkInteractions);
router.post('/ask-question', assistantController.askQuestion);
router.get('/search-drugs', assistantController.searchDrugs);

module.exports = router;