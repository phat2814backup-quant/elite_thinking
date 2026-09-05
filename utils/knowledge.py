# -*- coding: utf-8 -*-
"""Shared knowledge base (JSON files) + per-user history (Supabase or local JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KB_FILE = DATA_DIR / "knowledge_base.json"
HISTORIES_DIR = DATA_DIR / "histories"
HISTORIES_DIR.mkdir(parents=True, exist_ok=True)


def load_knowledge_base() -> Dict[str, Any]:
    if not KB_FILE.exists():
        return {"metadata": {}, "principles": []}
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_principles(domain: Optional[str] = None) -> List[Dict[str, Any]]:
    kb = load_knowledge_base()
    principles = kb.get("principles", [])
    if domain and domain != "Tất cả":
        principles = [p for p in principles if p.get("domain") == domain]
    return principles


def get_domains() -> List[str]:
    principles = get_principles()
    domains = sorted({p.get("domain", "Khác") for p in principles})
    return ["Tất cả"] + domains


def search_principles(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    if not query.strip():
        return []
    q = query.lower().strip()
    results = []
    for p in get_principles():
        text = " ".join(
            [
                str(p.get("principle_name", "")),
                str(p.get("domain", "")),
                str(p.get("description", "")),
                str(p.get("intuitive_summary", "")),
                str(p.get("formal_definition", "")),
            ]
        ).lower()
        if q in text:
            results.append(p)
        if len(results) >= limit:
            break
    return results


# ---------- Per-user history ----------

def _empty_history(username: str) -> Dict[str, Any]:
    return {
        "username": username,
        "analyses": [],
        "training": {},
        "updated_at": None,
    }


def _history_path(username: str) -> Path:
    safe = "".join(c for c in username if c.isalnum() or c in ("_", "-"))
    return HISTORIES_DIR / f"{safe}.json"


def _load_history_local(username: str) -> Dict[str, Any]:
    path = _history_path(username)
    if not path.exists():
        return _empty_history(username)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _empty_history(username)


def _save_history_local(username: str, data: Dict[str, Any]) -> None:
    path = _history_path(username)
    data["username"] = username
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
    tmp.replace(path)


def _load_history_supabase(username: str) -> Optional[Dict[str, Any]]:
    from utils.db import get_supabase

    client = get_supabase()
    if client is None:
        return None
    try:
        res = (
            client.table("user_histories")
            .select("data")
            .eq("username", username)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        if not rows:
            return _empty_history(username)
        data = rows[0].get("data") or {}
        if not isinstance(data, dict):
            data = {}
        data["username"] = username
        return data
    except Exception:
        return None


def _save_history_supabase(username: str, data: Dict[str, Any]) -> bool:
    from utils.db import get_supabase

    client = get_supabase()
    if client is None:
        return False
    data = dict(data)
    data["username"] = username
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        client.table("user_histories").upsert(
            {
                "username": username,
                "data": data,
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }
        ).execute()
        return True
    except Exception:
        return False


def load_user_history(username: str) -> Dict[str, Any]:
    from utils.db import get_supabase

    if get_supabase() is not None:
        remote = _load_history_supabase(username)
        if remote is not None:
            return remote
    return _load_history_local(username)


def save_user_history(username: str, data: Dict[str, Any]) -> None:
    from utils.db import get_supabase

    data = dict(data)
    data["username"] = username
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if get_supabase() is not None:
        if _save_history_supabase(username, data):
            return
    _save_history_local(username, data)


def append_analysis(
    username: str,
    problem: str,
    result_summary: str,
    full_result: Optional[Dict[str, Any]] = None,
    user_note: str = "",
) -> Dict[str, Any]:
    hist = load_user_history(username)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_id = f"ana_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    entry: Dict[str, Any] = {
        "id": entry_id,
        "time": now_str,
        "problem": problem.strip(),
        "summary": result_summary[:1000],
        "user_note": user_note.strip(),
    }
    if full_result:
        entry["is_valid"] = full_result.get("is_valid", True)
        entry["details"] = full_result
    hist.setdefault("analyses", []).insert(0, entry)
    hist["analyses"] = hist["analyses"][:100]
    save_user_history(username, hist)
    return entry


def update_analysis_note(username: str, analysis_id_or_time: str, user_note: str) -> bool:
    """Cập nhật ghi chú / nhận định cá nhân cho một bản phân rã cụ thể."""
    hist = load_user_history(username)
    analyses = hist.get("analyses", [])
    updated = False
    for a in analyses:
        if a.get("id") == analysis_id_or_time or a.get("time") == analysis_id_or_time:
            a["user_note"] = user_note.strip()
            updated = True
            break
    if updated:
        save_user_history(username, hist)
    return updated


def delete_analysis(username: str, analysis_id_or_time: str) -> bool:
    """Xóa một bản phân rã khỏi lịch sử người dùng."""
    hist = load_user_history(username)
    analyses = hist.get("analyses", [])
    new_analyses = [
        a for a in analyses 
        if a.get("id") != analysis_id_or_time and a.get("time") != analysis_id_or_time
    ]
    if len(new_analyses) != len(analyses):
        hist["analyses"] = new_analyses
        save_user_history(username, hist)
        return True
    return False


def save_training_answer(
    username: str, lesson_id: str, answer: str, feedback: str = ""
) -> None:
    hist = load_user_history(username)
    hist.setdefault("training", {})[lesson_id] = {
        "answer": answer,
        "feedback": feedback,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_user_history(username, hist)


def list_all_user_histories() -> List[Dict[str, Any]]:
    from utils.db import get_supabase

    client = get_supabase()
    if client is not None:
        try:
            res = client.table("user_histories").select("username, data, updated_at").execute()
            results = []
            for row in res.data or []:
                data = row.get("data") or {}
                if not isinstance(data, dict):
                    data = {}
                data["username"] = row.get("username") or data.get("username", "?")
                if row.get("updated_at") and not data.get("updated_at"):
                    data["updated_at"] = row["updated_at"]
                results.append(data)
            return results
        except Exception:
            pass

    results = []
    if not HISTORIES_DIR.exists():
        return results
    for path in sorted(HISTORIES_DIR.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        except Exception:
            continue
    return results
