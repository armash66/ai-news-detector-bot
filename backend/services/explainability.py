"""
Explainability engine for the misinformation classifier.

Provides three complementary explanation methods:
  1. SHAP (SHapley Additive exPlanations) for token-level importance
  2. LIME (Local Interpretable Model-agnostic Explanations) for local approximation
  3. Attention visualization from transformer layers

All methods highlight which parts of the text most influenced the model's prediction.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.utils.logger import get_logger

logger = get_logger("explainability")


@dataclass
class TokenImportance:
    """Importance score for a single token."""
    token: str
    score: float
    is_suspicious: bool = False


@dataclass
class ExplanationResult:
    """Full explanation output combining multiple methods."""
    method: str  # "shap", "lime", "attention", "combined"
    token_importances: list[TokenImportance] = field(default_factory=list)
    top_suspicious_phrases: list[str] = field(default_factory=list)
    summary: str = ""
    raw_scores: Optional[list[float]] = None


class ExplainabilityEngine:
    """Generates human-readable explanations for model predictions.

    Supports SHAP, LIME, and attention-based explanations. Falls back
    gracefully when libraries are not installed.
    """

    def __init__(self, classifier=None):
        """Initialize with an optional reference to a MisinformationClassifier."""
        self.classifier = classifier

    def explain_shap(
        self,
        text: str,
        classifier=None,
        max_tokens: int = 50,
    ) -> ExplanationResult:
        """Generate SHAP-based explanation.

        Args:
            text: Input text to explain.
            classifier: MisinformationClassifier instance.
            max_tokens: Maximum tokens to include in output.

        Returns:
            ExplanationResult with per-token SHAP values.
        """
        clf = classifier or self.classifier
        if clf is None:
            return ExplanationResult(
                method="shap",
                summary="No classifier provided for SHAP explanation.",
            )

        try:
            import shap

            def predict_fn(texts):
                """Prediction function for SHAP."""
                results = clf.predict_batch(list(texts))
                return np.array([
                    [r.probabilities.get("REAL", 0), r.probabilities.get("FAKE", 0)]
                    for r in results
                ])

            explainer = shap.Explainer(predict_fn, shap.maskers.Text(clf.tokenizer))
            shap_values = explainer([text])

            # Extract token importance for the predicted class
            tokens = shap_values.data[0]
            values = shap_values.values[0]

            # Use FAKE class values (index 1)
            fake_values = values[:, 1] if len(values.shape) > 1 else values

            importances = []
            for token, score in zip(tokens[:max_tokens], fake_values[:max_tokens]):
                importances.append(TokenImportance(
                    token=str(token),
                    score=round(float(score), 4),
                    is_suspicious=float(score) > 0.1,
                ))

            suspicious = [t.token for t in importances if t.is_suspicious]

            return ExplanationResult(
                method="shap",
                token_importances=importances,
                top_suspicious_phrases=suspicious[:10],
                summary=self._build_summary("SHAP", suspicious),
                raw_scores=fake_values.tolist(),
            )

        except ImportError:
            logger.warning("SHAP library not installed. Install with: pip install shap")
            return ExplanationResult(
                method="shap",
                summary="SHAP library not available. Install with: pip install shap",
            )
        except Exception as exc:
            logger.error("SHAP explanation failed: %s", exc)
            return ExplanationResult(
                method="shap",
                summary=f"SHAP explanation failed: {exc}",
            )

    def explain_lime(
        self,
        text: str,
        classifier=None,
        num_features: int = 20,
        num_samples: int = 500,
    ) -> ExplanationResult:
        """Generate LIME-based explanation.

        Args:
            text: Input text to explain.
            classifier: MisinformationClassifier instance.
            num_features: Number of top features to return.
            num_samples: Number of perturbation samples for LIME.

        Returns:
            ExplanationResult with locally weighted feature importances.
        """
        clf = classifier or self.classifier
        if clf is None:
            return ExplanationResult(
                method="lime",
                summary="No classifier provided for LIME explanation.",
            )

        try:
            from lime.lime_text import LimeTextExplainer

            def predict_fn(texts):
                results = clf.predict_batch(list(texts))
                return np.array([
                    [r.probabilities.get("REAL", 0), r.probabilities.get("FAKE", 0)]
                    for r in results
                ])

            explainer = LimeTextExplainer(class_names=["REAL", "FAKE"])
            explanation = explainer.explain_instance(
                text,
                predict_fn,
                num_features=num_features,
                num_samples=num_samples,
            )

            importances = []
            suspicious = []
            for word, score in explanation.as_list():
                is_sus = score > 0.05
                importances.append(TokenImportance(
                    token=word,
                    score=round(score, 4),
                    is_suspicious=is_sus,
                ))
                if is_sus:
                    suspicious.append(word)

            return ExplanationResult(
                method="lime",
                token_importances=importances,
                top_suspicious_phrases=suspicious[:10],
                summary=self._build_summary("LIME", suspicious),
            )

        except ImportError:
            logger.warning("LIME library not installed. Install with: pip install lime")
            return ExplanationResult(
                method="lime",
                summary="LIME library not available. Install with: pip install lime",
            )
        except Exception as exc:
            logger.error("LIME explanation failed: %s", exc)
            return ExplanationResult(
                method="lime",
                summary=f"LIME explanation failed: {exc}",
            )

    def explain_attention(
        self,
        text: str,
        classifier=None,
        top_k: int = 15,
    ) -> ExplanationResult:
        """Generate attention-based explanation.

        Extracts attention weights from the last transformer layer and
        maps them to input tokens.

        Args:
            text: Input text to explain.
            classifier: MisinformationClassifier instance.
            top_k: Number of highest-attention tokens to highlight.

        Returns:
            ExplanationResult with attention-weighted token importance.
        """
        clf = classifier or self.classifier
        if clf is None:
            return ExplanationResult(
                method="attention",
                summary="No classifier provided for attention explanation.",
            )

        try:
            result = clf.predict(text, return_attention=True)
            if result.attention_weights is None:
                return ExplanationResult(
                    method="attention",
                    summary="Model did not return attention weights.",
                )

            tokens = clf.tokenizer.tokenize(
                text, max_length=512, truncation=True
            )

            # Average attention across sequence for CLS token (first row)
            cls_attention = result.attention_weights[0]  # CLS -> all tokens
            if isinstance(cls_attention, list):
                cls_attention = np.array(cls_attention)

            # Map attention to tokens (skip special tokens)
            importances = []
            for i, (token, attn) in enumerate(
                zip(tokens[:len(cls_attention) - 2], cls_attention[1:])
            ):
                importances.append(TokenImportance(
                    token=token,
                    score=round(float(attn), 4),
                    is_suspicious=bool(float(attn) > np.mean(cls_attention) * 1.5),
                ))

            # Sort by attention score
            importances.sort(key=lambda t: t.score, reverse=True)
            top_tokens = importances[:top_k]
            suspicious = [t.token for t in top_tokens if t.is_suspicious]

            return ExplanationResult(
                method="attention",
                token_importances=top_tokens,
                top_suspicious_phrases=suspicious,
                summary=self._build_summary("Attention", suspicious),
            )

        except Exception as exc:
            logger.error("Attention explanation failed: %s", exc)
            return ExplanationResult(
                method="attention",
                summary=f"Attention explanation failed: {exc}",
            )

    def explain(
        self,
        text: str,
        classifier=None,
        methods: Optional[list[str]] = None,
    ) -> dict[str, ExplanationResult]:
        """Run multiple explanation methods.

        Args:
            text: Input text.
            classifier: Classifier instance.
            methods: List of methods to run. Default: ["attention"].

        Returns:
            Dictionary mapping method name to ExplanationResult.
        """
        methods = methods or ["attention"]
        results = {}

        method_map = {
            "shap": self.explain_shap,
            "lime": self.explain_lime,
            "attention": self.explain_attention,
        }

        for method in methods:
            fn = method_map.get(method)
            if fn:
                results[method] = fn(text, classifier=classifier)
            else:
                logger.warning("Unknown explanation method: %s", method)

        return results

    @staticmethod
    def _build_summary(method: str, suspicious_tokens: list[str]) -> str:
        """Build a human-readable summary."""
        if not suspicious_tokens:
            return f"{method} analysis: No highly suspicious tokens identified."
        token_list = ", ".join(f"'{t}'" for t in suspicious_tokens[:5])
        return (
            f"{method} analysis identified {len(suspicious_tokens)} suspicious "
            f"token(s). Key indicators: {token_list}."
        )
