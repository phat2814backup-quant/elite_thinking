# -*- coding: utf-8 -*-
"""
Module Kho Hồ Sơ SKU Tri Thức Nguyên Bản & Trình Ghép Sách (Verbatim Atomic Excerpt Warehouse & Book Compiler).

Triết lý cốt lõi:
1. Amazon Fulfillment SKU Model: Mỗi mẩu kiến thức nhỏ là một SKU độc lập, dán nhãn đa chiều.
2. Zero-Paraphrase Invariance: Bảo toàn 100% văn bản gốc, cấm sửa đổi/tóm tắt/paraphrase.
3. Book Assembler: Ghép các SKU theo cây mục lục sách (Chương -> Tiết) thành bản thảo hoàn chỉnh.
"""

from __future__ import annotations

import re
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from utils.knowledge import load_user_history, save_user_history
from utils.knowledge_archive import get_vn_now_str

try:
    import google.generativeai as genai
except Exception:
    genai = None

# Danh mục Lĩnh vực chuẩn
SKU_DOMAINS = [
    "🧠 Tư duy, Nhận thức & Mô hình tâm trí",
    "📈 Đầu tư, Tài chính & Chứng khoán",
    "💼 Quản trị, Lãnh đạo & Ra quyết định",
    "🤖 Công nghệ, AI & Khoa học máy tính",
    "🎲 Xác suất, Toán học & Hệ thống phức hợp",
    "🧬 Sinh học, Tâm lý & Hành vi con người",
    "🧘 Triết học, Nhân sinh & Chiêm nghiệm",
    "📚 Nghệ thuật viết lách & Sáng tạo",
    "📦 Lĩnh vực khác",
]

# Dữ liệu mẫu khởi đầu (Seed SKUs)
DEFAULT_SEED_SKUS: List[Dict[str, Any]] = [
    {
        "sku_id": "SKU-SEED-001",
        "title": "Elon Musk: Phương pháp Tư duy từ Nguyên lý đầu tiên (First Principles)",
        "raw_content": (
            "I think it's important to reason from first principles rather than by analogy. "
            "The normal way we conduct our lives is we reason by analogy. "
            "[With analogy] we are doing this because it's like something else that was done, "
            "or it is being done by other people. [With first principles] you boil things down to "
            "the most fundamental truths and then reason up from there.\n\n"
            "Dịch nghĩa nguyên bản: Tôi nghĩ điều quan trọng là phải tư duy từ nguyên lý đầu tiên thay vì tương suy (so sánh tương đồng). "
            "Cách thông thường chúng ta vận hành cuộc sống là so sánh: chúng ta làm việc này vì nó giống với việc người khác từng làm. "
            "Còn với nguyên lý đầu tiên, bạn phân rã mọi thứ về những chân lý cơ bản nhất mà bạn chắc chắn là đúng, "
            "rồi từ đó mới lập luận xây dựng ngược lên."
        ),
        "source": {
            "author": "Elon Musk",
            "book_title": "Phỏng vấn độc quyền với Kevin Rose (Foundation)",
            "page": "Video Interview",
            "url": "https://www.youtube.com",
            "collected_date": "2026-09-08"
        },
        "domain": "🧠 Tư duy, Nhận thức & Mô hình tâm trí",
        "topic": "First Principles & Phân rã nền tảng",
        "tags": ["first-principles", "elon-musk", "reasoning", "problem-solving"],
        "book_project_id": "book_elite_thinking_seed",
        "target_chapter_id": "chap_1",
        "target_chapter": "Chương 1: Nền Tảng Tư Duy Đột Phá",
        "target_section_id": "sec_1_1",
        "target_section": "1.1 Phân rã về chân lý cơ bản nhất",
        "sort_order": 1,
        "user_note": "Trích dẫn đinh để mở đầu Chương 1 về First Principles.",
        "created_at": "2026-09-08 10:00:00",
        "updated_at": "2026-09-08 10:00:00"
    },
    {
        "sku_id": "SKU-SEED-002",
        "title": "Charlie Munger: Nghệ thuật Đảo ngược vấn đề (Invert, Always Invert)",
        "raw_content": (
            "Invert, always invert: Turn a situation or problem upside down. Look at it backward. "
            "What happens if all our plans go wrong? Where don't we want to go, and how do you get there? "
            "Instead of looking for success, make a list of how to fail instead—through sloth, envy, "
            "resentment, self-pity, entitlement, all the mental habits of self-defeat. "
            "Avoid these qualities and you will succeed. Tell me where I'm going to die so I'll never go there.\n\n"
            "Dịch nghĩa nguyên bản: Đảo ngược, luôn luôn đảo ngược: Hãy lộn ngược một tình huống hoặc vấn đề. Nhìn nó từ phía sau tới. "
            "Điều gì sẽ xảy ra nếu mọi kế hoạch của ta đổ vỡ? Nơi nào ta không muốn tới, và bằng cách nào người ta đi tới đó? "
            "Thay vì tìm kiếm thành công, hãy lập danh sách những cách để thất bại—qua sự lười biếng, đố kỵ, oán giận, tự thương hại bản thân. "
            "Hãy tránh xa những thứ đó và bạn sẽ thành công. Hãy nói cho tôi biết tôi sẽ chết ở đâu, để tôi không bao giờ bén mảng tới đó."
        ),
        "source": {
            "author": "Charlie Munger",
            "book_title": "Poor Charlie's Almanack",
            "page": "142-145",
            "url": "",
            "collected_date": "2026-09-08"
        },
        "domain": "🧠 Tư duy, Nhận thức & Mô hình tâm trí",
        "topic": "Tư duy đảo ngược (Inversion)",
        "tags": ["charlie-munger", "inversion", "avoiding-stupidity", "mental-models"],
        "book_project_id": "book_elite_thinking_seed",
        "target_chapter_id": "chap_2",
        "target_chapter": "Chương 2: Nghệ Thuật Đảo Ngược Vấn Đề",
        "target_section_id": "sec_2_1",
        "target_section": "2.1 Tìm thất bại để né tránh thành công",
        "sort_order": 1,
        "user_note": "Dùng làm ví dụ thực tiễn cho mô hình Inversion.",
        "created_at": "2026-09-08 11:00:00",
        "updated_at": "2026-09-08 11:00:00"
    },
    {
        "sku_id": "SKU-SEED-003",
        "title": "Richard Feynman: Phân biệt giữa Biết Tên và Thấu Hiểu Bản Chất",
        "raw_content": (
            "You can know the name of that bird in all the languages of the world, but when you're finished, "
            "you'll know absolutely nothing whatever about the bird. You'll only know about humans in different "
            "places, and what they call the bird. So let's look at the bird and see what it's doing—that's what counts.\n\n"
            "Dịch nghĩa nguyên bản: Bạn có thể biết tên con chim đó trong tất cả các thứ tiếng trên thế giới, nhưng khi bạn nói xong tên nó, "
            "bạn thực chất chẳng biết một chút gì về con chim đó cả. Bạn chỉ biết con người ở những nơi khác nhau gọi con chim đó là gì. "
            "Bởi vậy, hãy quan sát con chim và xem nó đang thực sự làm gì—đó mới là điều có ý nghĩa."
        ),
        "source": {
            "author": "Richard Feynman",
            "book_title": "The Pleasure of Finding Things Out",
            "page": "14",
            "url": "",
            "collected_date": "2026-09-08"
        },
        "domain": "🧠 Tư duy, Nhận thức & Mô hình tâm trí",
        "topic": "Bản chất vs Tên gọi (Knowing vs Understanding)",
        "tags": ["richard-feynman", "feynman-technique", "deep-understanding", "epistemology"],
        "book_project_id": "book_elite_thinking_seed",
        "target_chapter_id": "chap_1",
        "target_chapter": "Chương 1: Nền Tảng Tư Duy Đột Phá",
        "target_section_id": "sec_1_2",
        "target_section": "1.2 Tránh bẫy tương suy & ảo tưởng nhãn mác",
        "sort_order": 1,
        "user_note": "Nhấn mạnh sự khác biệt giữa học vẹt từ ngữ và thấu hiểu cơ chế vận hành.",
        "created_at": "2026-09-08 12:00:00",
        "updated_at": "2026-09-08 12:00:00"
    }
]

