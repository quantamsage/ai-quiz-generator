import csv
import io

from scoring import calculate_score, missed_questions, results_csv

QUIZ = [
    {"question": "2 + 2?", "options": ["3", "4", "5", "6"], "correct_answer": "4", "explanation": "Basic sum."},
    {"question": "Capital of Kenya?", "options": ["Mombasa", "Kisumu", "Nairobi", "Nakuru"],
     "correct_answer": "Nairobi", "explanation": "Nairobi is the capital."},
]


def test_score_and_missed():
    answers = ["4", "Mombasa"]
    assert calculate_score(QUIZ, answers) == 1
    missed = missed_questions(QUIZ, answers)
    assert [q["question"] for q in missed] == ["Capital of Kenya?"]
    assert sorted(missed[0]["options"]) == sorted(QUIZ[1]["options"])
    assert QUIZ[1]["options"] == ["Mombasa", "Kisumu", "Nairobi", "Nakuru"]  # original untouched


def test_results_csv():
    rows = list(csv.DictReader(io.StringIO(results_csv("Mixed", QUIZ, ["4", "Mombasa"]))))
    assert [r["result"] for r in rows] == ["correct", "wrong"]
    assert rows[1]["correct_answer"] == "Nairobi"
