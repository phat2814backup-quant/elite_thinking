# -*- coding: utf-8 -*-
"""
Module Lưu Trữ Bền Vững (Cloud Supabase + Local JSON Fallback)
Quản trị toàn diện:
1. Máy Quét Đọc Vị Thế Cuộc (macro_radar_scans)
2. Phân Rã Vấn Đề Thực Chiến 9 Lăng Kính (analyses)
3. Nhật Ký Quyết Định & Đo Sai Số (decision_journal)
"""

from __future__ import annotations

import os
import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

# Tự động nạp cấu hình từ .env
try:
    import dotenv
    candidate_env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.abspath(".env"),
        "D:/02_HocTap/elite/.env",
        "D:/02_HocTap/elite_thinking/.env"
    ]
    for p in candidate_env_paths:
        if os.path.exists(p):
            dotenv.load_dotenv(dotenv_path=p, override=True)
except ImportError:
    pass

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)

LOCAL_MACRO_FILE = os.path.join(DATA_DIR, "macro_scans_history.json")
LOCAL_ANALYSES_FILE = os.path.join(DATA_DIR, "analyses_history.json")
LOCAL_DECISIONS_FILE = os.path.join(DATA_DIR, "decision_journal.json")
LOCAL_COMPRESSIONS_FILE = os.path.join(DATA_DIR, "compressions_history.json")
LOCAL_SCOUT_TREES_FILE = os.path.join(DATA_DIR, "macro_scout_trees.json")

_DEFAULT_URL = "https://szprfjzeauzstvmvgjrw.supabase.co"

DECISION_CATEGORIES = [
    "📈 Tài chính, Chứng khoán & Đầu tư",
    "💼 Sự nghiệp, Dự án & Kinh doanh",
    "🎒 Học tập, Học bổng & Chọn ngành",
    "🌱 Sức khỏe, Thói quen & Đời sống",
    "🤝 Mối quan hệ & Đàm phán",
]

REVIEW_INTERVALS = {
    "30 ngày (Ngắn hạn / Dự án nhanh)": 30,
    "90 ngày (Trung hạn / 1 Quý)": 90,
    "180 ngày (Dài hạn / Nửa năm)": 180,
    "365 ngày (Chiến lược 1 năm)": 365,
}

OUTCOME_RATINGS = {
    "🏆 Thành công vượt kỳ vọng (100%)": 100,
    "✅ Đúng như dự tính ban đầu (80%)": 80,
    "⚖️ Đúng một phần, có sai số (50%)": 50,
    "❌ Hoàn toàn sai lệch so với dự tính (0%)": 0,
}


def get_supabase_credentials() -> tuple[str, str]:
    """Lấy URL và Key từ st.secrets, .env, os.environ hoặc fallback an toàn."""
    url = ""
    key = ""

    # 1. Thử lấy từ st.secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "SUPABASE_URL" in st.secrets:
                url = str(st.secrets["SUPABASE_URL"]).strip()
            for k_name in ["SUPABASE_SERVICE_KEY", "SUPABASE_KEY", "SUPABASE_ANON_KEY"]:
                if k_name in st.secrets:
                    key = str(st.secrets[k_name]).strip()
                    if key:
                        break
    except Exception:
        pass

    # 2. Thử lấy từ os.environ / .env
    if not url:
        url = os.getenv("SUPABASE_URL", "").strip()
    if not key:
        key = (
            os.getenv("SUPABASE_SERVICE_KEY", "")
            or os.getenv("SUPABASE_KEY", "")
            or os.getenv("SUPABASE_ANON_KEY", "")
        ).strip()

    # 3. Fallback mặc định
    if not url:
        url = _DEFAULT_URL
    if not key:
        key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6cHJmanplYXV6c3R2bXZnanJ3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODU4ODUxNywiZXhwIjoyMTA0MTY0NTE3fQ."
            "oDdkRiCaGD3ljsUpqRJg8YZDANw7xvkSBDRuHh3KfOo"
        )

    return url, key


def get_supabase_client():
    """Khởi tạo hoặc lấy Supabase client đã cache."""
    try:
        import streamlit as st
        cache_key = "_supabase_client_farrow"
        if hasattr(st, "session_state") and cache_key in st.session_state:
            cached = st.session_state[cache_key]
            if cached is not None:
                return cached
    except Exception:
        st = None

    url, key = get_supabase_credentials()
    if not url or not key:
        return None

    try:
        from supabase import create_client
        client = create_client(url, key)
        if st is not None and hasattr(st, "session_state"):
            st.session_state["_supabase_client_farrow"] = client
        return client
    except Exception:
        return None


def _load_json_file(file_path: str) -> List[Dict[str, Any]]:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, list):
                    return d
        except Exception:
            pass
    return []


