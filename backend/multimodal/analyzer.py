import io
import requests
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from pydantic import BaseModel
from typing import Optional

from backend.utils.logger import get_logger

logger = get_logger("multimodal")

class MultimodalVerificationResult(BaseModel):
    is_consistent: bool
    consistency_score: float
    explanation: str
    error: Optional[str] = None

class MultimodalAnalyzer:
    """Uses Vision-Language models (CLIP) to verify if an image matches its textual claim."""
    _instance = None
    _model = None
    _processor = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_model(self):
        if self._model is None:
            logger.info("Loading CLIP model for multimodal verification... (this may take a minute on first run)")
            try:
                # Using a smaller, standard clip model
                model_name = "openai/clip-vit-base-patch32"
                self._model = CLIPModel.from_pretrained(model_name)
                self._processor = CLIPProcessor.from_pretrained(model_name)
                logger.info("CLIP Multimodal analyzer loaded.")
            except Exception as e:
                logger.error(f"Failed to load CLIP. Multimodal won't work: {e}")
                self._model = "failed"
                
    def verify_image_text_consistency(self, text: str, image_url: str) -> MultimodalVerificationResult:
        """Downloads an image and verifies if it actually matches the text caption/claim."""
        self._load_model()
        
        if self._model == "failed":
            return MultimodalVerificationResult(
                is_consistent=False, 
                consistency_score=0.0, 
                explanation="AI Vision Model failed to load on server.",
                error="Model initialization failed"
            )
            
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # Predict
            inputs = self._processor(text=[text], images=image, return_tensors="pt", padding=True)
            outputs = self._model(**inputs)
            
            # CLIP cosine similarity between image and text features (scaled)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)  # Usually helpful if multiple texts
            
            # For a single text-image pair, we look at the raw cosine similarity score
            # Score usually ranges from 15 to 30. Higher is better. 
            similarity = logits_per_image[0][0].item()
            
            # Very loose heuristic threshold for identical contexts
            # Fine-tuning might adjust this, but for demonstration:
            threshold = 24.0
            is_consistent = similarity >= threshold
            
            # Scale similarity strictly between 0 and 100 for display
            normalized = max(0, min(100, (similarity - 15) / 15 * 100))
            
            explanation = "Image context perfectly matches the claim." if is_consistent else \
                          "The image visually contradicts or is unrelated to the textual claim provided."
                          
            return MultimodalVerificationResult(
                is_consistent=bool(is_consistent),
                consistency_score=round(normalized, 1),
                explanation=f"{explanation} (Consistency index: {similarity:.1f})"
            )
            
        except Exception as e:
            logger.error(f"Multimodal check failed: {e}")
            return MultimodalVerificationResult(
                is_consistent=False,
                consistency_score=0.0,
                explanation="Failed to verify image context due to an error.",
                error=str(e)
            )
