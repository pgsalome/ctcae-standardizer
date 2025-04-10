"""
API for the CTCAE symptom matcher.
"""
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.symptom_matcher import SymptomMatcher
from src.utils import configure_logging

# Configure logging
configure_logging()

# Initialize FastAPI
app = FastAPI(
    title="CTCAE Symptom Standardizer",
    description="API for standardizing symptoms to CTCAE terminology",
    version="1.0.0"
)

# Initialize symptom matcher
symptom_matcher = SymptomMatcher(
    collection_name="ctcae_terms",
    model_name=os.getenv("SYMPTOM_MATCHER_MODEL", "gpt-3.5-turbo")
)


class SymptomRequest(BaseModel):
    """Request model for symptom matching."""
    symptom: str
    details: Optional[str] = ""


class SymptomResponse(BaseModel):
    """Response model for symptom matching."""
    ctcae_term: str
    grade: str
    grade_description: str
    meddra_soc: str
    confidence: str
    rationale: str
    original_symptom: str
    details: Optional[str] = None


@app.post("/match", response_model=SymptomResponse)
async def match_symptom(request: SymptomRequest) -> Dict[str, Any]:
    """
    Match a symptom to CTCAE terminology.

    Args:
        request: SymptomRequest with symptom and optional details

    Returns:
        Standardized CTCAE term with grade
    """
    try:
        result = symptom_matcher.match_symptom(
            symptom=request.symptom,
            details=request.details
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status response
    """
    return {"status": "ok"}