def _save_json_file(file_path: str, data: List[Dict[str, Any]]):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _fetch_user_blob(username: str) -> Dict[str, Any]:
    """Lấy dữ liệu blob của user từ Supabase."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = (
                client.table("user_histories")
                .select("data")
                .eq("username", username)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                blob = res.data[0].get("data") or {}
                if isinstance(blob, dict):
                    return blob
        except Exception:
            pass
    return {}


def _update_user_blob_field(username: str, field_name: str, value: Any) -> bool:
    """Cập nhật một trường trong blob user_histories của Supabase."""
    client = get_supabase_client()
    if client is not None:
        try:
            blob = _fetch_user_blob(username)
            blob["username"] = username
            blob[field_name] = value
            blob["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            client.table("user_histories").upsert({
                "username": username,
                "data": blob,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }).execute()
            return True
        except Exception:
            return False
    return False


# =============================================================================
# 1. QUẢN TRỊ MÁY QUÉT ĐỌC VỊ THẾ CUỘC (MACRO RADAR SCANS)
# =============================================================================
def load_macro_scans(username: str = "Phat") -> List[Dict[str, Any]]:
    blob = _fetch_user_blob(username)
    if "macro_radar_scans" in blob and isinstance(blob["macro_radar_scans"], list):
        scans = blob["macro_radar_scans"]
        _save_json_file(LOCAL_MACRO_FILE, scans)
        return scans
    return _load_json_file(LOCAL_MACRO_FILE)


def save_macro_scan(
    query_text: str,
    analysis_result: Dict[str, Any],
    username: str = "Phat"
) -> bool:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "id": f"scan_{int(datetime.now().timestamp() * 1000)}",
        "created_at": now_str,
        "query": query_text.strip(),
        "result": analysis_result
    }

    current_scans = load_macro_scans(username)
    updated_scans = [s for s in current_scans if s.get("query") != record["query"]]
    updated_scans.insert(0, record)
    if len(updated_scans) > 50:
        updated_scans = updated_scans[:50]

    _save_json_file(LOCAL_MACRO_FILE, updated_scans)
    return _update_user_blob_field(username, "macro_radar_scans", updated_scans)


def delete_macro_scan(scan_id: str, username: str = "Phat") -> bool:
    current_scans = load_macro_scans(username)
    updated_scans = [s for s in current_scans if s.get("id") != scan_id]
    _save_json_file(LOCAL_MACRO_FILE, updated_scans)
    return _update_user_blob_field(username, "macro_radar_scans", updated_scans)


# =============================================================================
# 1B. QUẢN TRỊ CÂY TRINH SÁT THỜI CUỘC (MACRO SCOUT TREES & MULTI-TIER CACHE)
# =============================================================================
def load_macro_scout_trees(username: str = "Phat") -> List[Dict[str, Any]]:
    """Tải toàn bộ cây trinh sát xu hướng F1 & F2 đã bóc tách từ Cloud hoặc local."""
    blob = _fetch_user_blob(username)
    if "macro_scout_trees" in blob and isinstance(blob["macro_scout_trees"], list):
        trees = blob["macro_scout_trees"]
        _save_json_file(LOCAL_SCOUT_TREES_FILE, trees)
        return trees
    return _load_json_file(LOCAL_SCOUT_TREES_FILE)


def save_macro_scout_tree(
    domain_name: str,
    scout_overview: str,
    trends: List[Dict[str, Any]],
    tree_id: Optional[str] = None,
    username: str = "Phat"
) -> Dict[str, Any]:
    """Lưu hoặc cập nhật một cây trinh sát thế cuộc (F0 -> F1 -> F2), bảo toàn các F2 đã soi sâu."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tid = tree_id if tree_id else f"tree_{int(datetime.now().timestamp() * 1000)}"

    current_trees = load_macro_scout_trees(username)
    existing = next((t for t in current_trees if t.get("id") == tid or t.get("domain", "").lower() == domain_name.strip().lower()), None)

    if existing:
        existing["updated_at"] = now_str
        existing["scout_overview"] = scout_overview
        # Giữ lại các nhánh F2 (drill_down) đã bóc tách trước đó nếu có
        existing_drill = {t.get("title"): t.get("drill_down") for t in existing.get("trends", []) if "drill_down" in t}
        for t in trends:
            if t.get("title") in existing_drill and "drill_down" not in t:
                t["drill_down"] = existing_drill[t.get("title")]
        existing["trends"] = trends
        record = existing
        updated_trees = [t if t.get("id") != existing.get("id") else existing for t in current_trees]
    else:
        record = {
            "id": tid,
            "created_at": now_str,
            "updated_at": now_str,
            "domain": domain_name.strip(),
            "scout_overview": scout_overview,
            "trends": trends
        }
        updated_trees = [t for t in current_trees if t.get("domain", "").lower() != domain_name.strip().lower()]
        updated_trees.insert(0, record)

    if len(updated_trees) > 30:
        updated_trees = updated_trees[:30]

    _save_json_file(LOCAL_SCOUT_TREES_FILE, updated_trees)
    _update_user_blob_field(username, "macro_scout_trees", updated_trees)
    return record


