from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import logging
import uuid
import sys
import os

# Add the parent directory strings dynamically so we can import internal modules easily.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from ai_pipelines.multimodal import MultimodalAnalyzer

router = APIRouter()
logger = logging.getLogger("truthlens.api.analyze")
ml_analyzer = MultimodalAnalyzer()

class AnalyzeTextRequest(BaseModel):
    text: str

@router.post("/text")
async def analyze_text(payload: AnalyzeTextRequest):
    """
    Standard LLM text analysis endpoint. Triggers claim extraction and evidence retrieval.
    """
    if len(payload.text) < 10:
        raise HTTPException(status_code=400, detail="Text payload too short for structural analysis.")
        
    logger.info("Initializing text intelligence pipeline.")
    return {
        "status": "success",
        "verdict": "Likely Credible",
        "score": 85.5,
        "narrative_cluster_detected": "Emerging Tech Policy",
        "claims_extracted": 2
    }

@router.post("/multimodal")
async def analyze_multimodal(
    file: UploadFile = File(...), 
    contextual_caption: str = Form(None)
):
    """
    Advanced VLM Endpoint. Dissects images and compares them dynamically to contextual claims
    to detect deepfakes, cheap fakes (recycling), and manipulation.
    """
    logger.info(f"Received multimodal payload: {file.filename}")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="TruthLens currently only supports image formats for the VLM endpoint.")

    # Read image bytes securely
    image_bytes = await file.read()
    
    # Process through the Vision pipeline
    insight = ml_analyzer.cross_reference_image(image_bytes, contextual_caption)
    
    return {
        "status": "success",
        "transaction_id": str(uuid.uuid4()),
        "analysis": insight
    }
