import re
from collections import Counter

import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.crud import get_notes_list


def clean_text(text: str):
    """
    Cleans the input text by removing punctuation,
    converting to lowercase, and splitting into words.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        list[str]: A list of words from the cleaned text.
    """
    if not text:
        return []
    text = re.sub(r"[^\w\s]", "", text).lower()
    return text.split()


def analyze_note_content(db: Session):
    """
    Analyzes the content of notes in the database
    and returns various statistics.

    Args:
        db (Session): The database session to use for querying notes.

    Raises:
        HTTPException: If no notes are found in the database.

    Returns:
        dict: A dictionary containing the following keys:
            - total_notes (int): The total number of notes.
            - total_words (int): The total number of words across all notes.
            - average_length (float): The average length of notes in words.
            - top_longest_notes (list[dict]): A list of the top 3 longest
                                              notes with their IDs
                                              and word counts.
            - top_shortest_notes (list[dict]): A list of the top 3 shortest
                                               notes with their IDs
                                               and word counts.
            - most_common_words (list[dict]): A list of the 10 most common
                                              words and their frequencies.
    """
    notes = get_notes_list(db=db, is_deleted=False)

    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )

    df = pd.DataFrame(
        [
            {
                "id": note.id,
                "content": note.content,
                "word_count": len(clean_text(note.content))
                if note.content
                else 0,
            }
            for note in notes
        ]
    )

    total_words = df["word_count"].sum()
    avg_length = np.mean(df["word_count"])

    top_longest = df.nlargest(
        3, "word_count"
    )[["id", "word_count"]].to_dict("records")
    top_shortest = df.nsmallest(
        3, "word_count"
    )[["id", "word_count"]].to_dict("records")

    all_words = df["content"].dropna().apply(clean_text).explode()
    word_freq = Counter(all_words)
    common_words = word_freq.most_common(10) if word_freq else []

    return {
        "total_notes": len(df),
        "total_words": int(total_words),
        "average_length": round(avg_length, 2),
        "top_longest_notes": top_longest,
        "top_shortest_notes": top_shortest,
        "most_common_words": [
            {"word": w, "count": c} for w, c in common_words
        ],
    }
