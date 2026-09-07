# -*- coding: utf-8 -*-
"""
Manager for Elite English Vocabulary (First-Principles Roots).
100% Static / Zero-API.
Manages vocabulary lookup, Lego root breakdowns, and persistence of user mastery.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VOCAB_FILE = DATA_DIR / "elite_vocab.json"
HISTORIES_DIR = DATA_DIR / "histories"


@st.cache_data(show_spinner=False)
def load_elite_vocab() -> Dict[str, Any]:
    """Tải ngân hàng từ vựng tinh hoa từ file static JSON."""
    if not VOCAB_FILE.exists():
        return {"metadata": {}, "categories": [], "vocab_list": []}
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"metadata": {"error": str(e)}, "categories": [], "vocab_list": []}


def get_all_vocab() -> List[Dict[str, Any]]:
    """Trả về danh sách toàn bộ từ vựng."""
    data = load_elite_vocab()
    return data.get("vocab_list", [])


def get_categories() -> List[str]:
    """Trả về danh mục các nhóm từ vựng."""
    data = load_elite_vocab()
    cats = data.get("categories", [])
    if not cats:
        seen = []
        for item in data.get("vocab_list", []):
            c = item.get("category")
            if c and c not in seen:
                seen.append(c)
        return seen
    return cats


def get_pillars() -> List[Dict[str, Any]]:
    """Trả về danh sách 3 Cột trụ lớn (9 Chế độ, 88 Mô hình Munger, 100 Nguyên lý)."""
    data = load_elite_vocab()
    raw_pillars = data.get("pillars", [])
    normalized_pillars = []
    for p in raw_pillars:
        pid = p.get("pillar_id") or p.get("id", "")
        pname = p.get("pillar_name") or p.get("name", "")
        raw_topics = p.get("topics", [])
        norm_topics = []
        for t in raw_topics:
            tcode = t.get("topic_code") or t.get("code", "")
            tname = t.get("topic_name") or t.get("name", "")
            wcount = t.get("words_count", t.get("word_count", 0))
            norm_topics.append({
                "topic_code": tcode,
                "code": tcode,
                "topic_name": tname,
                "name": tname,
                "words_count": wcount,
                "word_count": wcount,
            })
        normalized_pillars.append({
            "pillar_id": pid,
            "id": pid,
            "pillar_name": pname,
            "name": pname,
            "topics": norm_topics,
            "word_count": p.get("word_count", sum(t.get("words_count", 0) for t in norm_topics)),
        })
    return normalized_pillars


def get_topics_by_pillar(pillar_id: str) -> List[Dict[str, Any]]:
    """Trả về danh sách các chủ đề / mô hình cụ thể thuộc về 1 cột trụ."""
    pillars = get_pillars()
    if not pillar_id or pillar_id == "all":
        all_topics: List[Dict[str, Any]] = []
        for p in pillars:
            all_topics.extend(p.get("topics", []))
        return all_topics

    for p in pillars:
        if p.get("pillar_id") == pillar_id or p.get("id") == pillar_id:
            return p.get("topics", [])
    return []



def get_vocab_by_pillar(pillar_id: str) -> List[Dict[str, Any]]:
    """Lọc danh sách từ vựng theo cột trụ lớn."""
    all_v = get_all_vocab()
    if not pillar_id or pillar_id == "all":
        return all_v
    return [v for v in all_v if v.get("pillar_id") == pillar_id]


def get_vocab_by_topic(topic_code: str) -> List[Dict[str, Any]]:
    """Lọc danh sách từ vựng theo chủ đề / mô hình cụ thể (VD: MODE-01, PHYS-01)."""
    all_v = get_all_vocab()
    if not topic_code or topic_code == "all":
        return all_v
    return [v for v in all_v if v.get("topic_code") == topic_code]


def get_vocab_by_id(vocab_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết một từ vựng theo ID."""
    for item in get_all_vocab():
        if item.get("id") == vocab_id:
            return item
    return None



# -----------------------------------------------------------------------------
# User Progress & Mastery Persistence (Supabase + Local fallback)
# -----------------------------------------------------------------------------
def get_user_vocab_state(username: str) -> Dict[str, Any]:
    """Lấy trạng thái học từ vựng của user (đã thuộc, đánh dấu sao, số lần ôn tập)."""
    if not username:
        return {}

    cache_key = f"_vocab_state_{username}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    state = {}
    from utils.db import get_supabase, is_supabase_enabled

    if is_supabase_enabled():
        client = get_supabase()
        if client:
            try:
                res = client.table("user_histories").select("data").eq("username", username).execute()
                if res.data and len(res.data) > 0:
                    blob = res.data[0].get("data") or {}
                    state = blob.get("elite_vocab_mastery", {})
            except Exception:
                pass

    if not state:
        user_file = HISTORIES_DIR / f"{username}.json"
        if user_file.exists():
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    blob = json.load(f)
                    state = blob.get("elite_vocab_mastery", {})
            except Exception:
                pass

    st.session_state[cache_key] = state
    return state


