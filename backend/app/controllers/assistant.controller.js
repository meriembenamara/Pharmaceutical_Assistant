//assistant.controller.js : Logique métier
const llmService = require('../services/llm.service');
const { validationResult } = require('express-validator');

class AssistantController {
  /**
   * Traite une question médicale de l'utilisateur
   * @route POST /api/assistant/ask
   */
  async askQuestion(req, res, next) {
    try {
      const { question, context = {}, userId } = req.body;
      
      // Validation basique
      if (!question || question.trim().length === 0) {
        return res.status(400).json({
          error: 'Question requise',
          code: 'VALIDATION_ERROR'
        });
      }

      // Appel au service LLM via le microservice AI
      const response = await llmService.processMedicalQuery({
        question: question.trim(),
        context,
        userId: userId || 'anonymous'
      });

      // Enregistrer l'interaction en base de données (à implémenter)
      // await this.saveInteraction(userId, question, response);

      res.json({
        success: true,
        data: response,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      next(error); // Passe à l'error middleware
    }
  }

  /**
   * Recherche un médicament dans la base de données
   * @route GET /api/assistant/drugs/search
   */
  async searchDrug(req, res, next) {
    try {
      const { query, limit = 10 } = req.query;
      
      // Appel au service AI pour la recherche sémantique
      const results = await llmService.searchDrugs(query, parseInt(limit));
      
      res.json({
        success: true,
        count: results.length,
        drugs: results
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Vérifie les interactions entre médicaments
   * @route POST /api/assistant/drugs/interactions
   */
  async checkInteractions(req, res, next) {
    try {
      const { drugs, patientInfo } = req.body;
      
      if (!drugs || !Array.isArray(drugs) || drugs.length < 2) {
        return res.status(400).json({
          error: 'Au moins deux médicaments requis',
          code: 'INVALID_INPUT'
        });
      }

      const interactions = await llmService.checkDrugInteractions(drugs, patientInfo);
      
      res.json({
        success: true,
        interactions,
        severity: this.calculateOverallSeverity(interactions)
      });
    } catch (error) {
      next(error);
    }
  }

  calculateOverallSeverity(interactions) {
    // Logique de calcul de sévérité
    const severities = interactions.map(i => i.severity);
    if (severities.includes('high')) return 'high';
    if (severities.includes('medium')) return 'medium';
    return 'low';
  }
}

module.exports = new AssistantController();