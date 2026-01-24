//llm.service.js : Service d'appel AI
const axios = require('axios');
const config = require('../config/config');

class LLMService {
  constructor() {
    this.aiServiceBaseURL = config.aiServiceURL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.aiServiceBaseURL,
      timeout: 30000, // 30 secondes timeout pour les requêtes LLM
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': config.aiServiceApiKey // Authentification entre services
      }
    });
  }

  /**
   * Traite une requête médicale via le service AI
   */
  async processMedicalQuery({ question, context, userId }) {
    try {
      const response = await this.client.post('/api/llm/ask', {
        query: question,
        context: {
          ...context,
          userId,
          timestamp: new Date().toISOString(),
          language: 'fr' // Support multilingue
        }
      });

      return {
        answer: response.data.answer,
        sources: response.data.sources || [],
        confidence: response.data.confidence,
        suggestions: response.data.suggestions || []
      };
    } catch (error) {
      console.error('Erreur service AI:', error.message);
      throw new Error(`Service AI indisponible: ${error.message}`);
    }
  }

  /**
   * Recherche sémantique de médicaments
   */
  async searchDrugs(query, limit = 10) {
    try {
      const response = await this.client.get('/api/drugs/search', {
        params: { q: query, limit }
      });
      return response.data.results;
    } catch (error) {
      console.error('Erreur recherche médicaments:', error.message);
      return []; // Retourner tableau vide plutôt que d'échouer
    }
  }

  /**
   * Vérifie les interactions médicamenteuses
   */
  async checkDrugInteractions(drugs, patientInfo = {}) {
    try {
      const response = await this.client.post('/api/drugs/interactions', {
        drugs,
        patient_info: patientInfo
      });
      return response.data.interactions;
    } catch (error) {
      console.error('Erreur vérification interactions:', error.message);
      throw error;
    }
  }
}

module.exports = new LLMService();