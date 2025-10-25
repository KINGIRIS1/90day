from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class UsageStats(BaseModel):
    """Track usage statistics for cost estimation"""
    total_scans: int = 0
    total_images: int = 0
    emergent_calls: int = 0
    openai_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    period_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: Optional[datetime] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_scans": 150,
                "total_images": 1500,
                "emergent_calls": 1200,
                "openai_calls": 300,
                "total_input_tokens": 1500000,
                "total_output_tokens": 300000,
                "estimated_cost_usd": 6.75,
                "period_start": "2025-01-01T00:00:00Z"
            }
        }
    }

# Pricing constants (per 1K tokens)
PRICING = {
    "emergent": {
        "gpt-4o": {
            "input": 0.0025,   # $2.50 per 1M tokens
            "output": 0.010     # $10.00 per 1M tokens
        }
    },
    "openai": {
        "gpt-4o-mini": {
            "input": 0.00015,   # $0.15 per 1M tokens
            "output": 0.00012,  # $0.60 per 1M tokens
            "vision": 0.0017    # Vision API surcharge per image
        }
    }
}

def estimate_tokens(image_size_kb: int = 50, response_length: int = 200) -> dict:
    """
    Estimate tokens for an image scan
    
    Args:
        image_size_kb: Compressed image size in KB (default 50KB after compression)
        response_length: Expected response tokens (default 200)
    
    Returns:
        dict with input_tokens and output_tokens
    """
    # GPT-4 Vision token estimation:
    # - Image: ~85 tokens per tile (512x512)
    # - For 800px image: ~4 tiles = 340 tokens
    # - Prompt: ~600 tokens (document types list + instructions)
    base_image_tokens = 340
    prompt_tokens = 600
    
    return {
        "input_tokens": base_image_tokens + prompt_tokens,  # ~940 tokens
        "output_tokens": response_length  # ~200 tokens
    }

def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    image_count: int = 1
) -> float:
    """
    Calculate cost for LLM API call
    
    Args:
        provider: "emergent" or "openai"
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        image_count: Number of images (for vision surcharge)
    
    Returns:
        Estimated cost in USD
    """
    if provider not in PRICING or model not in PRICING[provider]:
        # Default to emergent gpt-4o pricing
        pricing = PRICING["emergent"]["gpt-4o"]
        vision_cost = 0
    else:
        pricing = PRICING[provider][model]
        vision_cost = pricing.get("vision", 0) * image_count
    
    # Calculate cost (pricing is per 1K tokens)
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    
    total_cost = input_cost + output_cost + vision_cost
    return round(total_cost, 6)

def format_cost_display(cost_usd: float) -> dict:
    """Format cost for display in multiple currencies"""
    return {
        "usd": f"${cost_usd:.4f}",
        "vnd": f"{int(cost_usd * 24000):,} VNĐ",  # Rough conversion
        "usd_raw": cost_usd
    }