# Dự án sách mẫu khởi đầu
DEFAULT_SEED_BOOK_PROJECT: Dict[str, Any] = {
    "project_id": "book_elite_thinking_seed",
    "title": "Sổ Tay Tư Duy Tinh Hoa & Thực Chiến",
    "subtitle": "Hệ thống trích dẫn nguyên bản, mô hình tâm trí và nguyên lý đệ nhất",
    "author": "Elite Thinking Family",
    "description": "Bản thảo sách tổng hợp các trích đoạn tinh hoa nguyên bản được phân loại theo cấu trúc logic từ nền tảng đến ứng dụng.",
    "outline": [
        {
            "chapter_id": "chap_1",
            "chapter_title": "Chương 1: Nền Tảng Tư Duy Đột Phá",
            "sections": [
                {"section_id": "sec_1_1", "section_title": "1.1 Phân rã về chân lý cơ bản nhất"},
                {"section_id": "sec_1_2", "section_title": "1.2 Tránh bẫy tương suy & ảo tưởng nhãn mác"}
            ]
        },
        {
            "chapter_id": "chap_2",
            "chapter_title": "Chương 2: Nghệ Thuật Đảo Ngược Vấn Đề",
            "sections": [
                {"section_id": "sec_2_1", "section_title": "2.1 Tìm thất bại để né tránh thành công"},
                {"section_id": "sec_2_2", "section_title": "2.2 Nhận diện điểm mù và bẫy định kiến"}
            ]
        },
        {
            "chapter_id": "chap_3",
            "chapter_title": "Chương 3: Tư Duy Hệ Thống & Tác Động Bậc Hai",
            "sections": [
                {"section_id": "sec_3_1", "section_title": "3.1 Câu hỏi 'Và rồi sao nữa?' (Second-Order Thinking)"},
                {"section_id": "sec_3_2", "section_title": "3.2 Vòng lặp phản hồi và độ trễ hệ thống"}
            ]
        }
    ],
    "created_at": "2026-09-08 10:00:00",
    "updated_at": "2026-09-08 10:00:00"
}


# =============================================================================
# Helper Persistence: SKUs
# =============================================================================

