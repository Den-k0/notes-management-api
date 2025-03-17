from datetime import datetime

from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    Text,
    DateTime,
    Boolean,
    func,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        UniqueConstraint(
            "previous_version_id", "is_current",
            name="only_one_current_version"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("notes.id"), nullable=True
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
