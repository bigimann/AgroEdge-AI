from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Farmer's agricultural question")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]