def update_tree_drilldown(
    tree_id: str,
    trend_rank: int,
    drill_down_data: Dict[str, Any],
    username: str = "Phat"
) -> bool:
    """Lưu trữ đệm kết quả bóc tách lớp 2/3 (F2) trực tiếp vào nhánh F1 tương ứng trong cây."""
    trees = load_macro_scout_trees(username)
    for t in trees:
        if t.get("id") == tree_id:
            for trend in t.get("trends", []):
                if trend.get("rank") == trend_rank:
                    trend["drill_down"] = drill_down_data
                    t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    _save_json_file(LOCAL_SCOUT_TREES_FILE, trees)
                    _update_user_blob_field(username, "macro_scout_trees", trees)
                    return True
    return False


def delete_macro_scout_tree(tree_id: str, username: str = "Phat") -> bool:
    """Xóa một cây trinh sát theo ID."""
    trees = load_macro_scout_trees(username)
    updated = [t for t in trees if t.get("id") != tree_id]
    _save_json_file(LOCAL_SCOUT_TREES_FILE, updated)
    return _update_user_blob_field(username, "macro_scout_trees", updated)



# =============================================================================
# 2. QUẢN TRỊ PHÂN RÃ VẤN ĐỀ 9 LĂNG KÍNH (PROBLEM ANALYSES)
# =============================================================================
def load_problem_analyses(username: str = "Phat") -> List[Dict[str, Any]]:
    blob = _fetch_user_blob(username)
    if "analyses" in blob and isinstance(blob["analyses"], list):
        analyses = blob["analyses"]
        _save_json_file(LOCAL_ANALYSES_FILE, analyses)
        return analyses
    return _load_json_file(LOCAL_ANALYSES_FILE)


def save_problem_analysis(
    problem_text: str,
    result_data: Dict[str, Any],
    username: str = "Phat"
) -> bool:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "id": f"ana_{int(datetime.now().timestamp() * 1000)}",
        "time": now_str,
        "created_at": now_str,
        "problem": problem_text.strip(),
        "summary": result_data.get("first_principles_breakdown", "")[:300],
        "full_result": result_data,
        "is_valid": result_data.get("is_valid", True),
    }

    current = load_problem_analyses(username)
    updated = [a for a in current if a.get("problem") != record["problem"]]
    updated.insert(0, record)
    if len(updated) > 50:
        updated = updated[:50]

    _save_json_file(LOCAL_ANALYSES_FILE, updated)
    return _update_user_blob_field(username, "analyses", updated)


def delete_problem_analysis(analysis_id: str, username: str = "Phat") -> bool:
    current = load_problem_analyses(username)
    updated = [a for a in current if a.get("id") != analysis_id]
    _save_json_file(LOCAL_ANALYSES_FILE, updated)
    return _update_user_blob_field(username, "analyses", updated)


# =============================================================================
# 3. QUẢN TRỊ NHẬT KÝ QUYẾT ĐỊNH (DECISION JOURNAL & SAI SỐ)
# =============================================================================
def get_user_decisions(username: str = "Phat") -> List[Dict[str, Any]]:
    blob = _fetch_user_blob(username)
    journal = []
    if "decision_journal" in blob and isinstance(blob["decision_journal"], list):
        journal = blob["decision_journal"]
    else:
        journal = _load_json_file(LOCAL_DECISIONS_FILE)

    today_str = date.today().isoformat()
    has_changes = False
    for item in journal:
        if item.get("status") == "pending":
            rev_date = item.get("review_date", "")
            if rev_date and rev_date <= today_str:
                item["status"] = "due"
                has_changes = True

    if has_changes:
        _save_json_file(LOCAL_DECISIONS_FILE, journal)
        _update_user_blob_field(username, "decision_journal", journal)

    return journal


