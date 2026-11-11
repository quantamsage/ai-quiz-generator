"""Scoring, retry, and export helpers. Kept free of Streamlit so they are easy to test."""

import csv
import io
import random


def calculate_score(quiz: list[dict], answers: list[str | None]) -> int:
    """Count how many answers match the correct answer."""
    return sum(1 for q, a in zip(quiz, answers) if a == q["correct_answer"])


def missed_questions(quiz: list[dict], answers: list[str | None], shuffle: bool = True) -> list[dict]:
    """Return copies of the questions answered wrongly, ready to retake.

    Options are reshuffled by default so a retry tests the answer, not its position.
    """
    missed = []
    for q, a in zip(quiz, answers):
        if a == q["correct_answer"]:
            continue
        retry = dict(q)
        retry["options"] = list(q["options"])
        if shuffle:
            random.shuffle(retry["options"])
        missed.append(retry)
    return missed


def results_csv(topic: str, quiz: list[dict], answers: list[str | None]) -> str:
    """Build a CSV of the quiz results for download."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["topic", "number", "question", "your_answer", "correct_answer", "result", "explanation"])
    for i, (q, a) in enumerate(zip(quiz, answers), start=1):
        result = "correct" if a == q["correct_answer"] else "wrong"
        writer.writerow([topic, i, q["question"], a or "", q["correct_answer"], result, q["explanation"]])
    return buffer.getvalue()
