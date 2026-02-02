const llmService = require('../services/llm.service');

class AssistantController {
  async getDrugInfo(req, res, next) {
    try {
      const { drugName, lang = 'fr' } = req.body;
      
      if (!drugName || drugName.trim().length === 0) {
        return res.status(400).json({
          error: 'Le nom du médicament est requis',
          code: 'INVALID_DRUG_NAME'
        });
      }

      // Appel au service LLM via FastAPI
      const drugInfo = await llmService.getDrugInfo(drugName, lang);
      
      res.json({
        success: true,
        data: {
          drugName,
          information: drugInfo,
          timestamp: new Date().toISOString(),
          source: 'DailyMed FDA'
        }
      });
    } catch (error) {
      next(error);
    }
  }

  async checkInteractions(req, res, next) {
    try {
      const { drugs, lang = 'fr' } = req.body;
      
      if (!Array.isArray(drugs) || drugs.length < 1) {
        return res.status(400).json({
          error: 'Une liste de médicaments est requise',
          code: 'INVALID_DRUG_LIST'
        });
      }

      // Nettoyer les noms de médicaments
      const cleanedDrugs = drugs
        .map(drug => drug.trim())
        .filter(drug => drug.length > 0);

      if (cleanedDrugs.length < 1) {
        return res.status(400).json({
          error: 'Aucun médicament valide fourni',
          code: 'NO_VALID_DRUGS'
        });
      }

      // Appel au service d'interactions
      const interactions = await llmService.checkDrugInteractions(cleanedDrugs, lang);
      
      res.json({
        success: true,
        data: {
          drugs: cleanedDrugs,
          interactions,
          timestamp: new Date().toISOString(),
          severity: interactions.severity || 'unknown'
        }
      });
    } catch (error) {
      next(error);
    }
  }

  async askQuestion(req, res, next) {
    try {
      const { question, context = {}, lang = 'fr' } = req.body;
      
      if (!question || question.trim().length === 0) {
        return res.status(400).json({
          error: 'La question est requise',
          code: 'EMPTY_QUESTION'
        });
      }

      // Limiter la longueur de la question
      if (question.length > 1000) {
        return res.status(400).json({
          error: 'La question est trop longue (max 1000 caractères)',
          code: 'QUESTION_TOO_LONG'
        });
      }

      const answer = await llmService.askQuestion(question, context, lang);
      
      res.json({
        success: true,
        data: {
          question: question.trim(),
          answer,
          timestamp: new Date().toISOString(),
          contextUsed: Object.keys(context).length > 0
        }
      });
    } catch (error) {
      next(error);
    }
  }

  async searchDrugs(req, res, next) {
    try {
      const { query, limit = 10 } = req.query;
      
      if (!query || query.trim().length < 2) {
        return res.status(400).json({
          error: 'Requête de recherche trop courte (min 2 caractères)',
          code: 'QUERY_TOO_SHORT'
        });
      }

      const results = await llmService.searchDrugs(query, parseInt(limit));
      
      res.json({
        success: true,
        data: {
          query,
          results,
          count: results.length,
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new AssistantController();