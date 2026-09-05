# -*- coding: utf-8 -*-
"""Supabase client + helpers. Falls back to local JSON when not configured."""

from __future__ import annotations

import os
from typing import Any, Optional

import streamlit as st


def _secret(name: str, default: str = "") -> str:
    try:
        if name in st.secrets and st.secrets[name]:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return (os.getenv(name) or default).strip()


def is_supabase_enabled() -> bool:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_KEY") or _secret("SUPABASE_ANON_KEY") or _secret("SUPABASE_SERVICE_KEY")
    return bool(url and key)


def get_supabase():
    """Return supabase client or None if not configured / import fails.
    Cached on st.session_state when available.
    """
    cache_key = "_supabase_client"
    try:
        if cache_key in st.session_state:
            return st.session_state[cache_key]
    except Exception:
        pass

    if not is_supabase_enabled():
        return None
    try:
        from supabase import create_client
    except ImportError:
        return None

    url = _secret("SUPABASE_URL")
    key = (
        _secret("SUPABASE_SERVICE_KEY")
        or _secret("SUPABASE_KEY")
        or _secret("SUPABASE_ANON_KEY")
    )
    client = None
    try:
        client = create_client(url, key)
    except Exception:
        client = None

    try:
        st.session_state[cache_key] = client
    except Exception:
        pass
    return client


def supabase_status() -> dict[str, Any]:
    enabled = is_supabase_enabled()
    client = get_supabase() if enabled else None
    return {
        "configured": enabled,
        "connected": client is not None,
        "backend": "supabase" if client is not None else "local_json",
    }
