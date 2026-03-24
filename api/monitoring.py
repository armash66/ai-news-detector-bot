"""Monitoring API Router — Prometheus metrics and detailed health."""

from fastapi import APIRouter
import time
import os
import psutil

router = APIRouter()

START_TIME = time.time()

@router.get("/metrics")
def get_metrics():
    """Detailed metrics for monitoring (CPU, Memory, Uptime)."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "uptime_seconds": time.time() - START_TIME,
        "cpu_percent": process.cpu_percent(),
        "memory_mb": memory_info.rss / 1024 / 1024,
        "threads": process.num_threads(),
        "status": "healthy"
    }