def save_user_vocab_state(username: str, state: Dict[str, Any]) -> None:
    """Lưu trạng thái học từ vựng bền vững lên Supabase hoặc local JSON."""
    if not username:
        return

    cache_key = f"_vocab_state_{username}"
    st.session_state[cache_key] = state

    from utils.db import get_supabase, is_supabase_enabled

    if is_supabase_enabled():
        client = get_supabase()
        if client:
            try:
                res = client.table("user_histories").select("data").eq("username", username).execute()
                blob = {}
                if res.data and len(res.data) > 0:
                    blob = res.data[0].get("data") or {}
                blob["elite_vocab_mastery"] = state
                client.table("user_histories").upsert({"username": username, "data": blob}).execute()
                return
            except Exception:
                pass

    # Fallback local JSON
    HISTORIES_DIR.mkdir(parents=True, exist_ok=True)
    user_file = HISTORIES_DIR / f"{username}.json"
    blob = {}
    if user_file.exists():
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                blob = json.load(f)
        except Exception:
            blob = {}
    blob["elite_vocab_mastery"] = state
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)


def toggle_vocab_mastery(username: str, vocab_id: str) -> bool:
    """Bật/tắt trạng thái 'Đã thông suốt' của một từ vựng."""
    state = get_user_vocab_state(username)
    item_state = state.get(vocab_id, {})
    current_status = item_state.get("mastered", False)
    new_status = not current_status
    item_state["mastered"] = new_status
    item_state["last_reviewed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item_state["reviews_count"] = item_state.get("reviews_count", 0) + 1
    state[vocab_id] = item_state
    save_user_vocab_state(username, state)
    return new_status


def toggle_vocab_star(username: str, vocab_id: str) -> bool:
    """Bật/tắt gắn sao yêu thích cho một từ vựng."""
    state = get_user_vocab_state(username)
    item_state = state.get(vocab_id, {})
    current_star = item_state.get("starred", False)
    new_star = not current_star
    item_state["starred"] = new_star
    state[vocab_id] = item_state
    save_user_vocab_state(username, state)
    return new_star


def record_quiz_attempt(username: str, vocab_id: str, is_correct: bool) -> None:
    """Ghi nhận kết quả làm quiz của user."""
    state = get_user_vocab_state(username)
    item_state = state.get(vocab_id, {})
    item_state["quiz_attempts"] = item_state.get("quiz_attempts", 0) + 1
    if is_correct:
        item_state["quiz_correct"] = item_state.get("quiz_correct", 0) + 1
        item_state["mastered"] = True
    item_state["last_reviewed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state[vocab_id] = item_state
    save_user_vocab_state(username, state)


def get_vocab_stats(username: str) -> Dict[str, Any]:
    """Tính toán tỷ lệ hoàn thành và thống kê theo từng nhóm và từng cột trụ."""
    all_vocab = get_all_vocab()
    total_words = len(all_vocab)
    state = get_user_vocab_state(username)

    mastered_count = sum(1 for item in all_vocab if state.get(item["id"], {}).get("mastered"))
    starred_count = sum(1 for item in all_vocab if state.get(item["id"], {}).get("starred"))

    categories_stats: Dict[str, Dict[str, int]] = {}
    for item in all_vocab:
        cat = item.get("category", "Khác")
        if cat not in categories_stats:
            categories_stats[cat] = {"total": 0, "mastered": 0}
        categories_stats[cat]["total"] += 1
        if state.get(item["id"], {}).get("mastered"):
            categories_stats[cat]["mastered"] += 1

    pillars_stats: Dict[str, Dict[str, Any]] = {}
    pillars = get_pillars()
    for p in pillars:
        pid = p.get("id", "")
        p_words = [v for v in all_vocab if v.get("pillar_id") == pid]
        p_mastered = sum(1 for v in p_words if state.get(v["id"], {}).get("mastered"))
        p_pct = int((p_mastered / len(p_words)) * 100) if p_words else 0
        pillars_stats[pid] = {
            "name": p.get("name", pid),
            "total": len(p_words),
            "mastered": p_mastered,
            "progress_percent": p_pct,
            "topics_count": len(p.get("topics", [])),
        }

    progress_percent = int((mastered_count / total_words) * 100) if total_words > 0 else 0

    return {
        "total_words": total_words,
        "mastered_count": mastered_count,
        "starred_count": starred_count,
        "progress_percent": progress_percent,
        "categories_stats": categories_stats,
        "pillars_stats": pillars_stats,
    }

