# app/utils/helpers.py
"""
General utility functions for the AI microservice.
"""
from typing import Any, Dict, Optional

# Text truncation utility
def truncate_text(text: str, max_length: int = 2000) -> str:
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# Tenant context helper
def get_tenant_context(tenant_id: str) -> Dict[str, Any]:
    # Placeholder for tenant context retrieval
    return {"tenant_id": tenant_id}

# Error mapping helper
def map_exception_to_error(exc: Exception) -> str:
    return exc.__class__.__name__
