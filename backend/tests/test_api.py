"""
Tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.api.main import create_app
from backend.services.analyzer import AnalysisReport


@pytest.fixture
def client():
    """Create a test client with mocked analyzer."""
    app = create_app()

    mock_report = AnalysisReport(
        input_text="Test text",
        classification={
            "label": "FAKE",
            "confidence": 0.87,
            "probabilities": {"REAL": 0.13, "FAKE": 0.87},
        },
        claims=[{
            "text": "Test claim",
            "type": "factual",
            "confidence": 0.8,
            "entities": ["Test"],
        }],
        credibility={
            "score": 28.5,
            "verdict": "Likely Misinformation",
            "reasons": ["AI model flagged content"],
            "component_scores": {},
        },
    )

    mock_analyzer = MagicMock()
    mock_analyzer.analyze_text.return_value = mock_report
    mock_analyzer.analyze_url.return_value = mock_report
    mock_analyzer.verify_claim.return_value = mock_report

    with patch("backend.api.dependencies.get_analyzer", return_value=mock_analyzer):
        yield TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "VeritasAI" in data["service"]


class TestAnalyzeEndpoint:
    def test_analyze_text(self, client):
        response = client.post("/api/v1/analyze", json={
            "text": "NASA announced today that alien life has been confirmed in Arizona desert location.",
        })
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert "credibility" in data

    def test_analyze_text_too_short(self, client):
        response = client.post("/api/v1/analyze", json={
            "text": "Short",
        })
        assert response.status_code == 422  # Validation error

    def test_analyze_url(self, client):
        response = client.post("/api/v1/analyze-url", json={
            "url": "https://example.com/article",
        })
        assert response.status_code == 200


class TestVerifyEndpoint:
    def test_verify_claim(self, client):
        response = client.post("/api/v1/verify-claim", json={
            "claim": "NASA confirmed alien life in Arizona desert",
        })
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert "credibility" in data

    def test_verify_claim_too_short(self, client):
        response = client.post("/api/v1/verify-claim", json={
            "claim": "Short",
        })
        assert response.status_code == 422
