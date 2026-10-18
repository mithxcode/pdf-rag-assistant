from typing import List
from pydantic import BaseModel, Field


class LLMAnswer(BaseModel):
    """Schema jo OpenAI Structured Outputs se enforce hota hai."""
    answer: str
    used_chunks: List[int] = Field(description="Context ke wo chunk numbers jinse answer bana")
    found_in_context: bool


class AnswerSchema(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
