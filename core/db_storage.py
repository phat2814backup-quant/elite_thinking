# -*- coding: utf-8 -*-
"""
Module Lưu Trữ Bền Vững (Cloud Supabase + Local JSON Fallback)
Hỗ trợ lưu trữ và truy xuất các bản phân tích Máy Quét Đọc Vị Thế Cuộc (AI Radar).
"""

from __future__ import annotations

import os
import json
import base64
from datetime import datetime
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

LOCAL_FALLBACK_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "macro_scans_history.json"
)

# Fallback credentials an toàn
_DEFAULT_URL = "https://szprfjzeauzstvmvgjrw.supabase.co"
_DEFAULT_KEY_B64 = (
    "ZXlKaGJHY2lPaUpJVXpJMVOaUlTk1SWVdSQ05Fa2lMQ0pwWVhRaU9pSktYMVRRSlNKOS5leUpwY3NJT2lK"
    "emRYSmtZV05sSUl3aWNtVmlJbk9pYzNwcWNtWnFld052Zkdod2JuSjNJaXdpY205c1pTSTZJbk5sY25acF"
    "kyVmZjbmxzWlNJSWZRRm1ZWFJmYjJ4bElpd2lhV0YwSUpveE56ZzROVGs0TlRFeUxDSmxlSEFpT2pJeE1E"
    "UXhOalExTVRjZlEuWkVjVlFsbFdSREpSZDAzbWRrMWhPRll3VEdSMmRteHNUa0pFUkhWb2EzSjJPVzg="
)


def get_supabase_credentials() -> tuple[str, str]:
    """Lấy URL và Key từ st.secrets, .env, os.environ hoặc fallback."""
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
        try:
            # Fallback service key
            key = (
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6cHJmanplYXV6c3R2bXZnanJ3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODU4ODUxNywiZXhwIjoyMTA0MTY0NTE3fQ."
                "oDdkRiCaGD3ljsUpqRJg8YZDANw7xvkSBDRuHh3KfOo"
            )
        except Exception:
            pass

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


def _load_local_scans() -> List[Dict[str, Any]]:
    """Tải lịch sử quét từ file JSON nội bộ."""
    if os.path.exists(LOCAL_FALLBACK_FILE):
        try:
            with open(LOCAL_FALLBACK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def _save_local_scans(scans: List[Dict[str, Any]]):
    """Lưu lịch sử quét ra file JSON nội bộ."""
    try:
        os.makedirs(os.path.dirname(LOCAL_FALLBACK_FILE), exist_ok=True)
        with open(LOCAL_FALLBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(scans, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_macro_scans(username: str = "Phat") -> List[Dict[str, Any]]:
    """
    Tải danh sách các lần quét thế cuộc từ Supabase user_histories.
    Nếu Supabase không sẵn sàng, tự động fallback sang local JSON.
    """
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
            rows = res.data or []
            if rows:
                blob = rows[0].get("data") or {}
                if isinstance(blob, dict) and "macro_radar_scans" in blob:
                    scans = blob.get("macro_radar_scans") or []
                    if isinstance(scans, list):
                        _save_local_scans(scans)
                        return scans
        except Exception:
            pass

    return _load_local_scans()


def save_macro_scan(
    query_text: str,
    analysis_result: Dict[str, Any],
    username: str = "Phat"
) -> bool:
    """
    Lưu một kết quả quét mới vào Supabase và đồng bộ file local JSON.
    Bản ghi mới nhất sẽ được đưa lên đầu danh sách.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "id": f"scan_{int(datetime.now().timestamp() * 1000)}",
        "created_at": now_str,
        "query": query_text.strip(),
        "result": analysis_result
    }

    # 1. Tải danh sách hiện tại
    current_scans = load_macro_scans(username)
    # Loại bỏ bản ghi trùng query nếu đã tồn tại trước đó để đưa lên đầu
    updated_scans = [s for s in current_scans if s.get("query") != record["query"]]
    updated_scans.insert(0, record)

    # Giữ tối đa 50 bản ghi gần nhất để tối ưu dung lượng
    if len(updated_scans) > 50:
        updated_scans = updated_scans[:50]

    # 2. Cập nhật Local JSON trước
    _save_local_scans(updated_scans)

    # 3. Cập nhật lên Supabase
    client = get_supabase_client()
    if client is not None:
        try:
            # Lấy data blob hiện tại của user để không làm mất các trường khác
            res = (
                client.table("user_histories")
                .select("data")
                .eq("username", username)
                .limit(1)
                .execute()
            )
            current_data = {}
            if res.data and len(res.data) > 0:
                current_data = res.data[0].get("data") or {}
            
            current_data["username"] = username
            current_data["macro_radar_scans"] = updated_scans
            current_data["updated_at"] = now_str

            client.table("user_histories").upsert({
                "username": username,
                "data": current_data,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }).execute()
            return True
        except Exception as e:
            print("Lỗi lưu Supabase:", e)
            return False

    return True


def delete_macro_scan(scan_id: str, username: str = "Phat") -> bool:
    """Xóa một bản ghi quét khỏi danh sách."""
    current_scans = load_macro_scans(username)
    updated_scans = [s for s in current_scans if s.get("id") != scan_id]

    _save_local_scans(updated_scans)

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
            current_data = {}
            if res.data and len(res.data) > 0:
                current_data = res.data[0].get("data") or {}
            
            current_data["macro_radar_scans"] = updated_scans
            current_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            client.table("user_histories").upsert({
                "username": username,
                "data": current_data,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }).execute()
            return True
        except Exception:
            return False

    return True
