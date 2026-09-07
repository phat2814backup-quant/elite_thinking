# -*- coding: utf-8 -*-
"""
Hệ thống Quản lý Tri thức Sống & Lưu trữ Tài liệu Tham khảo (Living Knowledge & Reference Vault)
- Lưu trữ các phiên đối thoại / tài liệu dạng Markdown nguyên bản (zero-bloat)
- Quản lý phân phối tri thức sang:
  1. Lý thuyết Chuyên sâu 9 Chế độ (data/mode_deep_dives.json)
  2. Case Thực chiến Nhóm P (data/cases_practice_user.json)
  3. Gương soi Socratic & Sổ tay Phản tư (data/socratic_reflections.json)
- Chỉ Admin mới có quyền thêm, sửa, xóa, phân phối.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ARCHIVE_DIR = DATA_DIR / "practice_archive"
INDEX_FILE = ARCHIVE_DIR / "archive_index.json"
DEEP_DIVES_FILE = DATA_DIR / "mode_deep_dives.json"
CASES_PRACTICE_FILE = DATA_DIR / "cases_practice_user.json"
SOCRATIC_FILE = DATA_DIR / "socratic_reflections.json"

def _ensure_dirs():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def slugify(text: str) -> str:
    """Tạo slug an toàn từ tên file hoặc tiêu đề tiếng Việt."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text or "document"

# =============================================================================
# 1. KHO THAM KHẢO NGUYÊN BẢN (ARCHIVE ENGINE)
# =============================================================================

def list_archives() -> List[Dict[str, Any]]:
    """Liệt kê toàn bộ tài liệu Markdown trong kho tham khảo."""
    _ensure_dirs()
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_archive(archive_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết một tài liệu kèm nội dung Markdown đầy đủ."""
    items = list_archives()
    entry = next((item for item in items if item.get("id") == archive_id), None)
    if not entry:
        return None
    
    file_path = ARCHIVE_DIR / entry.get("filename", "")
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                entry["content"] = f.read()
        except Exception:
            entry["content"] = ""
    else:
        entry["content"] = ""
    return entry

def save_to_archive(
    content: str,
    original_filename: str,
    title: str = "",
    author: str = "Admin",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Lưu văn bản Markdown vào kho và cập nhật chỉ mục."""
    _ensure_dirs()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    base_name = Path(original_filename).stem if original_filename else "document"
    clean_slug = slugify(base_name)
    file_name = f"{date_prefix}_{clean_slug}.md"
    file_path = ARCHIVE_DIR / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    items = list_archives()
    doc_id = f"arch_{date_prefix}_{clean_slug}"
    doc_title = title.strip() if title else base_name.replace("_", " ").title()

    entry = {
        "id": doc_id,
        "title": doc_title,
        "filename": file_name,
        "original_filename": original_filename,
        "created_at": now_str,
        "created_by": author,
        "word_count": len(content.split()),
        "char_count": len(content),
        "tags": tags or ["Tham khảo", "Hội đồng Trí tuệ"],
        "promoted_to": []
    }
    items.insert(0, entry)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return entry

def delete_archive(archive_id: str) -> bool:
    """Xóa tài liệu khỏi kho tham khảo."""
    _ensure_dirs()
    items = list_archives()
    entry = next((item for item in items if item.get("id") == archive_id), None)
    if not entry:
        return False
    
    file_path = ARCHIVE_DIR / entry.get("filename", "")
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass
            
    items = [i for i in items if i.get("id") != archive_id]
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return True

# =============================================================================
# 2. LÝ THUYẾT CHUYÊN SÂU (MODE DEEP-DIVES)
# =============================================================================

def load_deep_dives() -> Dict[str, Any]:
    """Tải toàn bộ luận giải chuyên sâu cho 9 chế độ tư duy."""
    if not DEEP_DIVES_FILE.exists():
        return {}
    try:
        with open(DEEP_DIVES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_deep_dive(
    mode_code: str,
    title: str,
    quote: str,
    layers: Dict[str, str],
    source_ref: str = "",
    author: str = "Admin"
) -> bool:
    """Lưu hoặc cập nhật một luận giải chuyên sâu cho một chế độ tư duy."""
    data = load_deep_dives()
    data[mode_code] = {
        "mode_code": mode_code,
        "title": title,
        "quote": quote,
        "layers": layers,
        "source_ref": source_ref,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": author
    }
    with open(DEEP_DIVES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def delete_deep_dive(mode_code: str) -> bool:
    """Xóa luận giải chuyên sâu của một chế độ tư duy."""
    data = load_deep_dives()
    if mode_code in data:
        del data[mode_code]
        with open(DEEP_DIVES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False

# =============================================================================
# 3. CASE THỰC CHIẾN HỘI ĐỒNG (USER & COUNCIL PRACTICE CASES)
# =============================================================================

def load_practice_cases() -> Dict[str, Any]:
    """Tải các case thực chiến nhóm P."""
    if not CASES_PRACTICE_FILE.exists():
        return {
            "metadata": {
                "group": "P",
                "title": "Tình Huống Thực Chiến Của Hội Đồng (User & Council Practice)",
                "target_age": "Giới Elite, Nhà đầu tư & Cha mẹ",
                "description": "Các bài toán thực chiến do Hội đồng Trí tuệ tối cao phân rã từ các phiên tham vấn thực tế."
            },
            "cases": []
        }
    try:
        with open(CASES_PRACTICE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"metadata": {}, "cases": []}

def save_practice_case(case_item: Dict[str, Any]) -> bool:
    """Thêm hoặc cập nhật một case thực chiến."""
    data = load_practice_cases()
    cases = data.get("cases", [])
    case_id = case_item.get("id")
    
    idx = next((i for i, c in enumerate(cases) if c.get("id") == case_id), -1)
    if idx >= 0:
        cases[idx] = case_item
    else:
        cases.append(case_item)
        
    data["cases"] = cases
    with open(CASES_PRACTICE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def delete_practice_case(case_id: str) -> bool:
    """Xóa một case thực chiến theo ID."""
    data = load_practice_cases()
    cases = data.get("cases", [])
    new_cases = [c for c in cases if c.get("id") != case_id]
    if len(new_cases) != len(cases):
        data["cases"] = new_cases
        with open(CASES_PRACTICE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False

# =============================================================================
# 4. GƯƠNG SOI SOCRATIC (SOCRATIC REFLECTIONS & INQUIRY)
# =============================================================================

def load_socratic_reflections() -> List[Dict[str, Any]]:
    """Tải danh sách các câu hỏi tự vấn / gương soi Socratic."""
    if not SOCRATIC_FILE.exists():
        return []
    try:
        with open(SOCRATIC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_socratic_reflection(item: Dict[str, Any]) -> bool:
    """Thêm hoặc cập nhật câu hỏi tự vấn Socratic."""
    items = load_socratic_reflections()
    ref_id = item.get("id")
    idx = next((i for i, r in enumerate(items) if r.get("id") == ref_id), -1)
    if idx >= 0:
        items[idx] = item
    else:
        items.append(item)
    with open(SOCRATIC_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return True

def delete_socratic_reflection(ref_id: str) -> bool:
    """Xóa một câu hỏi tự vấn Socratic."""
    items = load_socratic_reflections()
    new_items = [r for r in items if r.get("id") != ref_id]
    if len(new_items) != len(items):
        with open(SOCRATIC_FILE, "w", encoding="utf-8") as f:
            json.dump(new_items, f, ensure_ascii=False, indent=2)
        return True
    return False