def create_decision_entry(
    username: str = "Phat",
    title: str = "",
    category: str = "📈 Tài chính, Chứng khoán & Đầu tư",
    hypothesis: str = "",
    confidence_pct: int = 70,
    inversion_traps: str = "",
    second_order_consequences: str = "",
    review_days: int = 90,
    source_analysis: str = "",
    feynman_honesty_check: str = "",
) -> Dict[str, Any]:
    created_dt = date.today()
    review_dt = created_dt + timedelta(days=review_days)
    entry_id = f"DEC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    entry: Dict[str, Any] = {
        "id": entry_id,
        "title": title.strip(),
        "category": category,
        "created_at": created_dt.isoformat(),
        "review_date": review_dt.isoformat(),
        "review_days": review_days,
        "hypothesis": hypothesis.strip(),
        "confidence_pct": confidence_pct,
        "inversion_traps": inversion_traps.strip(),
        "second_order_consequences": second_order_consequences.strip(),
        "feynman_honesty_check": feynman_honesty_check.strip(),
        "source_analysis": source_analysis[:500] if source_analysis else "",
        "status": "pending",
        "reviewed_at": None,
        "actual_outcome": "",
        "outcome_score": None,
        "calibration_diff": None,
        "lessons_learned": "",
    }

    journal = get_user_decisions(username)
    journal.insert(0, entry)
    _save_json_file(LOCAL_DECISIONS_FILE, journal)
    _update_user_blob_field(username, "decision_journal", journal)
    return entry


def resolve_decision_review(
    username: str = "Phat",
    decision_id: str = "",
    actual_outcome: str = "",
    outcome_score: int = 80,
    lessons_learned: str = "",
) -> Optional[Dict[str, Any]]:
    journal = get_user_decisions(username)
    target = None
    for item in journal:
        if item.get("id") == decision_id:
            target = item
            break

    if not target:
        return None

    target["status"] = "reviewed"
    target["reviewed_at"] = date.today().isoformat()
    target["actual_outcome"] = actual_outcome.strip()
    target["outcome_score"] = outcome_score
    target["lessons_learned"] = lessons_learned.strip()

    conf = target.get("confidence_pct", 50)
    target["calibration_diff"] = abs(conf - outcome_score)

    _save_json_file(LOCAL_DECISIONS_FILE, journal)
    _update_user_blob_field(username, "decision_journal", journal)
    return target


def delete_decision_entry(username: str = "Phat", decision_id: str = "") -> bool:
    journal = get_user_decisions(username)
    updated = [d for d in journal if d.get("id") != decision_id]
    _save_json_file(LOCAL_DECISIONS_FILE, updated)
    return _update_user_blob_field(username, "decision_journal", updated)


def get_decision_summary_stats(username: str = "Phat") -> Dict[str, Any]:
    decisions = get_user_decisions(username)
    total = len(decisions)
    pending = sum(1 for d in decisions if d.get("status") == "pending")
    due = sum(1 for d in decisions if d.get("status") == "due")
    reviewed = [d for d in decisions if d.get("status") == "reviewed"]
    reviewed_count = len(reviewed)

    if reviewed:
        diffs = [d.get("calibration_diff", 0) for d in reviewed if d.get("calibration_diff") is not None]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        calibration_accuracy = max(0.0, round(100.0 - avg_diff, 1))
    else:
        calibration_accuracy = 0.0

    return {
        "total_logged": total,
        "pending_count": pending,
        "due_count": due,
        "reviewed_count": reviewed_count,
        "calibration_accuracy": calibration_accuracy,
        "decisions": decisions,
    }


# =============================================================================
# 4. QUẢN TRỊ MÁY ÉP FARROW 1-CLICK (COMPRESSIONS HISTORY)
# =============================================================================
def load_compression_history(username: str = "Phat") -> List[Dict[str, Any]]:
    """Tải lịch sử các bản nén từ Supabase Cloud hoặc local JSON."""
    blob = _fetch_user_blob(username)
    if "compressions" in blob and isinstance(blob["compressions"], list):
        comps = blob["compressions"]
        _save_json_file(LOCAL_COMPRESSIONS_FILE, comps)
        return comps
    return _load_json_file(LOCAL_COMPRESSIONS_FILE)


def save_compression_record(
    raw_text: str,
    result_data: Dict[str, Any],
    username: str = "Phat"
) -> bool:
    """Lưu một bản nén mới vào Supabase Cloud và local JSON."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = result_data.get("title", "Bản Nén Farrow")
    record = {
        "id": f"comp_{int(datetime.now().timestamp() * 1000)}",
        "created_at": now_str,
        "time": now_str,
        "title": title,
        "raw_text": raw_text.strip(),
        "summary": result_data.get("tagline", "")[:250],
        "result": result_data
    }

    current = load_compression_history(username)
    updated = [c for c in current if c.get("raw_text") != record["raw_text"]]
    updated.insert(0, record)
    if len(updated) > 50:
        updated = updated[:50]

    _save_json_file(LOCAL_COMPRESSIONS_FILE, updated)
    return _update_user_blob_field(username, "compressions", updated)


def delete_compression_record(record_id: str, username: str = "Phat") -> bool:
    """Xóa một bản nén theo ID khỏi Supabase Cloud và local JSON."""
    current = load_compression_history(username)
    updated = [c for c in current if c.get("id") != record_id]
    _save_json_file(LOCAL_COMPRESSIONS_FILE, updated)
    return _update_user_blob_field(username, "compressions", updated)

