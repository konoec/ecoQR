from fastapi import FastAPI
from ai_validation import (
    validate_recycling_classification,
    analyze_image_quality,
    get_recycling_tips
)
from typing import List, Dict, Any
import time

app = FastAPI(
    title="EcoRewards AI Validation Service",
    description="Mock AI service for recycling classification validation",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Validation Service",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.post("/validate")
async def validate_classification(
    image_data: str,
    expected_items: List[Dict[str, Any]]
):
    """Validate recycling classification"""
    result = await validate_recycling_classification(image_data, expected_items)
    return {"success": True, "result": result}


@app.post("/analyze")
async def analyze_image(image_data: str):
    """Analyze image quality"""
    result = await analyze_image_quality(image_data)
    return {"success": True, "analysis": result}


@app.get("/tips/{category}")
async def get_tips(category: str):
    """Get recycling tips"""
    tips = await get_recycling_tips(category)
    return {"category": category, "tips": tips}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
