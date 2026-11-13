from typing import Literal
from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=6)

    @field_validator('question')
    @classmethod
    def strip_question(cls, value):
        if len(value.strip()) < 3:
            raise ValueError('Informe uma pergunta com pelo menos três caracteres')
        return value.strip()


class ReviewRequest(BaseModel):
    decision: Literal['approved', 'rejected']
    reviewer: str = Field(min_length=2, max_length=100)
    note: str = Field(default='', max_length=2000)

    @field_validator('reviewer')
    @classmethod
    def strip_reviewer(cls, value):
        if len(value.strip()) < 2:
            raise ValueError('Identifique o revisor')
        return value.strip()
