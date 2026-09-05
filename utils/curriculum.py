# -*- coding: utf-8 -*-
"""12-week Family Elite Thinking curriculum — spine for Systems/Uncertainty + AI Judgment."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.knowledge import load_user_history, save_user_history

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CURRICULUM_FILE = DATA_DIR / "curriculum_12w.json"


def load_curriculum() -> Dict[str, Any]:
    if not CURRICULUM_FILE.exists():
        return {"version": "0", "title": "", "weeks": []}
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_weeks() -> List[Dict[str, Any]]:
    return load_curriculum().get("weeks", [])


def get_week(week_num: int) -> Optional[Dict[str, Any]]:
    for w in get_weeks():
        if int(w.get("week", 0)) == int(week_num):
            return w
    return None


def _progress_bucket(hist: Dict[str, Any]) -> Dict[str, Any]:
    return hist.setdefault(
        "curriculum_12w",
        {
            "started_at": None,
            "weeks": {},  # "1": {status, exercise_answer, quiz_score, completed_at, notes}
            "current_week": 1,
        },
    )


def get_user_curriculum_progress(username: str) -> Dict[str, Any]:
    hist = load_user_history(username)
    return _progress_bucket(hist)


def get_week_progress(username: str, week_num: int) -> Dict[str, Any]:
    prog = get_user_curriculum_progress(username)
    return prog.get("weeks", {}).get(
        str(week_num),
        {"status": "not_started", "exercise_answer": "", "quiz_score": None, "notes": ""},
    )


def start_curriculum(username: str) -> None:
    hist = load_user_history(username)
    bucket = _progress_bucket(hist)
    if not bucket.get("started_at"):
        bucket["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bucket["current_week"] = bucket.get("current_week") or 1
    save_user_history(username, hist)


def save_week_exercise(username: str, week_num: int, answer: str, notes: str = "") -> None:
    hist = load_user_history(username)
    bucket = _progress_bucket(hist)
    if not bucket.get("started_at"):
        bucket["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w = bucket.setdefault("weeks", {}).setdefault(str(week_num), {})
    w["exercise_answer"] = answer
    w["notes"] = notes
    w["status"] = w.get("status") if w.get("status") == "completed" else "in_progress"
    w["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bucket["current_week"] = max(int(bucket.get("current_week") or 1), int(week_num))
    save_user_history(username, hist)


def save_week_quiz_score(username: str, week_num: int, score: int, total: int) -> None:
    hist = load_user_history(username)
    bucket = _progress_bucket(hist)
    w = bucket.setdefault("weeks", {}).setdefault(str(week_num), {})
    w["quiz_score"] = score
    w["quiz_total"] = total
    w["status"] = w.get("status") if w.get("status") == "completed" else "in_progress"
    w["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_history(username, hist)


def complete_week(username: str, week_num: int, is_admin: Optional[bool] = None) -> tuple[bool, str]:
    """Mark week complete if exercise present (quiz optional but recommended). Admin can bypass answer requirement."""
    if is_admin is None:
        try:
            from utils.auth import is_admin as _check_admin
            is_admin = _check_admin()
        except Exception:
            is_admin = False

    hist = load_user_history(username)
    bucket = _progress_bucket(hist)
    w = bucket.setdefault("weeks", {}).setdefault(str(week_num), {})
    if not is_admin and not (w.get("exercise_answer") or "").strip():
        return False, "Cần nộp bài tập áp dụng trước khi hoàn thành tuần."
    if is_admin and not (w.get("exercise_answer") or "").strip():
        w["exercise_answer"] = "[Admin hoàn thành duyệt nội dung]"
    w["status"] = "completed"
    w["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Unlock next week pointer
    nxt = int(week_num) + 1
    if nxt <= 12:
        bucket["current_week"] = max(int(bucket.get("current_week") or 1), nxt)
    save_user_history(username, hist)
    return True, f"Đã hoàn thành Tuần {week_num}."


def curriculum_summary(username: str) -> Dict[str, Any]:
    weeks = get_weeks()
    prog = get_user_curriculum_progress(username)
    done = 0
    for w in weeks:
        status_val = prog.get("weeks", {}).get(str(w["week"]), {}).get("status")
        if status_val == "completed":
            done += 1
    total = len(weeks) or 12
    return {
        "completed_weeks": done,
        "total_weeks": total,
        "pct": round(100.0 * done / total, 1) if total else 0,
        "current_week": prog.get("current_week") or 1,
        "started_at": prog.get("started_at"),
    }


def is_week_unlocked(username: str, week_num: int, is_admin: Optional[bool] = None) -> bool:
    """Week 1 always open; admin has all weeks unlocked; week N open if N-1 completed OR N <= current_week."""
    if is_admin is None:
        try:
            from utils.auth import is_admin as _check_admin
            is_admin = _check_admin()
        except Exception:
            is_admin = False

    if is_admin or int(week_num) <= 1:
        return True
    prog = get_user_curriculum_progress(username)
    prev = prog.get("weeks", {}).get(str(int(week_num) - 1), {})
    if prev.get("status") == "completed":
        return True
    # Soft unlock: allow browsing up to current_week pointer
    return int(week_num) <= int(prog.get("current_week") or 1)
