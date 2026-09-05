# -*- coding: utf-8 -*-
"""
Module Elite Knowledge Vault & Second Brain (Sổ Tay Tri Thức Đa Chiều).
Quản lý ghi chú nguyên tử (Atomic Notes), mạng lưới liên kết chéo (Zettelkasten Latticework),
phân rã nhận thức, và ôn tập chủ động (Active Recall).
"""

from __future__ import annotations

import re
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

from pathlib import Path
from utils.knowledge import (
    load_user_history,
    save_user_history,
    load_knowledge_base,
    get_principles,
)

try:
    import google.generativeai as genai
except Exception:
    genai = None

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_FILE = DATA_DIR / "core_mental_models.json"


def get_all_models() -> List[Dict[str, Any]]:
    """Tải trực tiếp danh sách 88 mô hình từ core_mental_models.json."""
    if not MODELS_FILE.exists():
        return []
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("models", [])
    except Exception:
        return []

# Danh mục Lĩnh vực Tri thức Chuẩn mực
NOTE_DOMAINS = [
    "🧠 Siêu nhận thức & Phương pháp học (Metacognition)",
    "📈 Đầu tư, Chứng khoán & Trading",
    "💼 Quản trị, Lãnh đạo & Ra quyết định",
    "🤖 Công nghệ AI & Khoa học Máy tính",
    "🧬 Khoa học Não bộ & Sinh học",
    "🧘 Triết học, Tâm thức & Nhân sinh",
    "🎲 Xác suất, Toán học & Hệ thống phức hợp",
    "🌱 Thói quen & Phát triển cá nhân",
    "📦 Khác (Tổng quát)",
]