def get_user_skus(username: str) -> List[Dict[str, Any]]:
    """Tải danh sách SKU của user từ user_histories, fallback seed mặc định nếu trống."""
    history = load_user_history(username)
    skus = history.get("knowledge_skus")
    if skus is None:
        skus = list(DEFAULT_SEED_SKUS)
        history["knowledge_skus"] = skus
        save_user_history(username, history)
    return skus


def save_user_skus(username: str, skus: List[Dict[str, Any]]) -> bool:
    """Lưu danh sách SKU vào user_histories."""
    history = load_user_history(username)
    history["knowledge_skus"] = skus
    return save_user_history(username, history)


def create_sku(
    username: str,
    raw_content: str,
    title: str = "",
    source: Optional[Dict[str, Any]] = None,
    domain: str = "🧠 Tư duy, Nhận thức & Mô hình tâm trí",
    topic: str = "",
    tags: Optional[List[str]] = None,
    book_project_id: str = "",
    target_chapter_id: str = "",
    target_chapter: str = "",
    target_section_id: str = "",
    target_section: str = "",
    sort_order: int = 1,
    user_note: str = ""
) -> Dict[str, Any]:
    """
    Tạo mới một SKU trích đoạn nguyên bản (Bảo toàn 100% văn bản).
    """
    cleaned_raw = raw_content.strip()
    if not cleaned_raw:
        raise ValueError("Nội dung trích đoạn gốc (raw_content) không được để trống!")

    now_str = get_vn_now_str()
    short_uuid = uuid.uuid4().hex[:6].upper()
    sku_id = f"SKU-{datetime.now().strftime('%Y%m%d')}-{short_uuid}"

    if not title.strip():
        words = cleaned_raw.split()
        title = " ".join(words[:10]) + ("..." if len(words) > 10 else "")

    new_sku: Dict[str, Any] = {
        "sku_id": sku_id,
        "title": title.strip(),
        "raw_content": cleaned_raw,  # Nguyên bản bất biến
        "source": source or {
            "author": "",
            "book_title": "",
            "page": "",
            "url": "",
            "collected_date": datetime.now().strftime("%Y-%m-%d")
        },
        "domain": domain,
        "topic": topic.strip(),
        "tags": [t.strip().lower() for t in (tags or []) if t.strip()],
        "book_project_id": book_project_id.strip(),
        "target_chapter_id": target_chapter_id.strip(),
        "target_chapter": target_chapter.strip(),
        "target_section_id": target_section_id.strip(),
        "target_section": target_section.strip(),
        "sort_order": int(sort_order),
        "user_note": user_note.strip(),
        "created_at": now_str,
        "updated_at": now_str
    }

    skus = get_user_skus(username)
    skus.insert(0, new_sku)
    save_user_skus(username, skus)
    return new_sku


def update_sku(username: str, sku_id: str, updates: Dict[str, Any]) -> bool:
    """Cập nhật thông tin SKU (metadata, ghi chú, vị trí sách)."""
    skus = get_user_skus(username)
    found = False
    for sku in skus:
        if sku.get("sku_id") == sku_id:
            for k, v in updates.items():
                sku[k] = v
            sku["updated_at"] = get_vn_now_str()
            found = True
            break
    if found:
        return save_user_skus(username, skus)
    return False


def delete_sku(username: str, sku_id: str) -> bool:
    """Xoá một SKU khỏi kho."""
    skus = get_user_skus(username)
    new_skus = [s for s in skus if s.get("sku_id") != sku_id]
    if len(new_skus) < len(skus):
        return save_user_skus(username, new_skus)
    return False


def get_sku_by_id(username: str, sku_id: str) -> Optional[Dict[str, Any]]:
    skus = get_user_skus(username)
    for s in skus:
        if s.get("sku_id") == sku_id:
            return s
    return None


# =============================================================================
# Helper Persistence: Book Projects
# =============================================================================

def get_user_book_projects(username: str) -> List[Dict[str, Any]]:
    """Lấy danh sách các dự án sách của user."""
    history = load_user_history(username)
    projects = history.get("book_projects")
    if projects is None:
        projects = [dict(DEFAULT_SEED_BOOK_PROJECT)]
        history["book_projects"] = projects
        save_user_history(username, history)
    return projects


def save_user_book_projects(username: str, projects: List[Dict[str, Any]]) -> bool:
    history = load_user_history(username)
    history["book_projects"] = projects
    return save_user_history(username, history)


