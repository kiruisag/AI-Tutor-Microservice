class AIServiceError(Exception):
    """Base exception for AI microservice errors."""
    pass

class LLMError(AIServiceError):
    """Exception for LLM-related errors."""
    pass

class RAGError(AIServiceError):
    """Exception for Retrieval-Augmented Generation errors."""
    pass

class QuotaExceededError(AIServiceError):
    """Exception for quota limit violations."""
    pass

class ValidationError(AIServiceError):
    """Exception for input validation errors."""
    pass
