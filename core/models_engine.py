# -*- coding: utf-8 -*-
"""
Bộ Xử Lý Ma Trận Mô Hình & Nguyên Lý Tinh Hoa (Unified Farrow Latticework Engine)
Hợp nhất 88 Mô hình & 100 Nguyên lý về 3 Trụ Cột Farrow:
1. 🚪 SOI GỐC (First Principles, Bảo Toàn & Ranh Giới)
2. 🖥️ ĐỌC DÒNG (Dòng Chảy, Xác Suất, Hệ Thống & Động Lực)
3. 🪑 RA ĐÒN (Đòn Bẩy Bất Đối Xứng, Xúc Tác & Điểm Tựa)
"""

import json
import os
import random
from typing import Dict, List, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
UNIFIED_FILE = os.path.join(DATA_DIR, "unified_farrow_models.json")


def load_unified_farrow_catalog() -> List[Dict[str, Any]]:
    """Tải toàn bộ danh mục mô hình & nguyên lý tinh hoa đã làm sạch và hợp nhất."""
    if os.path.exists(UNIFIED_FILE):
        try:
            with open(UNIFIED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("catalog", [])
        except Exception:
            pass

    # Fallback to core_mental_models.json if unified file is missing
    fallback_path = os.path.join(DATA_DIR, "core_mental_models.json")
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f).get("models", [])
        except Exception:
            pass
    return []


def get_farrow_models_grouped() -> Dict[str, List[Dict[str, Any]]]:
    """Gom nhóm danh mục tinh hoa vào 3 Trụ Cột Farrow: root, flow, strike."""
    catalog = load_unified_farrow_catalog()
    grouped = {"root": [], "flow": [], "strike": []}
    for item in catalog:
        pillar = item.get("farrow_pillar", "root")
        if pillar not in grouped:
            pillar = "root"
        grouped[pillar].append(item)
    return grouped


def get_farrow_metrics() -> Dict[str, Any]:
    """Trả về các chỉ số thống kê tổng quan của ma trận tinh hoa."""
    catalog = load_unified_farrow_catalog()
    grouped = get_farrow_models_grouped()
    tier1 = [x for x in catalog if x.get("tier") == 1]
    return {
        "total": len(catalog),
        "tier1_count": len(tier1),
        "root_count": len(grouped["root"]),
        "flow_count": len(grouped["flow"]),
        "strike_count": len(grouped["strike"]),
    }


def draw_random_farrow_sprint_trio() -> List[Dict[str, Any]]:
    """Rút ngẫu nhiên 3 thẻ: 1 thẻ Soi Gốc, 1 thẻ Đọc Dòng, 1 thẻ Ra Đòn cho phiên 10 phút."""
    grouped = get_farrow_models_grouped()
    trio = []
    for k in ["root", "flow", "strike"]:
        pool = grouped[k]
        if pool:
            # Ưu tiên rút thẻ Tier 1 nếu có
            tier1_pool = [m for m in pool if m.get("tier") == 1]
            chosen = random.choice(tier1_pool if tier1_pool else pool)
            trio.append(chosen)
    return trio


# Backward compatibility aliases
def load_all_mental_models() -> List[Dict[str, Any]]:
    return load_unified_farrow_catalog()


def load_all_principles() -> List[Dict[str, Any]]:
    catalog = load_unified_farrow_catalog()
    return [x for x in catalog if x.get("source") in ["scientific_principle", "merged"]]


def get_farrow_principles_grouped() -> Dict[str, List[Dict[str, Any]]]:
    return get_farrow_models_grouped()


_MODELS_BY_ID: Optional[Dict[str, Dict[str, Any]]] = None

def get_all_models_map() -> Dict[str, Dict[str, Any]]:
    """Tải và lưu cache từ điển mô hình đầy đủ trường chi tiết GMM theo ID."""
    global _MODELS_BY_ID
    if _MODELS_BY_ID is not None:
        return _MODELS_BY_ID
    
    mapping: Dict[str, Dict[str, Any]] = {}
    
    # 1. Đọc từ core_mental_models.json (chứa đầy đủ action_steps, boundary_conditions, real_world_case)
    core_path = os.path.join(DATA_DIR, "core_mental_models.json")
    if os.path.exists(core_path):
        try:
            with open(core_path, "r", encoding="utf-8") as f:
                core_models = json.load(f).get("models", [])
                for m in core_models:
                    if "id" in m:
                        mapping[m["id"]] = m
        except Exception:
            pass

    # 2. Đọc bổ sung từ unified_farrow_models.json nếu có ID mới
    unified = load_unified_farrow_catalog()
    for item in unified:
        mid = item.get("id")
        if mid and mid not in mapping:
            mapping[mid] = item
            
    _MODELS_BY_ID = mapping
    return _MODELS_BY_ID


def get_model_full_detail(model_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết đầy đủ của một mô hình theo ID (gồm cả khung GMM chuyên sâu nếu có)."""
    m_map = get_all_models_map()
    return m_map.get(model_id)


def get_models_for_topic_chunk(chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Lấy danh sách 3 mô hình tương ứng cho 1 chunk (Trụ) của chủ đề Farrow."""
    model_ids = chunk.get("model_ids", [])
    models = []
    for mid in model_ids:
        m = get_model_full_detail(mid)
        if m:
            models.append(m)
        else:
            models.append({
                "id": mid,
                "name_vi": mid,
                "name_en": "",
                "tier": 1,
                "first_principle": chunk.get("principle", ""),
                "elite_leverage": "",
                "trigger_question": chunk.get("trigger_question", ""),
                "inversion_trap": "",
            })
    return models

