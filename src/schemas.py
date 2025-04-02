from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class NoteBaseSchema(BaseModel):
    title: str = Field(max_length=100)
    content: str


class NoteCreateRequestSchema(NoteBaseSchema):
    pass


class NoteResponseSchema(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class NoteDetailResponseSchema(NoteResponseSchema):
    summary: str | None = None
    created_at: datetime
    version: int
    previous_version_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class NoteUpdateRequestSchema(NoteBaseSchema):
    pass


class MessageResponseSchema(BaseModel):
    message: str


class CommonWordSchema(BaseModel):
    word: str
    count: int


class NoteLengthSchema(BaseModel):
    id: int
    word_count: int


class NotesAnalyticsSchema(BaseModel):
    total_notes: int
    total_words: int
    average_length: float
    top_longest_notes: list[NoteLengthSchema]
    top_shortest_notes: list[NoteLengthSchema]
    most_common_words: list[CommonWordSchema]
