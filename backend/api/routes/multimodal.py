from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from backend.multimodal.analyzer import MultimodalAnalyzer, MultimodalVerificationResult
from backend.utils.logger import get_logger

logger = get_logger("multimodal_api")
router = APIRouter()

class MultimodalRequest(BaseModel):
    text: str
    image_url: str

@router.post("/analyze-multimodal", response_model=MultimodalVerificationResult)
async def analyze_multimodal(request: MultimodalRequest):
    """Verifies image consistency against a text claim to detect reused/miscontextualized media."""
    try:
        analyzer = MultimodalAnalyzer()
        result = analyzer.verify_image_text_consistency(request.text, request.image_url)
        if result.error:
            logger.warning(f"Multimodal specific error: {result.error}")
        return result
    except Exception as e:
        logger.error(f"Multimodal pipeline crashed: {e}")
        raise HTTPException(status_code=500, detail="Failed to run multimodal AI")