# Ghi chú mẫu kinh điển: Kỹ thuật Feynman
DEFAULT_FEYNMAN_NOTE: Dict[str, Any] = {
    "id": "NOTE-FEYNMAN-TECHNIQUE",
    "title": "Kỹ thuật Feynman (Feynman Technique) — Giải thích bình dân & Khắc phục điểm mù nhận thức",
    "created_at": "2026-09-05 20:00:00",
    "updated_at": "2026-09-05 20:00:00",
    "domain": "🧠 Siêu nhận thức & Phương pháp học (Metacognition)",
    "essence": "Thực sự hiểu một khái niệm là khi có thể giải thích trôi chảy cho một đứa trẻ 10 tuổi bằng ngôn ngữ đời thường; bất kỳ chỗ nào bị nghẹn hoặc phải dùng từ chuyên môn đều là điểm mù nhận thức cần quay lại tài liệu gốc để vá lỗi.",
    "metaphor": "Bộ não là chiếc máy tiêu hóa, tri thức sách vở là miếng thịt dai nhiều xương. Kỹ thuật Feynman là việc nhai nát miếng thịt thành món súp dễ nuốt đến mức đứa trẻ 10 tuổi cũng hấp thu được.",
    "atomic_concepts": [
        "Dạy lại cho trẻ 10 tuổi (Giản lược hóa ngôn ngữ về mức cơ bản, loại bỏ hoàn toàn thuật ngữ đao to búa lớn)",
        "Bắt quả tang điểm nghẽn (Phát hiện điểm mù khi ngập ngừng hoặc phải lấp liếm bằng từ 'đại loại là')",
        "Nấu lại món súp / Vá lỗi (Quay về tài liệu gốc để học lại chính xác khúc bị vấp và gắn vào ví dụ đời thường)",
        "Kiểm định trôi chảy (Active Recall & Phản xạ giải thích thông suốt để biến kiến thức thành sở hữu vĩnh viễn)"
    ],
    "mental_models_linked": [
        "Tư duy nguyên bản (First Principles Thinking)",
        "Ảo tưởng giải thích sâu (Illusion of Explanatory Depth)",
        "Tư duy đảo ngược (Inversion)",
        "Vòng lặp phản hồi (Feedback Loop)"
    ],
    "first_principles_linked": [
        "Nguyên lý trừu tượng hóa tối giản",
        "Nguyên lý phản hồi chủ động",
        "Định luật bảo toàn chân lý"
    ],
    "actionable_steps": [
        "Bước 1: Chọn một khái niệm mục tiêu bạn muốn thấu hiểu tận gốc.",
        "Bước 2: Tưởng tượng đang nói chuyện với một đứa trẻ 10 tuổi; giải thích bằng từ ngữ bình dân ngoài quán cà phê, không dùng biệt ngữ chuyên ngành.",
        "Bước 3: Bắt quả tang chỗ bị nghẹn — ghi nhận chính xác đoạn nào bạn lúng túng hoặc phải viện đến sách vở.",
        "Bước 4: Mở sách vá lỗi đúng khúc đó, tìm ví dụ đời thường gắn vào và giải thích lại cho đến khi trôi chảy."
    ],
    "traps_and_biases": "Ảo tưởng ghi nhớ (Confusing familiarity with understanding) — nhớ mặt chữ hoặc thuộc lòng thuật ngữ nhưng không thực sự hiểu cơ chế bên dưới.",
    "tags": ["feynman", "metacognition", "first-principles", "learning-technique", "active-recall", "feedback-loop"],
    "study_questions": [
        {
            "question": "Dấu hiệu rõ nhất cho thấy bạn đang 'học vẹt' thay vì thực sự thấu hiểu một khái niệm là gì?",
            "answer": "Khi được yêu cầu giải thích cho người không cùng ngành, bạn bị nghẹn lại hoặc buộc phải dùng đúng các thuật ngữ nguyên văn trong sách vở mà không diễn đạt được bằng ngôn ngữ đời thường."
        },
        {
            "question": "Hình tượng 'miếng thịt dai và món súp' trong kỹ thuật Feynman thể hiện nguyên lý tư duy nào?",
            "answer": "Thể hiện nguyên lý phân rã (First Principles) và trừu tượng hóa: bóc tách kiến thức phức tạp nhiều xương xẩu thành các thành phần nguyên tử dinh dưỡng, dễ tiêu hóa."
        }
    ],
    "cross_topic_connections": "Áp dụng trong Trading (giải thích chiến lược quản trị rủi ro cho người mới), trong Lãnh đạo doanh nghiệp (truyền thông tầm nhìn dự án minh bạch), và trong việc dạy con tư duy độc lập.",
    "favorite": True,
    "mastery_level": 3,
    "raw_content": """Đây là một bài toán mang tính "meta" rất thú vị. Để áp dụng chính Kỹ thuật Feynman vào việc giải thích Kỹ thuật Feynman, tôi sẽ gạt bỏ mọi từ ngữ có vẻ nguy hiểm như "ảo tưởng nhận thức", "tư duy nguyên bản", hay "củng cố trí nhớ".

Dưới đây là Kỹ thuật Feynman, được giải thích theo phong cách Feynman:

### Bước 1: Mục tiêu
Tôi muốn giải thích cho bạn: **Kỹ thuật Feynman là cái gì?**

### Bước 2: Dạy lại cho một đứa trẻ
Hãy tưởng tượng bộ não của bạn là một chiếc máy tiêu hóa, và những kiến thức trong sách vở là một miếng thịt rất dai và nhiều xương.
Nhiều người nghĩ rằng cứ nuốt chửng miếng thịt đó (học thuộc lòng từng chữ) là xong. Nhưng thực ra dạ dày họ không tiêu hóa được.
Kỹ thuật Feynman là việc bạn ép bản thân phải "nhai" miếng thịt đó cho thật nát, nhằn hết xương rườm rà ra, biến nó thành món súp dễ nuốt đến mức một đứa trẻ 10 tuổi hay bà ngoại của bạn cũng có thể "ăn" và hiểu được ngon lành.
Cách làm rất dễ: Hãy tưởng tượng một người không biết gì ngồi trước mặt bạn. Bạn hãy nói thành tiếng, kể lại cái bạn vừa học bằng ngôn ngữ ngoài quán cà phê, tuyệt đối không được dùng "từ ngữ chuyên ngành" có trong sách.

### Bước 3: Phát hiện chỗ bị "nghẹn" (Tìm điểm mù)
Trong lúc bạn đang hào hứng chém gió, đột nhiên bạn khựng lại. Bạn lúng túng, vò đầu bứt tai: *"Ờ... cái khúc này nó đại loại là... chà, nói sao cho dễ hiểu nhỉ? Thôi cứ biết là sách nó viết vậy đi!"*
Bùm! Bạn vừa bắt quả tang chính mình.
Chỗ mà bạn bị tắc, phải dùng những từ như "đại loại là", hoặc phải lôi từ khóa trong sách ra đọc nguyên xi... chính là cục xương bạn chưa nhai nát. Thực tế là bạn không hề hiểu đoạn đó, bạn chỉ đang nhớ mặt chữ của nó mà thôi.

### Bước 4: Nấu lại món súp (Vá lỗi)
Giờ thì bạn biết mình yếu ở đâu rồi. Bạn chỉ cần mở sách ra, đọc lại đúng cái khúc mà bạn vừa vấp ngã. Tìm hiểu nó thật kỹ, tìm một ví dụ đời thường để gắn nó vào.
Sau đó, bạn đóng sách lại, và thử giải thích lại đoạn đó một lần nữa. Cho đến khi nào bạn nói trôi chảy từ đầu đến cuối mà người nghe gật gù *"À, ra thế!"*, thì xin chúc mừng: Kiến thức đó đã vĩnh viễn thuộc về bạn.

---
> **Bản chất của Kỹ thuật Feynman (đã được tối giản):**
> Đừng tự lừa mình bằng việc học vẹt những từ ngữ phức tạp. Bạn chỉ thực sự hiểu một vấn đề khi bạn có thể kể lại nó bằng những từ ngữ bình dân nhất mà không bị vấp. Nếu vấp ở đâu, mở sách ra học lại đúng chỗ đó."""
}


