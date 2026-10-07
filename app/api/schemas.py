from pydantic import BaseModel, field_validator


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be empty.")
        return value.strip()


class Citation(BaseModel):
    context_id: int
    source: str
    page: int


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]