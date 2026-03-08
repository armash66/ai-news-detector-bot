"""
Claim verification endpoint.

POST /verify-claim - Verify a single factual claim
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import get_analyzer
from backend.utils.logger import get_logger

logger = get_logger("routes.verify")
router = APIRouter()


class VerifyClaimRequest(BaseModel):
    """Request body for claim verification."""
    claim: str = Field(
        ...,
        min_length=10,
        description="Factual claim to verify",
        examples=["NASA confirmed alien life in Arizona desert"],
    )
    explain: bool = Field(
        default=True,
        description="Include explainability analysis",
    )


@router.post("/verify-claim")
async def verify_claim(request: VerifyClaimRequest):
    """Verify a single factual claim.

    Classifies the claim, searches for evidence, and returns
    a credibility assessment with supporting/contradicting sources.
    """
    try:
        analyzer = get_analyzer()
        report = analyzer.verify_claim(
            claim=request.claim,
            explain=request.explain,
        )
        return report.to_dict()
    except Exception as exc:
        logger.error("Claim verification failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Claim verification failed: {str(exc)}",
        )
