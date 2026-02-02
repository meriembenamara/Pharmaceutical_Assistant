const validateRequest = (schema) => {
  return (req, res, next) => {
    const errors = [];
    
    // Valider le body
    if (req.body && schema) {
      for (const [field, rules] of Object.entries(schema)) {
        const value = req.body[field];
        
        // Vérification si requis
        if (rules.required && (value === undefined || value === null || value === '')) {
          errors.push(`Le champ '${field}' est requis`);
          continue;
        }
        
        // Si non requis et absent, continuer
        if (!rules.required && (value === undefined || value === null)) {
          continue;
        }
        
        // Validation du type
        if (rules.type === 'string' && typeof value !== 'string') {
          errors.push(`Le champ '${field}' doit être une chaîne de caractères`);
        }
        
        if (rules.type === 'array' && !Array.isArray(value)) {
          errors.push(`Le champ '${field}' doit être un tableau`);
        }
        
        if (rules.type === 'number' && typeof value !== 'number') {
          errors.push(`Le champ '${field}' doit être un nombre`);
        }
        
        // Validation de longueur (pour les strings)
        if (rules.type === 'string' && typeof value === 'string') {
          if (rules.minLength && value.length < rules.minLength) {
            errors.push(`Le champ '${field}' doit avoir au moins ${rules.minLength} caractères`);
          }
          
          if (rules.maxLength && value.length > rules.maxLength) {
            errors.push(`Le champ '${field}' ne doit pas dépasser ${rules.maxLength} caractères`);
          }
        }
        
        // Validation de taille (pour les arrays)
        if (rules.type === 'array' && Array.isArray(value)) {
          if (rules.minItems && value.length < rules.minItems) {
            errors.push(`Le champ '${field}' doit contenir au moins ${rules.minItems} éléments`);
          }
          
          if (rules.maxItems && value.length > rules.maxItems) {
            errors.push(`Le champ '${field}' ne doit pas contenir plus de ${rules.maxItems} éléments`);
          }
        }
      }
    }
    
    if (errors.length > 0) {
      return res.status(400).json({
        error: 'Validation échouée',
        details: errors,
        code: 'VALIDATION_ERROR'
      });
    }
    
    next();
  };
};

module.exports = validateRequest;