def heuristic_decompose_note(raw_content: str, title_hint: str = "") -> Dict[str, Any]:
    """
    Thuật toán Heuristic cục bộ bóc tách ghi chú khi offline hoặc không có API Key.
    Tự động trích xuất cấu trúc nguyên tử dựa trên phân tích văn bản và so khớp với kho 88 mô hình và 100 nguyên lý.
    """
    lines = [ln.strip() for ln in raw_content.splitlines() if ln.strip()]
    content_lower = raw_content.lower()

    # 1. Trích xuất Tiêu đề
    title = title_hint.strip()
    if not title:
        for ln in lines:
            if ln.startswith("# ") or ln.startswith("## "):
                title = re.sub(r"^#+\s*", "", ln).strip()
                break
            if len(ln) < 80 and not ln.startswith(">"):
                title = ln
                break
        if not title:
            title = f"Ghi chú Tri thức #{datetime.now().strftime('%Y%m%d_%H%M')}"

    # 2. Nhận diện Lĩnh vực bằng chấm điểm tần suất từ khóa
    domain = "📦 Khác (Tổng quát)"
    domain_keywords = {
        "📈 Đầu tư, Chứng khoán & Trading": ["trading", "chứng khoán", "cổ phiếu", "lãi kép", "rủi ro", "thị trường", "vị thế", "kelly", "smart money", "dòng tiền", "vốn", "forex", "crypto"],
        "🧠 Siêu nhận thức & Phương pháp học (Metacognition)": ["feynman", "học tập", "phương pháp học", "siêu nhận thức", "nhận thức", "trí nhớ", "bộ não", "tư duy", "hiểu sâu", "điểm mù", "ôn tập", "active recall", "phản xạ"],
        "💼 Quản trị, Lãnh đạo & Ra quyết định": ["quản trị", "lãnh đạo", "chiến lược", "nhân sự", "đàm phán", "mục tiêu", "dự án", "quyết định", "tối ưu hóa"],
        "🤖 Công nghệ AI & Khoa học Máy tính": ["ai", "mô hình ngôn ngữ", "llm", "thuật toán", "dữ liệu", "prompt", "code", "mã nguồn", "phần mềm", "tự động hóa"],
        "🧬 Khoa học Não bộ & Sinh học": ["dopamine", "noradrenaline", "thần kinh", "sinh học", "tiến hóa", "gen", "tế bào", "thích nghi"],
        "🧘 Triết học, Tâm thức & Nhân sinh": ["vô thường", "chánh niệm", "stoic", "khắc kỷ", "tâm thức", "thiền", "bình thản", "hạnh phúc", "ý nghĩa cuộc sống"],
        "🎲 Xác suất, Toán học & Hệ thống phức hợp": ["xác suất", "bayes", "gaussian", "power law", "entropy", "feedback loop", "hệ thống phức hợp", "phi tuyến"],
    }
    best_domain = "📦 Khác (Tổng quát)"
    max_score = 0
    for dom, kws in domain_keywords.items():
        score = sum(content_lower.count(kw) for kw in kws)
        if score > max_score:
            max_score = score
            best_domain = dom
    if max_score > 0:
        domain = best_domain

    # 3. Trích xuất Bản chất (Essence) & Ẩn dụ (Metaphor)
    essence = ""
    for ln in lines:
        if any(marker in ln.lower() for marker in ["bản chất", "tóm lại", "cốt lõi", "mấu chốt"]):
            essence = re.sub(r"^[#>*\-\s:]*", "", ln).strip()
            break
    if not essence and lines:
        essence = lines[0][:200]

    metaphor = ""
    for ln in lines:
        if any(m in ln.lower() for m in ["tưởng tượng", "ví như", "giống như", "món súp", "miếng thịt", "chiếc xe", "con thuyền"]):
            metaphor = ln[:250]
            break

    # 4. Trích xuất Các bước hành động (Actionable Steps)
    steps = []
    step_pattern = re.compile(r"^(bước\s*\d+|step\s*\d+|\d+\.)\s*[:\-\.]?\s*(.*)", re.IGNORECASE)
    for ln in lines:
        m = step_pattern.match(ln)
        if m:
            clean_step = re.sub(r"^[#>*\-\s]*", "", ln).strip()
            steps.append(clean_step)
    if not steps:
        steps = [
            "Bước 1: Xác định khái niệm hoặc vấn đề cốt lõi cần đào sâu.",
            "Bước 2: Phân rã vấn đề thành các yếu tố nguyên tử độc lập.",
            "Bước 3: Kiểm định tính nhất quán và ứng dụng vào thực tiễn."
        ]

    # 5. So khớp Mạng lưới: 88 Mô hình tư duy
    matched_models = []
    all_models = get_all_models()
    for m in all_models:
        m_name = m.get("name_vi", "").lower()
        m_en = m.get("name_en", "").lower()
        if (m_name and m_name in content_lower) or (m_en and m_en in content_lower):
            matched_models.append(f"{m.get('name_vi')} ({m.get('name_en', '')})")
    if not matched_models:
        if "feynman" in content_lower or "nguyên bản" in content_lower:
            matched_models = ["Tư duy nguyên bản (First Principles Thinking)", "Ảo tưởng giải thích sâu (Illusion of Explanatory Depth)"]

    # 6. So khớp Mạng lưới: 100 Nguyên lý đệ nhất
    matched_principles = []
    for p in get_principles():
        p_name = str(p.get("principle_name", "")).lower()
        if p_name and p_name in content_lower:
            matched_principles.append(p.get("principle_name"))
        if len(matched_principles) >= 3:
            break

    # 7. Trích xuất Tags
    tags = set()
    for word in re.findall(r"\b[a-z0-9_À-ỹ\-]{4,20}\b", content_lower):
        if word in ["feynman", "tư duy", "nguyên lý", "học tập", "trading", "đầu tư", "ai", "mô hình", "não bộ", "xác suất", "chiến lược", "phản biện", "tối giản"]:
            tags.add(word)
    if not tags:
        tags = {"ghi-chu", "tri-thuc", "atomic-note"}

    return {
        "title": title,
        "domain": domain,
        "essence": essence[:300] if essence else "Đúc kết tri thức cốt lõi thông qua phân rã đa chiều.",
        "metaphor": metaphor,
        "atomic_concepts": [
            "Khái niệm mục tiêu độc lập cần nắm bắt",
            "Cơ chế vận hành bên dưới của hiện tượng",
            "Điểm mù nhận thức cần chủ động loại bỏ"
        ],
        "mental_models_linked": matched_models[:5],
        "first_principles_linked": matched_principles[:4],
        "actionable_steps": steps[:6],
        "traps_and_biases": "Ảo tưởng nhận thức (Illusion of competence) — nhầm lẫn giữa việc nhận diện mặt chữ với việc thực sự hiểu bản chất.",
        "tags": sorted(list(tags))[:8],
        "study_questions": [
            {
                "question": f"Làm thế nào để ứng dụng '{title}' vào việc giải quyết bài toán thực tế?",
                "answer": "Áp dụng theo các bước hành động cụ thể, tìm ví dụ tương đồng và đối chiếu với phản hồi thực nghiệm."
            }
        ],
        "cross_topic_connections": "Có thể kết hợp với các nguyên lý đệ nhất và mô hình xác suất để tối ưu hóa quyết định trong đời sống và đầu tư."
    }