def create_book_project(
    username: str,
    title: str,
    subtitle: str = "",
    author: str = "",
    description: str = "",
    outline: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Tạo dự án sách mới."""
    now_str = get_vn_now_str()
    pid = f"book_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

    new_project: Dict[str, Any] = {
        "project_id": pid,
        "title": title.strip(),
        "subtitle": subtitle.strip(),
        "author": author.strip() or username,
        "description": description.strip(),
        "outline": outline or [
            {
                "chapter_id": "chap_1",
                "chapter_title": "Chương 1: Mở Đầu & Đặt Vấn Đề",
                "sections": [
                    {"section_id": "sec_1_1", "section_title": "1.1 Bối cảnh & Thực trạng"},
                    {"section_id": "sec_1_2", "section_title": "1.2 Mục tiêu cuốn sách"}
                ]
            }
        ],
        "created_at": now_str,
        "updated_at": now_str
    }

    projects = get_user_book_projects(username)
    projects.append(new_project)
    save_user_book_projects(username, projects)
    return new_project


def get_book_project_by_id(username: str, project_id: str) -> Optional[Dict[str, Any]]:
    projects = get_user_book_projects(username)
    for p in projects:
        if p.get("project_id") == project_id:
            return p
    return None


def update_book_project(username: str, project_id: str, updates: Dict[str, Any]) -> bool:
    projects = get_user_book_projects(username)
    for p in projects:
        if p.get("project_id") == project_id:
            for k, v in updates.items():
                p[k] = v
            p["updated_at"] = get_vn_now_str()
            return save_user_book_projects(username, projects)
    return False


def delete_book_project(username: str, project_id: str) -> bool:
    projects = get_user_book_projects(username)
    new_projects = [p for p in projects if p.get("project_id") != project_id]
    if len(new_projects) < len(projects):
        return save_user_book_projects(username, new_projects)
    return False


def add_chapter_to_book(username: str, project_id: str, chapter_title: str) -> bool:
    """Thêm một chương mới vào mục lục sách."""
    project = get_book_project_by_id(username, project_id)
    if not project:
        return False
    outline = project.get("outline", [])
    new_chap_id = f"chap_{len(outline) + 1}"
    outline.append({
        "chapter_id": new_chap_id,
        "chapter_title": chapter_title.strip(),
        "sections": [
            {"section_id": f"{new_chap_id}_sec_1", "section_title": "1.1 Tổng quan"}
        ]
    })
    return update_book_project(username, project_id, {"outline": outline})


def add_section_to_chapter(username: str, project_id: str, chapter_id: str, section_title: str) -> bool:
    """Thêm một tiết mới vào một chương cụ thể."""
    project = get_book_project_by_id(username, project_id)
    if not project:
        return False
    outline = project.get("outline", [])
    found = False
    for chap in outline:
        if chap.get("chapter_id") == chapter_id:
            sections = chap.get("sections", [])
            new_sec_id = f"{chapter_id}_sec_{len(sections) + 1}"
            sections.append({
                "section_id": new_sec_id,
                "section_title": section_title.strip()
            })
            chap["sections"] = sections
            found = True
            break
    if found:
        return update_book_project(username, project_id, {"outline": outline})
    return False


# =============================================================================
# Bộ Lọc & Tìm Kiếm SKU
# =============================================================================

def search_filter_skus(
    skus: List[Dict[str, Any]],
    query: str = "",
    domain: Optional[str] = None,
    tag: Optional[str] = None,
    book_project_id: Optional[str] = None,
    author: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lọc danh sách SKU đa chiều."""
    results = skus
    q = query.strip().lower()

    if q:
        matched = []
        for s in results:
            content_match = q in s.get("raw_content", "").lower()
            title_match = q in s.get("title", "").lower()
            topic_match = q in s.get("topic", "").lower()
            source_info = s.get("source", {})
            author_match = q in str(source_info.get("author", "")).lower()
            book_match = q in str(source_info.get("book_title", "")).lower()
            sku_id_match = q in s.get("sku_id", "").lower()
            tags_match = any(q in str(t).lower() for t in s.get("tags", []))
            note_match = q in s.get("user_note", "").lower()

            if any([content_match, title_match, topic_match, author_match, book_match, sku_id_match, tags_match, note_match]):
                matched.append(s)
        results = matched

    if domain and domain != "Tất cả":
        results = [s for s in results if s.get("domain") == domain]

    if tag and tag != "Tất cả":
        tag_norm = tag.strip().lower()
        results = [s for s in results if any(tag_norm == str(t).lower() for t in s.get("tags", []))]

    if book_project_id and book_project_id != "Tất cả":
        results = [s for s in results if s.get("book_project_id") == book_project_id]

    if author and author != "Tất cả":
        author_norm = author.strip().lower()
        results = [s for s in results if author_norm in str(s.get("source", {}).get("author", "")).lower()]

    return results


def get_all_sku_domains(skus: List[Dict[str, Any]]) -> List[str]:
    domains = sorted({s.get("domain") for s in skus if s.get("domain")})
    return ["Tất cả"] + domains


def get_all_sku_tags(skus: List[Dict[str, Any]]) -> List[str]:
    tags_set = set()
    for s in skus:
        for t in s.get("tags", []):
            if t:
                tags_set.add(t.strip().lower())
    return ["Tất cả"] + sorted(tags_set)


def get_all_sku_authors(skus: List[Dict[str, Any]]) -> List[str]:
    authors = set()
    for s in skus:
        a = s.get("source", {}).get("author", "").strip()
        if a:
            authors.add(a)
    return ["Tất cả"] + sorted(authors)


# =============================================================================
# AI Zero-Paraphrase Tagger (Thủ Kho Quét Mã Vạch)
# =============================================================================

ZERO_PARAPHRASE_PROMPT = """Bạn là 'Thủ Kho AI' của hệ thống Quản Trị Tri Thức Theo Mô Hình Amazon SKU (SKU Knowledge Warehouse).

NHIỆM VỤ DUY NHẤT CỦA BẠN:
Đọc kỹ đoạn văn bản trích dẫn gốc và trích xuất METADATA (Dữ liệu gắn nhãn phân loại).

QUY TẮC BẤT KHẢ XÂM PHẠM:
1. TUYỆT ĐỐI KHÔNG TÓM TẮT, KHÔNG VIẾT LẠI, KHÔNG PARAPHRASE, KHÔNG THAY ĐỔI DÙ CHỈ 1 CHỮ CỦA VĂN BẢN GỐC.
2. Bạn chỉ cung cấp thông tin phân loại để dán nhãn SKU và phân kệ lưu trữ.
3. Đầu ra BẮT BUỘC là 1 đối tượng JSON duy nhất với đúng các trường sau:

{
  "suggested_title": "Tiêu đề ngắn 6-12 từ nhận diện trích đoạn",
  "domain": "Chọn 1 trong: 🧠 Tư duy, Nhận thức & Mô hình tâm trí | 📈 Đầu tư, Tài chính & Chứng khoán | 💼 Quản trị, Lãnh đạo & Ra quyết định | 🤖 Công nghệ, AI & Khoa học máy tính | 🎲 Xác suất, Toán học & Hệ thống phức hợp | 🧬 Sinh học, Tâm lý & Hành vi con người | 🧘 Triết học, Nhân sinh & Chiêm nghiệm | 📚 Nghệ thuật viết lách & Sáng tạo | 📦 Lĩnh vực khác",
  "topic": "Chủ đề nhánh cụ thể (Ví dụ: First Principles, Biến động giá, Thiên kiến xác nhận...)",
  "tags": ["tag1", "tag2", "tag3", "tag4"],
  "suggested_chapter": "Gợi ý tên chương nếu đưa đoạn này vào một cuốn sách chuyên ngành",
  "suggested_section": "Gợi ý tên tiểu mục tương ứng"
}
"""


def _heuristic_tag_sku(raw_content: str) -> Dict[str, Any]:
    """Phân loại dự phòng khi không có AI API key."""
    words = raw_content.split()
    first_few = " ".join(words[:8])
    title = f"Trích đoạn: {first_few}..."

    text_lower = raw_content.lower()
    domain = "🧠 Tư duy, Nhận thức & Mô hình tâm trí"
    topic = "Nguyên lý & Tư duy cốt lõi"
    tags = ["tri-thuc-nguyen-ban", "trich-dan"]

    if any(w in text_lower for w in ["chứng khoán", "cổ phiếu", "đầu tư", "lợi nhuận", "tiền tệ", "thị trường", "giá"]):
        domain = "📈 Đầu tư, Tài chính & Chứng khoán"
        topic = "Đầu tư & Thị trường"
        tags.extend(["dau-tu", "tai-chinh"])
    elif any(w in text_lower for w in ["quản trị", "lãnh đạo", "doanh nghiệp", "nhân sự", "chiến lược", "quyết định"]):
        domain = "💼 Quản trị, Lãnh đạo & Ra quyết định"
        topic = "Chiến lược & Ra quyết định"
        tags.extend(["quan-tri", "lanh-dao"])
    elif any(w in text_lower for w in ["ai", "mô hình", "code", "máy tính", "thuật toán", "dữ liệu", "algorithm"]):
        domain = "🤖 Công nghệ, AI & Khoa học máy tính"
        topic = "Khoa học máy tính & AI"
        tags.extend(["cong-nghe", "ai"])

    return {
        "suggested_title": title,
        "domain": domain,
        "topic": topic,
        "tags": tags,
        "suggested_chapter": "Chương 1: Các luận điểm và quan sát nền tảng",
        "suggested_section": "1.1 Bóc tách và dẫn chứng nguyên bản",
        "_tagged_by": "Heuristic Rule-based"
    }


def ai_tag_sku_metadata(
    raw_content: str,
    api_keys: List[str],
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Sử dụng Gemini API để quét mã vạch và gắn nhãn cho trích đoạn.
    Cam kết: Tuyệt đối không can thiệp vào ruột văn bản gốc.
    """
    cleaned_raw = raw_content.strip()
    if not cleaned_raw:
        return _heuristic_tag_sku("Trống")

    valid_keys = [k.strip() for k in api_keys if k and k.strip() and not k.startswith("AQ.")]
    if not valid_keys or genai is None:
        return _heuristic_tag_sku(cleaned_raw)

    prompt = f"""Đoạn văn bản trích dẫn gốc cần quét mã vạch SKU:
\"\"\"
{cleaned_raw}
\"\"\"
"""
    candidates = [model_name, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

    for current_key in valid_keys:
        try:
            genai.configure(api_key=current_key)
            for candidate in candidates:
                try:
                    model = genai.GenerativeModel(
                        model_name=candidate,
                        system_instruction=ZERO_PARAPHRASE_PROMPT,
                        generation_config={"response_mime_type": "application/json"},
                    )
                    resp = model.generate_content(
                        prompt,
                        request_options={"timeout": 30}
                    )
                    if resp and resp.text:
                        text = resp.text.strip()
                        if text.startswith("```"):
                            lines = text.splitlines()
                            if len(lines) >= 2 and lines[-1].startswith("```"):
                                text = "\n".join(lines[1:-1]).strip()
                        data = json.loads(text)
                        if isinstance(data, dict):
                            data["_tagged_by"] = f"Gemini ({candidate})"
                            return data
                except Exception:
                    continue
        except Exception:
            continue

    return _heuristic_tag_sku(cleaned_raw)


# =============================================================================
# Book Compiler / Assembler (Trình Ghép Sách Hoàn Chỉnh)
# =============================================================================

def compile_book_manuscript(username: str, project_id: str) -> Dict[str, Any]:
    """
    Duyệt qua cây mục lục của dự án sách, bốc toàn bộ các SKU nguyên bản tương ứng,
    sắp xếp và ghép thành bản thảo sách hoàn chỉnh dưới dạng Markdown.
    """
    project = get_book_project_by_id(username, project_id)
    if not project:
        return {
            "success": False,
            "error": "Không tìm thấy dự án sách!",
            "markdown": "",
            "total_words": 0,
            "total_skus": 0
        }

    skus = get_user_skus(username)
    book_skus = [s for s in skus if s.get("book_project_id") == project_id]

    sku_by_section: Dict[str, List[Dict[str, Any]]] = {}
    for s in book_skus:
        sec_key = s.get("target_section_id") or s.get("target_section") or "unassigned"
        sku_by_section.setdefault(sec_key, []).append(s)

    for sec_key in sku_by_section:
        sku_by_section[sec_key].sort(key=lambda x: (int(x.get("sort_order", 1)), x.get("created_at", "")))

    md_lines: List[str] = []
    
    book_title = project.get("title", "BẢN THẢO SÁCH")
    subtitle = project.get("subtitle", "")
    author = project.get("author", username)
    desc = project.get("description", "")

    md_lines.append(f"# {book_title.upper()}")
    if subtitle:
        md_lines.append(f"*{subtitle}*\n")
    md_lines.append(f"**Tác giả / Tổng hợp:** {author}")
    md_lines.append(f"**Thời gian biên soạn:** {get_vn_now_str()}")
    if desc:
        md_lines.append(f"\n> **Lời tựa:** {desc}")
    md_lines.append("\n---\n")

    md_lines.append("## 📑 MỤC LỤC TỔNG QUAN\n")
    outline = project.get("outline", [])
    for idx_c, chap in enumerate(outline, 1):
        c_title = chap.get("chapter_title", f"Chương {idx_c}")
        md_lines.append(f"- **{c_title}**")
        for idx_s, sec in enumerate(chap.get("sections", []), 1):
            s_title = sec.get("section_title", f"Tiết {idx_s}")
            sec_id = sec.get("section_id", "")
            sec_skus_count = len(sku_by_section.get(sec_id, []))
            if not sec_skus_count:
                sec_skus_count = len(sku_by_section.get(s_title, []))
            md_lines.append(f"  - {s_title} *({sec_skus_count} trích đoạn)*")
    md_lines.append("\n---\n")

    total_skus_compiled = 0

    for idx_c, chap in enumerate(outline, 1):
        c_title = chap.get("chapter_title", f"Chương {idx_c}")
        md_lines.append(f"\n# {c_title}\n")

        sections = chap.get("sections", [])
        for idx_s, sec in enumerate(sections, 1):
            s_title = sec.get("section_title", f"Tiết {idx_s}")
            s_id = sec.get("section_id", "")
            md_lines.append(f"\n## {s_title}\n")

            sec_skus = sku_by_section.get(s_id, [])
            if not sec_skus:
                sec_skus = sku_by_section.get(s_title, [])

            if not sec_skus:
                md_lines.append("*(Tiết này chưa có trích đoạn SKU nào được gán)*\n")
                continue

            for sku in sec_skus:
                total_skus_compiled += 1
                sku_title = sku.get("title", "")
                raw_text = sku.get("raw_content", "").strip()
                source = sku.get("source", {})
                author_name = source.get("author", "Khuyết danh").strip()
                book_src = source.get("book_title", "").strip()
                page = source.get("page", "").strip()
                url = source.get("url", "").strip()
                note = sku.get("user_note", "").strip()
                sku_id = sku.get("sku_id", "")

                md_lines.append(f"### 📦 [{sku_id}] {sku_title}\n")
                
                quote_lines = [f"> {line}" for line in raw_text.splitlines()]
                md_lines.append("\n".join(quote_lines))
                md_lines.append(">")

                cite_parts = [f"**Tác giả:** {author_name}"]
                if book_src:
                    cite_parts.append(f"**Tác phẩm:** *{book_src}*")
                if page:
                    cite_parts.append(f"**Trang/Vị trí:** {page}")
                if url:
                    cite_parts.append(f"**Link:** {url}")
                md_lines.append(f"> — *Trích dẫn nguồn: {', '.join(cite_parts)}*")
                md_lines.append("")

                if note:
                    md_lines.append(f"💡 **Chỉ đạo / Bình luận của tác giả:** {note}\n")
                
                md_lines.append("")

    full_markdown = "\n".join(md_lines)
    word_count = len(full_markdown.split())

    return {
        "success": True,
        "markdown": full_markdown,
        "total_words": word_count,
        "total_skus": total_skus_compiled,
        "total_chapters": len(outline),
        "project_title": book_title
    }


# =============================================================================
# AI Auto-Clustering & Living Book Synthesis (Từ Mảnh Ghép -> Mục Lục Sách)
# =============================================================================

BOOK_CLUSTERING_PROMPT = """Bạn là Tổng Biên Tập Xuất Bản Sách Chuyên Nghiệp.
Tác giả đã thu thập nhiều mảnh ghép tri thức (trích đoạn, thẻ ghi chú) về một chủ đề cụ thể.
Nhiệm vụ của bạn là đọc các trích đoạn này, phát hiện các cụm ngữ nghĩa tự nhiên, và thiết kế một CÂY MỤC LỤC SÁCH HOÀN CHỈNH (Chương -> Tiết), sau đó phân bổ từng trích đoạn (theo ID) vào đúng Tiết phù hợp nhất.

QUY TẮC CỐT LÕI:
1. Thứ tự logic sách: Đi từ Bản chất / Nguyên lý cơ bản -> Công cụ / Kỹ thuật phân tích -> Chiến lược / Quản trị rủi ro -> Ứng dụng thực chiến.
2. Đặt tên Chương và Tiết thật cô đọng, sắc bén, mang phong thái chuyên gia.
3. Mỗi trích đoạn BẮT BUỘC phải được gán vào ít nhất một Tiết.
4. Trả về 1 JSON duy nhất theo schema sau (không kèm markdown ngoài JSON):
{
  "suggested_title": "Tựa đề cuốn sách đầy đủ",
  "suggested_subtitle": "Phụ đề gợi ý",
  "chapters": [
    {
      "chapter_id": "chap_1",
      "chapter_title": "Chương 1: Tên chương",
      "sections": [
        {
          "section_id": "sec_1_1",
          "section_title": "1.1 Tên tiết",
          "assigned_sku_ids": ["SKU-ID-1", "SKU-ID-2"]
        }
      ]
    }
  ]
}
"""


def _heuristic_cluster_book(
    skus_subset: List[Dict[str, Any]],
    target_tag: str,
    book_title: str
) -> Dict[str, Any]:
    """Phân cụm dự phòng dựa trên heuristic rule-based khi không có Gemini API key."""
    title = book_title.strip() or f"Sổ Tay Chuyên Khảo: {target_tag.capitalize()}"
    chap1_skus, chap2_skus, chap3_skus = [], [], []

    for s in skus_subset:
        txt = (s.get("raw_content", "") + " " + " ".join(s.get("tags", []))).lower()
        if any(w in txt for w in ["định nghĩa", "khái niệm", "bản chất", "nguyên lý", "first principles", "tổng quan"]):
            chap1_skus.append(s.get("sku_id"))
        elif any(w in txt for w in ["rủi ro", "tâm lý", "stoploss", "kỷ luật", "quản trị", "asymmetric", "taleb"]):
            chap3_skus.append(s.get("sku_id"))
        else:
            chap2_skus.append(s.get("sku_id"))

    # Đảm bảo không chương nào rỗng nếu có thể
    if not chap1_skus and skus_subset:
        chap1_skus.append(skus_subset[0].get("sku_id"))
    all_assigned = set(chap1_skus + chap2_skus + chap3_skus)
    for s in skus_subset:
        sid = s.get("sku_id")
        if sid not in all_assigned:
            chap2_skus.append(sid)

    return {
        "suggested_title": title,
        "suggested_subtitle": f"Đúc kết từ các ghi chép và trích đoạn chuyên sâu về {target_tag}",
        "chapters": [
            {
                "chapter_id": "chap_1",
                "chapter_title": "Chương 1: Bản Chất Cốt Lõi & Nguyên Lý Nền Tảng",
                "sections": [
                    {
                        "section_id": "sec_1_1",
                        "section_title": "1.1 Định vị bản chất & Tiền đề quan trọng",
                        "assigned_sku_ids": chap1_skus
                    }
                ]
            },
            {
                "chapter_id": "chap_2",
                "chapter_title": "Chương 2: Cấu Trúc, Cơ Chế & Kỹ Thuật Chi Tiết",
                "sections": [
                    {
                        "section_id": "sec_2_1",
                        "section_title": "2.1 Bóc tách cấu trúc và quy luật vận hành",
                        "assigned_sku_ids": chap2_skus
                    }
                ]
            },
            {
                "chapter_id": "chap_3",
                "chapter_title": "Chương 3: Quản Trị Rủi Ro & Chiến Lược Thực Chiến",
                "sections": [
                    {
                        "section_id": "sec_3_1",
                        "section_title": "3.1 Tối ưu vị thế và kiểm soát rủi ro",
                        "assigned_sku_ids": chap3_skus
                    }
                ]
            }
        ]
    }


def ai_auto_cluster_and_build_book(
    username: str,
    target_tag: str,
    book_title: str = "",
    api_keys: Optional[List[str]] = None,
    model_name: str = "gemini-2.5-flash",
    book_subtitle: str = "",
    author: str = ""
) -> Dict[str, Any]:
    """
    Tự động đọc tất cả mảnh ghép (SKU) có chứa target_tag (hoặc toàn bộ kho nếu target_tag rỗng),
    dùng AI để phân cụm ngữ nghĩa, tự động kiến tạo mục lục sách logic và gán các mảnh ghép vào các chương.
    """
    all_skus = get_user_skus(username)
    norm_tag = target_tag.strip().lower()

    if norm_tag and norm_tag != "tất cả":
        matched_skus = [
            s for s in all_skus
            if any(norm_tag in str(t).lower() for t in s.get("tags", []))
            or (norm_tag in s.get("raw_content", "").lower())
            or (norm_tag in s.get("title", "").lower())
        ]
    else:
        matched_skus = list(all_skus)

    if not matched_skus:
        return {
            "success": False,
            "error": f"Không tìm thấy mảnh ghép nào phù hợp với thẻ '{target_tag}'!"
        }

    # Chuẩn bị dữ liệu tóm lược cho AI
    snippet_data = []
    for s in matched_skus:
        snippet_data.append({
            "sku_id": s.get("sku_id"),
            "title": s.get("title", ""),
            "tags": s.get("tags", []),
            "content_preview": s.get("raw_content", "")[:350],
            "user_note": s.get("user_note", "")
        })

    cluster_result = None
    valid_keys = [k.strip() for k in (api_keys or []) if k and k.strip() and not k.startswith("AQ.")]

    if valid_keys and genai is not None:
        user_prompt = f"""Chủ đề trọng tâm của cuốn sách: {target_tag or 'Tri thức tinh hoa'}
Tựa đề dự kiến (nếu có): {book_title or 'Chưa đặt'}

Dưới đây là danh sách {len(snippet_data)} mảnh ghép tri thức cần phân bổ vào các chương:
{json.dumps(snippet_data, ensure_ascii=False, indent=2)}
"""
        candidates = [model_name, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
        for key in valid_keys:
            try:
                genai.configure(api_key=key)
                for cand in candidates:
                    try:
                        model = genai.GenerativeModel(
                            model_name=cand,
                            system_instruction=BOOK_CLUSTERING_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        resp = model.generate_content(user_prompt, request_options={"timeout": 45})
                        if resp and resp.text:
                            text = resp.text.strip()
                            if text.startswith("```"):
                                lines = text.splitlines()
                                if len(lines) >= 2 and lines[-1].startswith("```"):
                                    text = "\n".join(lines[1:-1]).strip()
                            data = json.loads(text)
                            if isinstance(data, dict) and "chapters" in data:
                                cluster_result = data
                                break
                    except Exception:
                        continue
                if cluster_result:
                    break
            except Exception:
                continue

    if not cluster_result:
        cluster_result = _heuristic_cluster_book(matched_skus, target_tag, book_title)

    # Khởi tạo dự án sách mới
    final_title = book_title.strip() or cluster_result.get("suggested_title", f"Sách Chuyên Đề: {target_tag}")
    final_subtitle = book_subtitle.strip() or cluster_result.get("suggested_subtitle", "")

    # Chuẩn hóa cấu trúc outline cho project
    outline_for_project = []
    sku_assignment_map = {}  # sku_id -> (chap_id, chap_title, sec_id, sec_title, order)

    for idx_c, chap in enumerate(cluster_result.get("chapters", []), 1):
        c_id = chap.get("chapter_id") or f"chap_{idx_c}"
        c_title = chap.get("chapter_title", f"Chương {idx_c}")
        sec_list = []
        for idx_s, sec in enumerate(chap.get("sections", []), 1):
            s_id = sec.get("section_id") or f"{c_id}_sec_{idx_s}"
            s_title = sec.get("section_title", f"{idx_c}.{idx_s} Tiểu mục")
            sec_list.append({
                "section_id": s_id,
                "section_title": s_title
            })
            for ord_idx, sku_id in enumerate(sec.get("assigned_sku_ids", []), 1):
                sku_assignment_map[sku_id] = (c_id, c_title, s_id, s_title, ord_idx)
        outline_for_project.append({
            "chapter_id": c_id,
            "chapter_title": c_title,
            "sections": sec_list
        })

    # Tạo Book Project
    new_proj = create_book_project(
        username=username,
        title=final_title,
        subtitle=final_subtitle,
        author=author or username,
        description=f"Cuốn sách được tổng hợp tự động từ {len(matched_skus)} mảnh ghép tri thức về '{target_tag}'.",
        outline=outline_for_project
    )
    new_pid = new_proj.get("project_id")

    # Cập nhật vị trí cho từng SKU
    assigned_count = 0
    all_user_skus = get_user_skus(username)
    for s in all_user_skus:
        sid = s.get("sku_id")
        if sid in sku_assignment_map:
            c_id, c_title, s_id, s_title, ord_num = sku_assignment_map[sid]
            s["book_project_id"] = new_pid
            s["target_chapter_id"] = c_id
            s["target_chapter"] = c_title
            s["target_section_id"] = s_id
            s["target_section"] = s_title
            s["sort_order"] = ord_num
            assigned_count += 1
        elif sid in [m.get("sku_id") for m in matched_skus]:
            # SKU thuộc tag nhưng AI chưa gán -> đưa vào chương 1 tiết 1
            first_c = outline_for_project[0] if outline_for_project else {}
            first_s = (first_c.get("sections") or [{}])[0]
            s["book_project_id"] = new_pid
            s["target_chapter_id"] = first_c.get("chapter_id", "")
            s["target_chapter"] = first_c.get("chapter_title", "")
            s["target_section_id"] = first_s.get("section_id", "")
            s["target_section"] = first_s.get("section_title", "")
            s["sort_order"] = 99
            assigned_count += 1

    save_user_skus(username, all_user_skus)

    return {
        "success": True,
        "project": new_proj,
        "assigned_count": assigned_count,
        "total_chapters": len(outline_for_project)
    }

