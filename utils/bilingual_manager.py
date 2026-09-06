# -*- coding: utf-8 -*-
"""
Bilingual Reader & Ultralearning Manager.
- Loads pre-processed parallel books (EN/VI).
- Manages High-Frequency Vocabulary tracking & Spaced Repetition (Active Recall).
- Powers the AI Feynman Explainer (No jargon grammar & First Principles of language).
- Seamlessly bridges insights into the Second Brain (pages/10_so_tay_tri_thuc.py).
"""

from __future__ import annotations

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st

from utils.knowledge import load_user_history, save_user_history
from utils.ai_engine import _normalize_keys, clean_json_response
from utils.notes_manager import create_note



DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "bilingual_books"
CACHE_DIR = DATA_DIR / "cache"


@st.cache_data(show_spinner=False)
def load_available_books() -> List[Dict[str, Any]]:
    """Scans data/bilingual_books/ and returns list of books."""
    books = []
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return books

    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name.startswith("cache_"):
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                books.append(data)
        except Exception as e:
            print(f"Error loading book {f}: {e}")
    return books


def _get_cache_file(book_id: str, chapter_id: Any) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"jit_{book_id}_ch{chapter_id}.json"


def load_chapter_jit_cache(book_id: str, chapter_id: Any) -> Dict[str, Any]:
    """Loads cached translations for a chapter."""
    c_path = _get_cache_file(book_id, chapter_id)
    if c_path.exists():
        try:
            with open(c_path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            return {}
    return {}


def save_chapter_jit_cache(book_id: str, chapter_id: Any, cache_data: Dict[str, Any]) -> None:
    """Saves translations into persistent cache file."""
    c_path = _get_cache_file(book_id, chapter_id)
    try:
        with open(c_path, "w", encoding="utf-8") as fp:
            json.dump(cache_data, fp, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving JIT cache: {e}")


def translate_paragraphs_batch(
    paragraphs: List[str],
    book_title: str = "Surely You're Joking, Mr. Feynman!",
    chapter_title: str = "",
    api_keys: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Translates a batch of English paragraphs into Vietnamese using Gemini.
    Follows Richard Feynman's vivid, precise, and conversational style.
    Returns: List of {"vi": "...", "vocab": [{"word": "...", "vi": "...", "nuance": "..."}]}
    """
    import google.generativeai as genai

    if not paragraphs:
        return []

    # Comprehensive key collection with fallback to all environment and secrets
    configured_keys = []
    if api_keys:
        configured_keys.extend(_normalize_keys(api_keys))

    # Also check env and secrets directly
    try:
        from utils.app_common import get_configured_api_keys
        configured_keys.extend(get_configured_api_keys())
    except Exception:
        pass

    for i in range(1, 10):
        v = os.environ.get(f"GEMINI_API_KEY_{i}") or os.environ.get(f"GEMINI_API_KEY")
        if v and v.strip():
            configured_keys.append(v.strip())
    if os.environ.get("GOOGLE_API_KEY"):
        configured_keys.append(os.environ.get("GOOGLE_API_KEY").strip())

    # Filter out genai v1 keys (AQ.*) and deduplicate
    keys = []
    seen = set()
    for k in configured_keys:
        if k and not k.startswith("AQ.") and k not in seen:
            seen.add(k)
            keys.append(k)

    prompt = f"""Bạn là dịch giả phong cách Richard Feynman kiêm chuyên gia sư phạm ngôn ngữ.
Nhiệm vụ của bạn là dịch nguyên bản 100% từng đoạn văn tiếng Anh sau đây sang tiếng Việt một cách mượt mà, sống động, chuẩn xác kỹ thuật và tự nhiên theo văn phong của Feynman.

Sách: {book_title}
Chương: {chapter_title}

DANH SÁCH {len(paragraphs)} ĐOẠN VĂN GỐC (JSON Array):
{json.dumps(paragraphs, ensure_ascii=False)}

YÊU CẦU ĐẦU RA BẮT BUỘC:
Trả về DUY NHẤT một JSON Array có đúng {len(paragraphs)} phần tử tương ứng theo thứ tự:
[
  {{
    "index": 0,
    "vi": "Bản dịch tiếng Việt chuẩn xác 100% của đoạn này",
    "key_vocab": [
      {{
        "word": "từ hoặc cụm từ hay/khó trong đoạn",
        "vi": "nghĩa ngắn gọn",
        "nuance": "sắc thái tự nhiên của từ"
      }}
    ]
  }}
]
"""

    candidates = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

    for key in keys:
        try:
            genai.configure(api_key=key)
            for cand in candidates:
                try:
                    model = genai.GenerativeModel(
                        model_name=cand,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    resp = model.generate_content(prompt, request_options={"timeout": 30})
                    if resp and resp.text:
                        raw_data = json.loads(clean_json_response(resp.text))
                        if isinstance(raw_data, list) and len(raw_data) == len(paragraphs):
                            return raw_data
                        elif isinstance(raw_data, list):
                            res_map = {item.get("index", idx): item for idx, item in enumerate(raw_data)}
                            return [res_map.get(idx, {"vi": "", "key_vocab": []}) for idx in range(len(paragraphs))]
                except Exception as ex:
                    print(f"Model {cand} on key {key[:8]} failed: {ex}")
                    continue
        except Exception as ex:
            print(f"Configuring key {key[:8]} failed: {ex}")
            continue

    # Fallback if offline/exhausted
    return [{"vi": "(Đang chờ kết nối API hoặc vượt hạn ngạch ngày - bạn có thể bấm nút Dịch lại bên dưới)", "key_vocab": []} for _ in paragraphs]



def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """Finds a book by its book_id."""
    books = load_available_books()
    for b in books:
        if b.get("book_id") == book_id:
            return b
    return None


def get_user_vocab_vault(username: str) -> Dict[str, Any]:
    """Retrieves user's vocabulary tracker from user history."""
    hist = load_user_history(username)
    vocab = hist.get("bilingual_vocab")
    if vocab is None:
        vocab = {}
        hist["bilingual_vocab"] = vocab
        save_user_history(username, hist)
    return vocab


def record_word_lookup(
    username: str,
    word: str,
    context_sentence: str = "",
    feynman_breakdown: str = "",
    vi_meaning: str = "",
    source_chapter: str = "",
) -> Dict[str, Any]:
    """
    Records or updates a looked-up word.
    Increments lookup_count. If lookup_count >= 2, flags as Target Drill (Blindspot).
    """
    clean_word = word.strip().lower()
    if not clean_word:
        return {}

    hist = load_user_history(username)
    vocab = hist.setdefault("bilingual_vocab", {})

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if clean_word in vocab:
        entry = vocab[clean_word]
        entry["count"] = entry.get("count", 1) + 1
        entry["updated_at"] = now_str
        if context_sentence and context_sentence not in entry.get("contexts", []):
            entry.setdefault("contexts", []).append(context_sentence)
        if feynman_breakdown and not entry.get("feynman_breakdown"):
            entry["feynman_breakdown"] = feynman_breakdown
        if vi_meaning and not entry.get("vi_meaning"):
            entry["vi_meaning"] = vi_meaning
    else:
        entry = {
            "word": clean_word,
            "count": 1,
            "created_at": now_str,
            "updated_at": now_str,
            "vi_meaning": vi_meaning,
            "feynman_breakdown": feynman_breakdown,
            "contexts": [context_sentence] if context_sentence else [],
            "source_chapter": source_chapter,
            "mastered": False,
        }
        vocab[clean_word] = entry

    # High frequency threshold for Ultralearning
    entry["is_target_drill"] = entry["count"] >= 2

    save_user_history(username, hist)
    return entry


def toggle_word_mastery(username: str, word: str) -> bool:
    """Toggles whether user has mastered a vocabulary item."""
    clean_word = word.strip().lower()
    hist = load_user_history(username)
    vocab = hist.setdefault("bilingual_vocab", {})
    if clean_word in vocab:
        vocab[clean_word]["mastered"] = not vocab[clean_word].get("mastered", False)
        save_user_history(username, hist)
        return vocab[clean_word]["mastered"]
    return False


def delete_word_from_vault(username: str, word: str) -> bool:
    """Removes a word from the user's vocabulary list."""
    clean_word = word.strip().lower()
    hist = load_user_history(username)
    vocab = hist.setdefault("bilingual_vocab", {})
    if clean_word in vocab:
        del vocab[clean_word]
        save_user_history(username, hist)
        return True
    return False


# -----------------------------------------------------------------------------
# AI Feynman Explainer Engine
# -----------------------------------------------------------------------------
FEYNMAN_PROMPT_TEMPLATE = """Bạn là Richard Feynman — nhà vật lý đạt giải Nobel kiêm bậc thầy sư phạm giảng giải mọi thứ bằng ngôn ngữ bình dân nhất.
Người đọc đang đọc cuốn sách tự truyện của bạn ("Surely You're Joking, Mr. Feynman!") và gặp một từ / cụm từ tiếng Anh khó.

CỤM TỪ CẦN GIẢI THÍCH: "{phrase}"
NGỮ CẢNH TRONG ĐOẠN VĂN:
\"\"\"{context}\"\"\"

Hãy phân tích theo Kỹ thuật Feynman cho người mới học tiếng Anh:
YÊU CẦU ĐẦU RA BẮT BUỘC BẰNG JSON HỢP LỆ (không markdown thừa):
{{
  "phrase": "{phrase}",
  "phonetic": "/phiên âm IPA nếu có/",
  "part_of_speech": "từ loại (noun, verb, idiom, phrasal verb...)",
  "vietnamese_meaning": "nghĩa tiếng Việt chuẩn xác nhất trong ngữ cảnh này",
  "root_nuance": "Bản chất nguyên lý gốc: Tại sao người bản xứ / Feynman lại dùng từ này mà không dùng từ khác? Hình ảnh ẩn dụ bên dưới là gì? (Giải thích giản dị như nói chuyện ngoài quán cà phê)",
  "grammar_breakdown": "Giải phẫu cú pháp: Cấu trúc câu, cách kết nối từ trong câu mà không dùng thuật ngữ ngữ pháp phức tạp",
  "real_life_examples": [
    {{"en": "Ví dụ 1 bằng tiếng Anh thực tế", "vi": "Bản dịch tiếng Việt"}},
    {{"en": "Ví dụ 2 bằng tiếng Anh thực tế", "vi": "Bản dịch tiếng Việt"}}
  ],
  "feynman_tip": "Mẹo siêu học nhớ lâu: Một câu ngắn gọn, hài hước để nhớ từ này mãi mãi"
}}
"""


def explain_phrase_feynman(
    phrase: str,
    context: str,
    model_choice: str = "gemini-2.5-flash",
    api_keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calls Gemini with the Feynman persona to dissect a phrase/sentence with multi-key failover."""
    import google.generativeai as genai

    keys = _normalize_keys(api_keys or os.environ.get("GOOGLE_API_KEY", ""))
    if not keys:
        # Fallback to .env keys
        env_keys = [os.environ.get(f"GEMINI_API_KEY_{i}") for i in range(1, 9)]
        keys = _normalize_keys([k for k in env_keys if k])

    prompt = FEYNMAN_PROMPT_TEMPLATE.format(phrase=phrase.strip(), context=context.strip())
    candidates = [model_choice, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

    for key in keys:
        try:
            genai.configure(api_key=key)
            for cand in candidates:
                try:
                    model = genai.GenerativeModel(
                        model_name=cand,
                        system_instruction="Bạn là Richard Feynman phân tích tiếng Anh theo nguyên lý khởi thủy và ngôn ngữ giản dị nhất.",
                        generation_config={"response_mime_type": "application/json"}
                    )
                    resp = model.generate_content(prompt, request_options={"timeout": 25})
                    if resp and resp.text:
                        data = json.loads(clean_json_response(resp.text))
                        return data
                except Exception:
                    continue
        except Exception:
            continue

    # Clean offline fallback if API keys unavailable or exhausted
    return {
        "phrase": phrase,
        "phonetic": "",
        "part_of_speech": "idiom / phrase",
        "vietnamese_meaning": f"Thuật ngữ trong ngữ cảnh: {phrase}",
        "root_nuance": f"'{phrase}' phản ánh cách nói tự nhiên của Feynman, mô tả hành động từ nguyên lý cơ bản nhất.",
        "grammar_breakdown": f"Trong đoạn văn trích: cụm từ giữ vai trò diễn đạt ý nòng cốt.",
        "real_life_examples": [
            {"en": f"He applied '{phrase}' to fix the issue.", "vi": f"Anh ấy đã ứng dụng '{phrase}' để xử lý vấn đề."}
        ],
        "feynman_tip": f"Hãy nhớ lại hoàn cảnh cậu bé Feynman giải quyết chiếc máy để nhớ từ '{phrase}' mãi mãi!",
        "is_offline": True
    }



def export_feynman_to_second_brain(
    username: str,
    phrase: str,
    explanation: Dict[str, Any],
    source_info: str = "Surely You're Joking, Mr. Feynman!",
) -> Dict[str, Any]:
    """Exports a Feynman vocab analysis directly into Second Brain (pages/10_so_tay_tri_thuc.py)."""
    title = f"Siêu Học Tiếng Anh: {phrase.title()} — {explanation.get('vietnamese_meaning', '')}"
    
    raw_content = f"""### 📖 HỌC TIẾNG ANH THEO PHƯƠNG PHÁP FEYNMAN
**Từ / Cụm từ:** `{phrase}` {explanation.get('phonetic', '')} ({explanation.get('part_of_speech', '')})
**Nguồn sách:** {source_info}

---
#### 1. Nghĩa ngữ cảnh:
> {explanation.get('vietnamese_meaning', '')}

#### 2. Bản chất nguyên lý gốc (Why this word?):
{explanation.get('root_nuance', '')}

#### 3. Giải phẫu cú pháp (Không thuật ngữ rườm rà):
{explanation.get('grammar_breakdown', '')}

#### 4. Ví dụ đời thực:
"""
    for ex in explanation.get("real_life_examples", []):
        raw_content += f"- **{ex.get('en', '')}**\n  ➔ *{ex.get('vi', '')}*\n"

    raw_content += f"\n💡 **Mẹo nhớ lâu (Feynman Tip):** {explanation.get('feynman_tip', '')}\n"

    decomposed_data = {
        "title": title,
        "domain": "🧠 Siêu nhận thức & Phương pháp học (Metacognition)",
        "essence": explanation.get("vietnamese_meaning", "") + " — " + explanation.get("root_nuance", "")[:120],
        "metaphor": explanation.get("feynman_tip", ""),
        "atomic_concepts": [
            f"Nghĩa từ vựng: {phrase}",
            "Nguyên lý dùng từ theo ngữ cảnh Feynman",
            "Ứng dụng phản xạ Active Recall"
        ],
        "mental_models_linked": [
            "Tư duy nguyên bản (First Principles Thinking)",
            "Vòng lặp phản hồi (Feedback Loop)"
        ],
        "first_principles_linked": [
            "Nguyên lý trừu tượng hóa tối giản",
            "Nguyên lý phản hồi chủ động"
        ],
        "actionable_steps": [
            f"Bước 1: Nhớ lại hình ảnh ẩn dụ của '{phrase}'.",
            "Bước 2: Tự đặt một câu tiếng Anh mới không nhìn tài liệu.",
            "Bước 3: Ôn lại sau 24h bằng bài tập điền từ Cloze Test."
        ],
        "traps_and_biases": "Bẫy học vẹt từ đơn lẻ không gắn với ngữ cảnh thực tế của câu chuyện.",
        "tags": ["feynman-reader", "english-vocab", "ultralearning", "second-brain"]
    }

    note = create_note(
        username=username,
        raw_content=raw_content,
        decomposed_data=decomposed_data,
        custom_title=title,
        note_type="feynman_vocab"
    )
    return note