def ensure_user_notes_initialized(username: str) -> List[Dict[str, Any]]:
    """Đảm bảo kho ghi chú của người dùng đã được khởi tạo, tự động nạp bài Feynman mẫu nếu kho còn trống."""
    hist = load_user_history(username)
    notes = hist.get("knowledge_notes")
    if notes is None:
        notes = [dict(DEFAULT_FEYNMAN_NOTE)]
        hist["knowledge_notes"] = notes
        save_user_history(username, hist)
    return notes


def get_user_notes(username: str) -> List[Dict[str, Any]]:
    """Lấy danh sách ghi chú của người dùng, sắp xếp theo thời gian cập nhật mới nhất."""
    notes = ensure_user_notes_initialized(username)
    return sorted(notes, key=lambda n: n.get("updated_at", n.get("created_at", "")), reverse=True)


def get_note_by_id(username: str, note_id: str) -> Optional[Dict[str, Any]]:
    """Tìm một ghi chú theo ID."""
    notes = get_user_notes(username)
    for n in notes:
        if n.get("id") == note_id:
            return n
    return None


def create_note(
    username: str,
    raw_content: str,
    decomposed_data: Dict[str, Any],
    custom_title: str = "",
) -> Dict[str, Any]:
    """Tạo một ghi chú mới và lưu vào Second Brain."""
    hist = load_user_history(username)
    notes = hist.setdefault("knowledge_notes", [])

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note_id = f"NOTE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    title = custom_title.strip() or decomposed_data.get("title") or "Ghi chú Tri thức Mới"

    new_note: Dict[str, Any] = {
        "id": note_id,
        "title": title,
        "created_at": now_str,
        "updated_at": now_str,
        "domain": decomposed_data.get("domain", "📦 Khác (Tổng quát)"),
        "essence": decomposed_data.get("essence", ""),
        "metaphor": decomposed_data.get("metaphor", ""),
        "atomic_concepts": decomposed_data.get("atomic_concepts", []),
        "mental_models_linked": decomposed_data.get("mental_models_linked", []),
        "first_principles_linked": decomposed_data.get("first_principles_linked", []),
        "actionable_steps": decomposed_data.get("actionable_steps", []),
        "traps_and_biases": decomposed_data.get("traps_and_biases", ""),
        "tags": [t.strip().lower() for t in decomposed_data.get("tags", []) if t.strip()],
        "study_questions": decomposed_data.get("study_questions", []),
        "cross_topic_connections": decomposed_data.get("cross_topic_connections", ""),
        "favorite": False,
        "mastery_level": 1,
        "raw_content": raw_content.strip(),
    }

    notes.insert(0, new_note)
    save_user_history(username, hist)
    return new_note


def update_note(
    username: str,
    note_id: str,
    updated_fields: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Cập nhật các trường thông tin của một ghi chú."""
    hist = load_user_history(username)
    notes = hist.setdefault("knowledge_notes", [])

    target = None
    for n in notes:
        if n.get("id") == note_id:
            target = n
            break

    if not target:
        return None

    for k, v in updated_fields.items():
        if k != "id":
            target[k] = v

    target["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_history(username, hist)
    return target


def delete_note(username: str, note_id: str) -> bool:
    """Xóa một ghi chú khỏi Second Brain."""
    hist = load_user_history(username)
    notes = hist.get("knowledge_notes", [])
    new_notes = [n for n in notes if n.get("id") != note_id]
    if len(new_notes) != len(notes):
        hist["knowledge_notes"] = new_notes
        save_user_history(username, hist)
        return True
    return False


def toggle_favorite(username: str, note_id: str) -> bool:
    """Chuyển đổi trạng thái yêu thích của ghi chú."""
    note = get_note_by_id(username, note_id)
    if note:
        new_fav = not note.get("favorite", False)
        update_note(username, note_id, {"favorite": new_fav})
        return new_fav
    return False


def update_mastery(username: str, note_id: str, level: int) -> bool:
    """Cập nhật độ nhuần nhuyễn của ghi chú (1: Mới lưu, 2: Đang rèn, 3: Đã nhuần nhuyễn)."""
    if 1 <= level <= 3:
        update_note(username, note_id, {"mastery_level": level})
        return True
    return False


def search_notes(
    username: str,
    query: str = "",
    domain: str = "Tất cả",
    mental_model: str = "Tất cả",
    tag: str = "Tất cả",
    only_favorites: bool = False,
    mastery_filter: str = "Tất cả",
) -> List[Dict[str, Any]]:
    """Tìm kiếm và lọc ghi chú theo nhiều chiều kích."""
    notes = get_user_notes(username)
    results = []

    q = query.lower().strip()

    for n in notes:
        # Lọc yêu thích
        if only_favorites and not n.get("favorite", False):
            continue

        # Lọc Mastery
        if mastery_filter != "Tất cả":
            lvl_map = {"🌱 Mới lưu": 1, "🔥 Đang rèn luyện": 2, "👑 Đã nhuần nhuyễn": 3}
            req_lvl = lvl_map.get(mastery_filter)
            if req_lvl and n.get("mastery_level", 1) != req_lvl:
                continue

        # Lọc Domain
        if domain != "Tất cả" and n.get("domain") != domain:
            continue

        # Lọc Mental Model
        if mental_model != "Tất cả":
            m_links = [m.lower() for m in n.get("mental_models_linked", [])]
            if not any(mental_model.lower() in ml for ml in m_links):
                continue

        # Lọc Tag
        if tag != "Tất cả":
            tags = [t.lower() for t in n.get("tags", [])]
            if tag.lower() not in tags:
                continue

        # Tìm kiếm từ khóa full-text
        if q:
            searchable_text = " ".join([
                str(n.get("title", "")),
                str(n.get("essence", "")),
                str(n.get("metaphor", "")),
                str(n.get("raw_content", "")),
                str(n.get("traps_and_biases", "")),
                " ".join(n.get("atomic_concepts", [])),
                " ".join(n.get("tags", [])),
                " ".join(n.get("mental_models_linked", [])),
            ]).lower()
            if q not in searchable_text:
                continue

        results.append(n)

    return results


def find_related_notes(username: str, current_note_id: str, limit: int = 5) -> List[Tuple[Dict[str, Any], int, List[str]]]:
    """
    Tìm các ghi chú liên quan trong Second Brain dựa trên:
    - Điểm trùng lặp Tags
    - Điểm trùng lặp Mental Models
    - Cùng Lĩnh vực (Domain)
    Trả về danh sách (note, similarity_score, common_elements).
    """
    notes = get_user_notes(username)
    target = None
    for n in notes:
        if n.get("id") == current_note_id:
            target = n
            break

    if not target:
        return []

    target_tags = set(t.lower() for t in target.get("tags", []))
    target_models = set(m.lower() for m in target.get("mental_models_linked", []))
    target_domain = target.get("domain", "")

    related = []
    for n in notes:
        if n.get("id") == current_note_id:
            continue

        score = 0
        common_reasons = []

        # So sánh tags
        n_tags = set(t.lower() for t in n.get("tags", []))
        shared_tags = target_tags.intersection(n_tags)
        if shared_tags:
            score += len(shared_tags) * 3
            common_reasons.append(f"Chung tag: {', '.join(list(shared_tags)[:3])}")

        # So sánh Mental Models
        n_models = set(m.lower() for m in n.get("mental_models_linked", []))
        shared_models = target_models.intersection(n_models)
        if shared_models:
            score += len(shared_models) * 5
            common_reasons.append(f"Chung mô hình: {len(shared_models)} mô hình")

        # So sánh Domain
        if target_domain and n.get("domain") == target_domain:
            score += 2
            common_reasons.append("Chung lĩnh vực")

        if score > 0:
            related.append((n, score, common_reasons))

    # Sắp xếp theo độ tương quan cao nhất
    related.sort(key=lambda item: item[1], reverse=True)
    return related[:limit]


def get_all_vault_tags(username: str) -> List[str]:
    """Lấy danh sách tất cả các tag duy nhất trong kho ghi chú của người dùng."""
    notes = get_user_notes(username)
    all_tags = set()
    for n in notes:
        for t in n.get("tags", []):
            if t.strip():
                all_tags.add(t.strip().lower())
    return sorted(list(all_tags))


def get_all_vault_models(username: str) -> List[str]:
    """Lấy danh sách tất cả các Mô hình tư duy đã được liên kết trong kho ghi chú."""
    notes = get_user_notes(username)
    all_models = set()
    for n in notes:
        for m in n.get("mental_models_linked", []):
            if m.strip():
                all_models.add(m.strip())
    return sorted(list(all_models))


def get_random_flashcards(username: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Rút các flashcard ngẫu nhiên từ toàn bộ kho ghi chú để phục vụ Active Recall."""
    import random
    notes = get_user_notes(username)
    cards = []
    for n in notes:
        q_list = n.get("study_questions", [])
        for q in q_list:
            cards.append({
                "note_id": n.get("id"),
                "note_title": n.get("title"),
                "domain": n.get("domain"),
                "question": q.get("question"),
                "answer": q.get("answer"),
                "essence": n.get("essence"),
            })
    if not cards:
        return []
    random.shuffle(cards)
    return cards[:limit]


def export_notes_to_markdown(username: str) -> str:
    """Xuất toàn bộ kho ghi chú sang định dạng Markdown Zettelkasten chuẩn (tương thích Obsidian / Logseq)."""
    notes = get_user_notes(username)
    out = [
        "# KHO TRI THỨC SECOND BRAIN — ELITE THINKING",
        f"*Người dùng:* `{username}` | *Ngày xuất:* `{datetime.now().strftime('%Y-%m-%d %H:%M')}`",
        "---"
    ]

    for n in notes:
        tags_str = " ".join([f"#{t}" for t in n.get("tags", [])])
        models_str = ", ".join([f"[[{m}]]" for m in n.get("mental_models_linked", [])])
        principles_str = ", ".join([f"[[{p}]]" for p in n.get("first_principles_linked", [])])

        out.append(f"\n## {n.get('title')}")
        out.append(f"- **ID:** `{n.get('id')}`")
        out.append(f"- **Lĩnh vực:** {n.get('domain')}")
        out.append(f"- **Độ nhuần nhuyễn:** {'⭐' * n.get('mastery_level', 1)}")
        out.append(f"- **Tags:** {tags_str}")
        out.append(f"- **Mô hình kết nối:** {models_str or 'None'}")
        out.append(f"- **Nguyên lý kết nối:** {principles_str or 'None'}")
        out.append(f"\n### 💡 Bản chất cốt lõi\n> {n.get('essence')}\n")
        if n.get("metaphor"):
            out.append(f"**Ẩn dụ trực quan:** {n.get('metaphor')}\n")

        if n.get("atomic_concepts"):
            out.append("### 🧩 Khái niệm nguyên tử")
            for c in n.get("atomic_concepts"):
                out.append(f"- {c}")

        if n.get("actionable_steps"):
            out.append("\n### 🪜 Khung hành động thực tế")
            for s in n.get("actionable_steps"):
                out.append(f"1. {s}")

        if n.get("traps_and_biases"):
            out.append(f"\n### 🛡️ Bẫy nhận thức khắc phục\n{n.get('traps_and_biases')}")

        out.append(f"\n<details>\n<summary>📄 Xem nội dung gốc</summary>\n\n```\n{n.get('raw_content')}\n```\n</details>\n")
        out.append("---\n")

    return "\n".join(out)


def export_notes_to_json(username: str) -> str:
    """Xuất toàn bộ kho ghi chú sang định dạng JSON để backup."""
    notes = get_user_notes(username)
    return json.dumps({"username": username, "exported_at": datetime.now().isoformat(), "notes": notes}, ensure_ascii=False, indent=2)


# =============================================================================
# AI DECOMPOSITION & CROSS-SYNTHESIS ENGINE (SELF-CONTAINED)
# =============================================================================

def _clean_json_str(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _normalize_key_list(api_keys: Any) -> List[str]:
    if isinstance(api_keys, str):
        raw = [k.strip() for k in api_keys.split(",") if k.strip()]
    elif isinstance(api_keys, (list, tuple)):
        raw = [str(k).strip() for k in api_keys if str(k).strip()]
    else:
        raw = []
    seen = set()
    unique = []
    for k in raw:
        if k and k not in seen:
            seen.add(k)
            unique.append(k)
    return unique


def _mask_api_key(key: str) -> str:
    if not key or len(key) < 8:
        return "***"
    return f"...{key[-6:]}"


def _is_rate_limit_or_quota(err_str: str) -> bool:
    lower = err_str.lower()
    return any(sig in lower for sig in [
        "429", "resourceexhausted", "quota", "rate limit", "rate_limit", "exhausted", "permission_denied"
    ])


DECOMPOSE_NOTE_PROMPT = """Bạn là Elite Knowledge Architect & Cognitive Scientist (chuyên gia về Second Brain, Zettelkasten, First Principles và Munger Latticework).

Nhiệm vụ: Tiếp nhận nội dung ghi chú thô của người học, phân rã sâu sắc thành các hạt tri thức nguyên tử (atomic knowledge) và kết nối chéo với mạng lưới tư duy đỉnh cao.

BẮT BUỘC trả lời bằng JSON hợp lệ, không bọc code block markdown ngoài JSON.

Cấu trúc JSON yêu cầu:
{
  "title": "Tiêu đề xúc tích, tinh hoa, chuẩn nhận thức (kèm từ khóa chính hoặc song ngữ nếu phù hợp)",
  "essence": "Bản chất cốt lõi nhất được đúc kết trong 1-2 câu ngắn gọn, chuẩn xác, không dùng từ sáo rỗng",
  "domain": "Lĩnh vực chính (chọn 1 trong: 🧠 Siêu nhận thức & Phương pháp học (Metacognition) | 📈 Đầu tư, Chứng khoán & Trading | 💼 Quản trị, Lãnh đạo & Ra quyết định | 🤖 Công nghệ AI & Khoa học Máy tính | 🧬 Khoa học Não bộ & Sinh học | 🧘 Triết học, Tâm thức & Nhân sinh | 🎲 Xác suất, Toán học & Hệ thống phức hợp | 🌱 Thói quen & Phát triển cá nhân | 📦 Khác (Tổng quát))",
  "metaphor": "Hình tượng ẩn dụ hoặc ví dụ đời thường nổi bật được sử dụng trong ghi chú (nếu có, tóm tắt 1-2 câu)",
  "atomic_concepts": [
    "Khái niệm nguyên tử 1 (định nghĩa 1 dòng)",
    "Khái niệm nguyên tử 2 (định nghĩa 1 dòng)",
    "Khái niệm nguyên tử 3 (định nghĩa 1 dòng)"
  ],
  "mental_models_linked": [
    "Tên mô hình tư duy liên quan mật thiết (Ví dụ: First Principles Thinking, Illusion of Explanatory Depth, Inversion, Feedback Loop, Power Law, Opportunity Cost...)"
  ],
  "first_principles_linked": [
    "Tên nguyên lý đệ nhất liên quan (Ví dụ: Nguyên lý trừu tượng hóa, Nguyên lý phản hồi chủ động, Định luật bảo toàn...)"
  ],
  "actionable_steps": [
    "Bước 1: ...",
    "Bước 2: ...",
    "Bước 3: ..."
  ],
  "traps_and_biases": "Bẫy tư duy, ảo tưởng hoặc sai lầm nhận thức phổ biến mà ghi chú này giúp khắc phục",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "study_questions": [
    {
      "question": "Câu hỏi ôn tập / phản xạ nhận thức (Active Recall)",
      "answer": "Gợi ý cốt lõi trả lời"
    },
    {
      "question": "Câu hỏi đào sâu / phản biện tình huống",
      "answer": "Gợi ý cốt lõi trả lời"
    }
  ],
  "cross_topic_connections": "Gợi ý liên kết chéo: khái niệm này có thể ứng dụng chéo vào những bài toán hay lĩnh vực nào khác (ví dụ: trading, giao tiếp lãnh đạo, nuôi dạy con, đàm phán...)"
}

Quy tắc BẮT BUỘC:
- 100% nội dung giải thích, câu hỏi, bước hành động phải viết bằng TIẾNG VIỆT tự nhiên, sâu sắc, chuẩn xác.
"""


def decompose_knowledge_note(
    api_keys: Any,
    model_name: str,
    raw_content: str,
    title_hint: str = "",
) -> Dict[str, Any]:
    """Phân rã ghi chú thô bằng AI Gemini với cơ chế failover và fallback Heuristic tự động."""
    if not raw_content.strip():
        return heuristic_decompose_note(raw_content, title_hint)

    keys = _normalize_key_list(api_keys)
    if not keys or genai is None:
        return heuristic_decompose_note(raw_content, title_hint)

    prompt = f"""Gợi ý tiêu đề từ người học (nếu có): {title_hint}

Nội dung ghi chú thô cần phân rã:
\"\"\"
{raw_content}
\"\"\"
"""
    candidates = [model_name or "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
    last_err = None

    for idx, current_key in enumerate(keys, 1):
        mask = _mask_api_key(current_key)
        try:
            genai.configure(api_key=current_key)
        except Exception as e:
            last_err = f"Lỗi cấu hình Key #{idx} ({mask}): {e}"
            continue

        for candidate in candidates:
            try:
                model = genai.GenerativeModel(
                    model_name=candidate,
                    system_instruction=DECOMPOSE_NOTE_PROMPT,
                    generation_config={"response_mime_type": "application/json"},
                )
                resp = model.generate_content(
                    prompt,
                    request_options={"retry": None, "timeout": 30}
                )
                if resp and resp.text:
                    cleaned = _clean_json_str(resp.text)
                    data = json.loads(cleaned)
                    if isinstance(data, dict):
                        data["_decomposed_by"] = f"Gemini ({candidate}) [Key {mask}]"
                        return data
            except Exception as e:
                err_msg = str(e)
                last_err = f"Key #{idx} ({mask}) lỗi [{candidate}]: {err_msg}"
                if _is_rate_limit_or_quota(err_msg):
                    break
                continue

    # Fallback sang Heuristic nếu API lỗi
    data = heuristic_decompose_note(raw_content, title_hint)
    data["_decomposed_by"] = f"Heuristic Fallback Engine (API tạm gián đoạn: {last_err})"
    return data


SYNTHESIZE_NOTES_PROMPT = """Bạn là Elite Knowledge Architect. 
Nhiệm vụ: Phân tích sự giao thoa, mối liên hệ đa chiều và tổng hợp bài học liên ngành giữa các ghi chú tri thức mà người học đã tích lũy trong Second Brain.

Yêu cầu đầu ra (viết bằng Markdown rõ ràng, sắc bén):
1. **Điểm Giao Thoa Tri Thức (Core Intersection)**: Bản chất chung kết nối các ghi chú này là gì?
2. **Hiệu Ứng Cộng Hưởng & Đòn Bẩy (Latticework Synergy)**: Khi kết hợp các khái niệm này lại, ta tạo ra lợi thế nhận thức gì mà từng khái niệm riêng lẻ không có?
3. **Mâu Thuẫn / Điểm Nghẽn Cần Lưu Ý (Nuances & Traps)**: Có điều kiện biên hay mâu thuẫn biểu kiến nào giữa chúng cần dung hòa không?
4. **Mô Hình Hành Động Tích Hợp (Integrated Action Playbook)**: 3-4 bước ứng dụng tổng hợp vào thực tế công việc, đầu tư hay học tập.
"""


def synthesize_cross_notes(
    api_keys: Any,
    model_name: str,
    notes_list: List[Dict[str, Any]],
    user_query: str = "",
) -> str:
    """Tổng hợp sự giao thoa giữa nhiều ghi chú tri thức."""
    keys = _normalize_key_list(api_keys)
    if not keys or genai is None:
        return "⚠️ Cần cấu hình API Key để kích hoạt tính năng AI Tổng Hợp Giao Thoa Tri Thức."

    notes_summary_parts = []
    for i, n in enumerate(notes_list, 1):
        notes_summary_parts.append(f"""### Ghi chú #{i}: {n.get('title')}
- Lĩnh vực: {n.get('domain')}
- Bản chất cốt lõi: {n.get('essence')}
- Mô hình liên kết: {', '.join(n.get('mental_models_linked', []))}
- Các bước: {' -> '.join(n.get('actionable_steps', []))}
- Tóm lược gốc: {n.get('raw_content', '')[:600]}
""")

    prompt = f"""Dưới đây là {len(notes_list)} ghi chú tri thức trong kho Second Brain của người học:

{chr(10).join(notes_summary_parts)}

{f'Câu hỏi / Hướng tập trung của người học: {user_query}' if user_query else 'Hãy phân tích sự giao thoa, sức mạnh cộng hưởng và mô hình hành động tích hợp giữa các ghi chú này.'}
"""
    candidates = [model_name or "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
    last_err = None

    for idx, current_key in enumerate(keys, 1):
        mask = _mask_api_key(current_key)
        try:
            genai.configure(api_key=current_key)
        except Exception as e:
            last_err = f"Lỗi cấu hình Key #{idx} ({mask}): {e}"
            continue

        for candidate in candidates:
            try:
                model = genai.GenerativeModel(
                    model_name=candidate,
                    system_instruction=SYNTHESIZE_NOTES_PROMPT,
                )
                resp = model.generate_content(
                    prompt,
                    request_options={"retry": None, "timeout": 30}
                )
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                err_msg = str(e)
                last_err = f"Key #{idx} ({mask}) lỗi [{candidate}]: {err_msg}"
                if _is_rate_limit_or_quota(err_msg):
                    break
                continue

    return f"Lỗi khi tổng hợp giao thoa ghi chú: {last_err}"

