# -*- coding: utf-8 -*-
"""
Export Project Context for AI Agents.
Tự động quét cấu trúc dự án, thống kê dữ liệu, kiến trúc CSDL và trạng thái tiến độ
xuất ra file PROJECT_CONTEXT.md để bất kỳ AI Agent nào đọc vào cũng hiểu toàn diện dự án.
TUYỆT ĐỐI KHÔNG XUẤT CÁC THÔNG TIN NHẠY CẢM (Mật khẩu, hash, API keys, .env secrets).
"""

from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Đảm bảo in tiếng Việt có dấu an toàn trên terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT_DIR / "PROJECT_CONTEXT.md"

# Thư mục và file cần bỏ qua khi vẽ cây thư mục (bảo vệ thông tin riêng tư & bảo mật)
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "scratch",
    "cache",
    ".mypy_cache",
    ".pytest_cache",
    "histories",
}
EXCLUDE_FILES = {
    ".env",
    "secrets.toml",
    ".DS_Store",
}
EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".bak",
}


def get_git_info() -> Dict[str, str]:
    """Lấy thông tin Git hiện tại."""
    info = {
        "branch": "unknown",
        "commit": "unknown",
        "date": "unknown",
        "remote": "unknown",
        "status": "clean",
    }
    try:
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            info["branch"] = res.stdout.strip()

        res = subprocess.run(
            ["git", "log", "-1", "--format=%h - %s (%ci)"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            info["commit"] = res.stdout.strip()

        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            info["remote"] = res.stdout.strip()

        res = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            modified_count = len(res.stdout.strip().splitlines()) if res.stdout.strip() else 0
            info["status"] = f"Clean (no uncommitted changes)" if modified_count == 0 else f"{modified_count} uncommitted file(s)"
    except Exception:
        pass
    return info


def generate_tree(dir_path: Path, prefix: str = "", max_depth: int = 4, current_depth: int = 1) -> List[str]:
    """Sinh cây thư mục trực quan và an toàn."""
    if current_depth > max_depth:
        return []

    lines = []
    try:
        items = sorted(
            list(dir_path.iterdir()),
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError:
        return []

    filtered_items = []
    for item in items:
        if item.name in EXCLUDE_DIRS or item.name in EXCLUDE_FILES:
            continue
        if item.suffix in EXCLUDE_EXTENSIONS:
            continue
        filtered_items.append(item)

    total = len(filtered_items)
    for i, item in enumerate(filtered_items):
        is_last = (i == total - 1)
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if item.is_dir():
            lines.append(f"{prefix}{connector}📂 **{item.name}/**")
            sub_lines = generate_tree(
                item,
                prefix + child_prefix,
                max_depth=max_depth,
                current_depth=current_depth + 1,
            )
            lines.extend(sub_lines)
        else:
            size_kb = item.stat().st_size / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
            lines.append(f"{prefix}{connector}📄 `{item.name}` *({size_str})*")

    return lines


def parse_data_statistics() -> Dict[str, Any]:
    """Phân tích và thống kê các file dữ liệu trong thư mục data/ mà không làm rò rỉ dữ liệu cá nhân."""
    stats: Dict[str, Any] = {
        "cases_total": 0,
        "cases_by_group": {},
        "models_count": 0,
        "principles_count": 0,
        "curriculum_weeks": 0,
        "lessons_count": 0,
        "bilingual_books": [],
    }

    data_dir = ROOT_DIR / "data"
    if not data_dir.exists():
        return stats

    # 1. Thống kê cases
    case_files = sorted(list(data_dir.glob("cases_*.json")))
    for cf in case_files:
        try:
            with open(cf, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                meta = cdata.get("metadata", {})
                grp = meta.get("group", cf.stem.replace("cases_", ""))
                title = meta.get("title", cf.name)
                cases_list = cdata.get("cases", [])
                count = len(cases_list)
                stats["cases_total"] += count
                stats["cases_by_group"][f"Nhóm {grp} - {title}"] = {
                    "file": cf.name,
                    "count": count,
                    "target_age": meta.get("target_age", "N/A"),
                }
        except Exception as e:
            stats["cases_by_group"][cf.name] = {"error": str(e)}

    # 2. Thống kê mental models
    models_file = data_dir / "core_mental_models.json"
    if models_file.exists():
        try:
            with open(models_file, "r", encoding="utf-8") as f:
                mdata = json.load(f)
                stats["models_count"] = len(mdata.get("models", [])) if isinstance(mdata, dict) else len(mdata)
        except Exception:
            pass

    # 3. Thống kê principles
    kb_file = data_dir / "knowledge_base.json"
    if kb_file.exists():
        try:
            with open(kb_file, "r", encoding="utf-8") as f:
                kbdata = json.load(f)
                items = kbdata.get("principles", []) if isinstance(kbdata, dict) else kbdata
                stats["principles_count"] = len(items)
        except Exception:
            pass

    # 4. Thống kê curriculum
    curr_file = data_dir / "curriculum_12w.json"
    if curr_file.exists():
        try:
            with open(curr_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                weeks = cdata.get("weeks", []) if isinstance(cdata, dict) else cdata
                stats["curriculum_weeks"] = len(weeks)
        except Exception:
            pass

    # 5. Thống kê lessons (theo các track K12 và Adult)
    lessons_file = data_dir / "lessons.json"
    if lessons_file.exists():
        try:
            with open(lessons_file, "r", encoding="utf-8") as f:
                ldata = json.load(f)
                tracks_meta = ldata.get("tracks_meta", {})
                total_l = 0
                track_counts = {}
                for t_key in tracks_meta.keys():
                    t_lessons = ldata.get(t_key, [])
                    if isinstance(t_lessons, list):
                        cnt = len(t_lessons)
                        total_l += cnt
                        t_name = tracks_meta[t_key].get("name", t_key)
                        track_counts[t_name] = cnt
                stats["lessons_count"] = total_l
                stats["lessons_by_track"] = track_counts
        except Exception:
            pass

    # 6. Thống kê bilingual books
    bilingual_dir = data_dir / "bilingual_books"
    if bilingual_dir.exists():
        for bf in bilingual_dir.glob("*.json"):
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    bdata = json.load(f)
                    parts = bdata.get("parts", [])
                    total_chaps = 0
                    total_scenes = 0
                    for p in parts:
                        chaps = p.get("chapters", [])
                        total_chaps += len(chaps)
                    stats["bilingual_books"].append({
                        "file": bf.name,
                        "title": bdata.get("title_vi") or bdata.get("title_en") or bf.stem,
                        "author": bdata.get("author", "N/A"),
                        "parts_count": len(parts),
                        "chapters_count": total_chaps,
                        "total_scenes": total_scenes,
                    })
            except Exception:
                pass

    # 7. Thống kê từ vựng tinh hoa (elite_vocab)
    vocab_file = data_dir / "elite_vocab.json"
    if vocab_file.exists():
        try:
            with open(vocab_file, "r", encoding="utf-8") as f:
                vdata = json.load(f)
                stats["elite_vocab_count"] = len(vdata.get("vocab_list", []))
                stats["elite_vocab_pillars"] = len(vdata.get("pillars", []))
                stats["elite_vocab_topics"] = sum(len(p.get("topics", [])) for p in vdata.get("pillars", []))
        except Exception:
            pass

    return stats



def parse_pages_info() -> List[Dict[str, str]]:
    """Phân tích các trang trong thư mục pages/."""
    pages_dir = ROOT_DIR / "pages"
    pages_info = []
    if not pages_dir.exists():
        return pages_info

    for pf in sorted(pages_dir.glob("*.py")):
        title = pf.stem
        desc = ""
        try:
            with open(pf, "r", encoding="utf-8") as f:
                content = f.read(1500)
                doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if doc_match:
                    desc = doc_match.group(1).strip().splitlines()[0]
                else:
                    doc_match_single = re.search(r"'''(.*?)'''", content, re.DOTALL)
                    if doc_match_single:
                        desc = doc_match_single.group(1).strip().splitlines()[0]
        except Exception:
            pass

        pages_info.append({
            "filename": pf.name,
            "stem": pf.stem,
            "description": desc or "Trang nghiệp vụ ứng dụng",
        })
    return pages_info


def build_markdown_document() -> str:
    """Xây dựng nội dung tài liệu Markdown hoàn chỉnh."""
    git_info = get_git_info()
    data_stats = parse_data_statistics()
    pages_info = parse_pages_info()
    tree_lines = generate_tree(ROOT_DIR, max_depth=3)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []

    # =========================================================================
    # Header & Meta
    # =========================================================================
    md.append("# 🧠 ELITE THINKING FAMILY V2 — PROJECT CONTEXT & ARCHITECTURE SPEC")
    md.append("")
    md.append("> **Dành cho AI Agent (Gemini, Claude, ChatGPT, Cursor, Windsurf, Antigravity...)**:")
    md.append("> Đây là tài liệu duy nhất chứa toàn bộ thông tin kiến trúc, vị trí source code, luồng ứng dụng, cơ sở dữ liệu và **tiến độ thực tế (cái gì đã xong, cái gì đang làm, cái gì chưa xong)** của dự án **Elite Thinking Family v2**.")
    md.append("> Đọc file này là Agent có 100% bối cảnh để bắt tay vào làm việc ngay mà không cần rà soát lại toàn bộ cây thư mục.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 📌 1. THÔNG TIN TỔNG QUAN & METADATA DỰ ÁN")
    md.append("")
    md.append(f"- **Tên Dự Án**: `Elite Thinking Family v2`")
    md.append(f"- **Mục đích**: Nền tảng huấn luyện tư duy tinh hoa (First Principles, Charlie Munger Mental Models, Richard Feynman Technique, Elon Musk Reasoning) dành cho Gia đình (Học sinh Wellspring K12 & Người lớn/Chuyên gia Tài chính/CKVN).")
    md.append(f"- **Công nghệ lõi**: Streamlit (Multipage Dynamic Router) + Google Gemini API (Multi-Key Failover) + Supabase PostgreSQL (Kèm Fallback Local JSON).")
    md.append(f"- **Thời điểm cập nhật**: `{now_str}`")
    md.append(f"- **Git Repository**: `{git_info['remote']}`")
    md.append(f"- **Git Branch**: `{git_info['branch']}`")
    md.append(f"- **Commit gần nhất**: `{git_info['commit']}`")
    md.append(f"- **Trạng thái Git**: `{git_info['status']}`")
    md.append("")
    md.append("---")
    md.append("")

    # =========================================================================
    # 2. Kiến trúc & Vị trí ứng dụng
    # =========================================================================
    md.append("## 🗺️ 2. VỊ TRÍ ỨNG DỤNG & CƠ CHẾ ROUTING")
    md.append("")
    md.append("### 2.1 File khởi chạy chính (Entrypoint)")
    md.append("- **File**: `app.py`")
    md.append("- **Đường dẫn**: `app.py` (tại thư mục gốc)")
    md.append("- **Cơ chế hoạt động**:")
    md.append("  1. Gọi `utils.auth.init_auth_state()` khởi tạo phiên làm việc trên `st.session_state`.")
    md.append("  2. **Cổng bảo mật tiền đăng nhập (Pre-login Gate)**:")
    md.append("     - Khi chưa đăng nhập: Ẩn hoàn toàn sidebar navigation menu (`position='hidden'`), chỉ render form đăng nhập `render_login()`.")
    md.append("     - Khi đã đăng nhập: Khởi tạo router điều hướng động (`st.navigation`) hiển thị sidebar phân loại theo cụm nghiệp vụ.")
    md.append("  3. **Phân quyền vai trò (Role-Based Access Control - RBAC)**:")
    md.append("     - User thường: Chỉ thấy các trang học tập, luyện tập, tra cứu, sổ tay tri thức.")
    md.append("     - Role `admin`: Tự động kích hoạt thêm trang `pages/9_admin.py` trong menu `👑 Quản trị`.")
    md.append("")
    md.append("### 2.2 Sơ đồ Cụm Trang Điều Hướng (Navigation Map)")
    md.append("")
    md.append("| Cụm Danh Mục | Icon | File Trang | Chức Năng Chính | Quyền Hạn |")
    md.append("|---|---|---|---|---|")
    md.append("| **🧭 Định hướng** | 🧭 | `app.py` (Home) | Bản đồ 7 bước huấn luyện, 3 triết lý cốt lõi, chọn Track học tập | Mọi User |")
    md.append("| | 📅 | `pages/0_lo_trinh_12_tuan.py` | Lộ trình huấn luyện chuẩn 12 tuần, nhiệm vụ ngày/tuần, lưu tiến độ | Mọi User |")
    md.append("| **🧠 Lăng kính & Mô hình** | 🌐 | `pages/1_the_cuoc_elite.py` | 5 kỷ nguyên tiến hóa, 8 mật mã vận hành, AI Macro Radar | Mọi User |")
    md.append("| | 📖 | `pages/2_9_che_do_tu_duy.py` | 9 chế độ tư duy siêu việt (First Principles, Inversion, 2nd Order...) | Mọi User |")
    md.append("| | 🕸️ | `pages/3_88_mo_hinh.py` | 88 mô hình tâm trí Munger chia 6 trụ cột khoa học | Mọi User |")
    md.append("| | 📚 | `pages/4_thu_vien_nguyen_ly.py` | 100 định luật khoa học bất biến kèm tiêu chuẩn khả bác Karl Popper | Mọi User |")
    md.append("| **⚔️ Rèn luyện & Thực chiến**| ⚡ | `pages/5_dau_truong.py` | Flashcards 5s, 731 câu trắc nghiệm, Dynamic AI Quiz, Feynman Challenge | Mọi User |")
    md.append("| | 🎓 | `pages/6_dao_tao.py` | Bài tập tự luận đa tầng K12 Wellspring & Người lớn CKVN + AI Mentor | Mọi User |")
    md.append("| | 🚀 | `pages/7_phan_ra.py` | AI bóc tách vấn đề thực tế bằng 9 lăng kính, tìm đòn bẩy bất đối xứng | Mọi User |")
    md.append("| | 🎯 | `pages/11_case_thuc_chien.py` | Ngân hàng 150+ Case thực tế đa lĩnh vực (Toán, CKVN, Sự nghiệp...) | Mọi User |")
    md.append("| | 📝 | `pages/8_lich_su.py` | Nhật ký quyết định (Decision Journal), biểu đồ tiến bộ, lịch sử bài nộp | Mọi User |")
    md.append("| **💡 Sổ tay & Tri thức** | 💡 | `pages/10_so_tay_tri_thuc.py` | Sổ tay Second Brain ghi chú Markdown theo mô hình tư duy | Mọi User |")
    md.append("| | 🧬 | `pages/12_tieng_anh_elite.py` | Học từ vựng theo Gốc từ Lego (Latin/Hy Lạp), Mỏ neo thị giác, 100% Zero-API | Mọi User |")
    md.append("| **👑 Quản trị** | 👑 | `pages/9_admin.py` | Quản lý users, reset password, theo dõi lịch sử và telemetry toàn hệ thống | **Chỉ Admin** |")
    md.append("")
    md.append("### 2.3 Các Module & Tiện ích Mở rộng (Extensions & Archive)")
    md.append("- **`extension/`**: Bản đóng gói case thực chiến 150+ độc lập (kèm file README hướng dẫn tích hợp vào repo khác).")
    md.append("- **`archive/`**: Thư mục lưu trữ mã nguồn tạm ngưng (`archive/pages/12_doc_song_ngu.py` - bản đọc sách song ngữ cũ) kèm `archive/README.md` ghi nhận lý do và định hướng phục hồi.")
    md.append("- **`extention_read_english/`**: Pipeline tiền xử lý sách (`bilingual_pipeline.py`) đọc PDF gốc đối chiếu tiếng Anh/Việt, làm sạch văn bản, phân đoạn Macro-Scenes.")
    md.append("### 2.4 Danh Mục Thư Viện Tiện Ích Lõi (`utils/`)")
    md.append("")
    md.append("| Module File | Chức Năng Chính | Vai Trò Kỹ Thuật |")
    md.append("|---|---|---|")
    md.append("| `utils/ai_engine.py` | Giao tiếp Gemini API | Multi-key rotation, failover khi dính 429, cache phản hồi |")
    md.append("| `utils/app_common.py` | Shared bootstrap & Sidebar | Kiểm tra đăng nhập, nạp API keys, render sidebar dùng chung |")
    md.append("| `utils/auth.py` | Xác thực PBKDF2 & Phân quyền | Hash 200,000 vòng, đổi mật khẩu, đồng bộ Supabase & users.json |")
    md.append("| `utils/bilingual_manager.py`| Quản lý Đọc Song Ngữ | JIT rolling translation, căn chỉnh từng đoạn, cache dịch thuật |")
    md.append("| `utils/curriculum.py` | Quản lý Lộ trình 12 tuần | Tải nội dung tuần, lưu/đọc tiến độ hoàn thành theo user |")
    md.append("| `utils/daily_workout.py` | Rèn luyện Hàng ngày & Streak| Tính toán streak, câu hỏi khởi động ngày, bài tập vi mô |")
    md.append("| `utils/db.py` | Kết nối Supabase | Khởi tạo client Supabase, fallback an toàn sang local JSON |")
    md.append("| `utils/decision_journal.py`| Nhật ký Quyết định | Ghi chép bối cảnh, dự phóng, đánh giá hậu nghiệm các quyết định |")
    md.append("| `utils/diagnostic.py` | Trắc nghiệm Chẩn đoán | Đo lường thiên kiến nhận thức, phong cách tư duy của người học |")
    md.append("| `utils/knowledge.py` | Thư viện 100 Nguyên lý | Tải dữ liệu, tìm kiếm, lọc theo trường phái khoa học |")
    md.append("| `utils/macro_evolution.py` | Radar Thế cuộc & Kỷ nguyên | Phân tích 5 kỷ nguyên tiến hóa, 8 mật mã vận hành ngầm |")
    md.append("| `utils/mental_models.py` | 88 Mô hình Tâm trí Munger | Tải 88 mô hình, phân nhóm theo 6 trụ cột khoa học, tìm kiếm |")
    md.append("| `utils/notes_manager.py` | Second Brain / Sổ tay tri thức| CRUD ghi chú Markdown cá nhân, gắn thẻ theo mô hình tư duy |")
    md.append("| `utils/quiz_engine.py` | Ngân hàng 731 câu Trắc nghiệm| Sinh đề thi trắc nghiệm, chấm điểm, giải thích đáp án chi tiết |")
    md.append("| `utils/training.py` | Huấn luyện Đào tạo & AI Mentor| Chấm điểm bài tự luận K12/Adult, sinh phản biện First Principles |")
    md.append("| `utils/vocab_manager.py` | Quản lý Từ vựng Tinh hoa | Tải từ vựng tĩnh, theo dõi mastery, thống kê, zero-API |")
    md.append("")
    md.append("---")
    md.append("")

    # =========================================================================
    # 3. Cơ sở dữ liệu & Lưu trữ (Persistence)
    # =========================================================================
    md.append("## 💾 3. CƠ SỞ DỮ LIỆU & KIẾN TRÚC LƯU TRỮ (PERSISTENCE)")
    md.append("")
    md.append("Dự án sử dụng cơ chế **Kiến trúc Kép (Dual Persistence Architecture)** đảm bảo app luôn chạy được cả khi có hoặc không có mạng/cloud database:")
    md.append("1. **Ưu tiên 1 (Production / Streamlit Cloud)**: **Supabase PostgreSQL**.")
    md.append("2. **Ưu tiên 2 (Local Development / Offline)**: **Local JSON**.")
    md.append("")
    md.append("### 3.1 Cấu trúc Bảng Supabase PostgreSQL (`supabase/schema.sql`)")
    md.append("")
    md.append("```sql")
    md.append("-- 1. Bảng người dùng (Tự quản lý Auth bằng PBKDF2, không phụ thuộc Supabase Auth)")
    md.append("create table if not exists public.app_users (")
    md.append("  username text primary key,")
    md.append("  password_hash text not null,       -- PBKDF2-HMAC-SHA256 (200,000 iterations, 16-byte salt)")
    md.append("  role text not null default 'user', -- 'admin' hoặc 'user'")
    md.append("  display_name text,")
    md.append("  created_at timestamptz not null default now(),")
    md.append("  updated_at timestamptz not null default now()")
    md.append(");")
    md.append("")
    md.append("-- 2. Bảng lưu trữ toàn bộ lịch sử học tập của từng người dùng (Blob JSONB bền vững)")
    md.append("create table if not exists public.user_histories (")
    md.append("  username text primary key references public.app_users(username) on delete cascade,")
    md.append("  data jsonb not null default '{}'::jsonb,  -- analyses, training, quiz, diagnostic, decisions...")
    md.append("  updated_at timestamptz not null default now()")
    md.append(");")
    md.append("```")
    md.append("")
    md.append("#### Các trường dữ liệu bên trong cột `data jsonb` của `user_histories`:")
    md.append("- `analyses`: Danh sách các phân tích vấn đề (Tab 7 Phân rã).")
    md.append("- `training_submissions`: Lịch sử bài nộp đào tạo có AI Mentor phản biện (Tab 6 Đào tạo).")
    md.append("- `quiz_history`: Lịch sử kết quả làm bài trắc nghiệm / flashcards (Tab 5 Đấu trường).")
    md.append("- `feynman_submissions`: Kết quả giải thích nguyên lý theo kỹ thuật Feynman.")
    md.append("- `diagnostic_history`: Kết quả kiểm tra trắc nghiệm thiên kiến nhận thức & phong cách tư duy.")
    md.append("- `decisions`: Nhật ký các quyết định quan trọng (Decision Journal).")
    md.append("- `daily_workouts`: Dữ liệu chuỗi rèn luyện ngày (Daily Streak).")
    md.append("- `curriculum_progress`: Tiến độ đánh dấu hoàn thành các tuần trong lộ trình 12 tuần.")
    md.append("- `notes`: Ghi chú cá nhân trong Sổ tay tri thức (Second Brain).")
    md.append("- `elite_vocab_mastery`: Trạng thái học và làm chủ từ vựng tinh hoa (đã thông suốt, gắn sao, số lần ôn, kết quả quiz) (Tab 12).")
    md.append("")
    md.append("### 3.2 Cơ chế Lưu trữ Fallback Local JSON")
    md.append("Nếu không có `SUPABASE_URL` và `SUPABASE_KEY` trong môi trường:")
    md.append("- Danh sách tài khoản: Đọc và ghi trực tiếp vào `data/users.json`.")
    md.append("- Lịch sử từng người dùng: Đọc và ghi tại `data/histories/<username>.json` (được `.gitignore` bảo vệ).")
    md.append("- Thư viện điều phối: `utils/db.py`, `utils/auth.py`, `utils/app_common.py`.")
    md.append("")
    md.append("### 3.3 Thống Kê Ngân Hàng Dữ Liệu Tĩnh (`data/`)")
    md.append(f"- **Tổng số Case Thực Chiến**: **{data_stats['cases_total']} cases** (chia làm 6 nhóm chuyên sâu):")
    for grp_name, ginfo in data_stats["cases_by_group"].items():
        md.append(f"  - `{grp_name}`: **{ginfo.get('count', 0)} case** (File: `{ginfo.get('file', '')}`, Đối tượng: {ginfo.get('target_age', 'Mọi đối tượng')})")
    md.append(f"- **Số Mô hình Tâm trí Munger (`core_mental_models.json`)**: **{data_stats['models_count']} mô hình**.")
    md.append(f"- **Số Định luật Khoa học (`knowledge_base.json`)**: **{data_stats['principles_count']} nguyên lý**.")
    if "lessons_by_track" in data_stats and data_stats["lessons_by_track"]:
        md.append(f"- **Bài học Đào tạo (`lessons.json`)**: **{data_stats['lessons_count']} bài học** phân bổ qua các track chuyên sâu:")
        for tname, tcnt in data_stats["lessons_by_track"].items():
            md.append(f"  - `{tname}`: **{tcnt} bài học**")
    else:
        md.append(f"- **Bài học Đào tạo (`lessons.json`)**: **{data_stats['lessons_count']} bài học**.")

    md.append(f"- **Từ Vựng Tư Duy Tinh Hoa (`data/elite_vocab.json`)**: **{data_stats.get('elite_vocab_count', 0)} từ vựng cốt lõi** phân bổ trên **{data_stats.get('elite_vocab_pillars', 3)} Cột trụ lớn** và **{data_stats.get('elite_vocab_topics', 76)} Chủ đề / Mô hình tư duy** kết nối 1-1 với Tab 2 (9 Chế độ), Tab 3 (88 Munger), Tab 4 (100 Nguyên lý) (Bóc tách gốc Lego Latinh/Hy Lạp, Mỏ neo thị giác, Cặp đối kháng, 100% Zero-API).")


    if data_stats["bilingual_books"]:
        md.append("- **Sách Song Ngữ Siêu Học (`data/bilingual_books/`)**:")
        for bb in data_stats["bilingual_books"]:
            md.append(f"  - 📚 **{bb['title']}** (Tác giả: *{bb['author']}*): **{bb['chapters_count']} chương**, **{bb['total_scenes']} macro-scenes** căn chỉnh Anh - Việt (File: `{bb['file']}`).")
    md.append("")
    md.append("### 3.4 Chính Sách Bảo Mật & Thông Tin Nhạy Cảm (Security Rules)")
    md.append("> [!IMPORTANT]")
    md.append("> **TUYỆT ĐỐI TUÂN THỦ CÁC QUY TẮC BẢO MẬT SAU KHI LÀM VIỆC VỚI DỰ ÁN**:")
    md.append("> 1. **KHÔNG BAO GIỜ COMMIT** file `.env`, `secrets.toml`, hay bất kỳ credential nào vào Git.")
    md.append("> 2. **KHÔNG BAO GIỜ HARDCODE** API key hay password vào code. Mọi API key phải gọi qua `utils.app_common.get_configured_api_keys()`.")
    md.append("> 3. Mật khẩu người dùng được băm bằng PBKDF2-HMAC-SHA256 với Salt 16 bytes ngẫu nhiên và 200.000 vòng băm (`utils/auth.py`). Tuyệt đối không lưu mật khẩu dạng plain text.")
    md.append("> 4. File này (`PROJECT_CONTEXT.md`) và script xuất tự động đã lọc bỏ hoàn toàn các chuỗi mật khẩu, token, API keys, cookie và private data.")
    md.append("")
    md.append("---")
    md.append("")

    # =========================================================================
    # 4. Trạng Thái & Tiến Độ Dự Án
    # =========================================================================
    md.append("## 📊 4. TRẠNG THÁI & TIẾN ĐỘ DỰ ÁN (PROJECT STATUS & PROGRESS)")
    md.append("")
    md.append("Bảng kiểm toán chi tiết tính năng giúp Agent nắm rõ: **Cái gì đã hoàn thành 100%, cái gì đang hoàn thiện, cái gì trong Backlog**.")
    md.append("")
    md.append("### 4.1 Tính Năng Đã Hoàn Thành 100% & Ổn Định (Production Ready) ✅")
    md.append("")
    md.append("| Phân Hệ | File Source Code | Trạng Thái | Mô Tả & Năng Lực Đã Đạt |")
    md.append("|---|---|---|---|")
    md.append("| **Multipage Router & Security Gate** | `app.py`, `utils/app_common.py` | ✅ Hoàn thành | Router động; ẩn menu khi chưa đăng nhập; phân quyền Admin/User; auto bootstrap; quản lý session state. |")
    md.append("| **Hệ thống Xác thực PBKDF2** | `utils/auth.py`, `supabase/schema.sql` | ✅ Hoàn thành | Băm mật khẩu 200,000 vòng; đổi mật khẩu an toàn; hỗ trợ đồng bộ cả Supabase và local `users.json`. |")
    md.append("| **Đồng bộ Dữ liệu Kép (Dual DB)** | `utils/db.py`, `supabase/schema.sql` | ✅ Hoàn thành | Tự động nhận diện Supabase Cloud; fallback mượt mà sang Local JSON; đồng bộ dữ liệu người dùng không gián đoạn. |")
    md.append("| **Xoay vòng Gemini API Keys** | `utils/app_common.py`, `utils/ai_engine.py` | ✅ Hoàn thành | Tự động luân chuyển đa key (`GEMINI_API_KEY_1..9`); tự động failover sang key kế tiếp khi gặp 429 Rate Limit. |")
    md.append("| **Lộ trình 12 Tuần** | `pages/0_lo_trinh_12_tuan.py`, `utils/curriculum.py` | ✅ Hoàn thành | Toàn bộ 12 tuần có bài học, mục tiêu, bài tập thực hành; lưu tiến độ từng user lên Supabase. |")
    md.append("| **Thế Cuộc & AI Radar** | `pages/1_the_cuoc_elite.py`, `utils/macro_evolution.py` | ✅ Hoàn thành | 5 kỷ nguyên, 8 mật mã, giao diện trực quan hóa, phân tích cục diện thời đại. |")
    md.append("| **9 Chế Độ Tư Duy** | `pages/2_9_che_do_tu_duy.py` | ✅ Hoàn thành | First Principles, Inversion, 2nd Order, Bayes, Đa quy mô thời gian, v.v. |")
    md.append("| **88 Mô Hình Munger** | `pages/3_88_mo_hinh.py`, `utils/mental_models.py` | ✅ Hoàn thành | Đầy đủ 6 nhóm khoa học; lọc theo nhóm; giải nghĩa chi tiết; ví dụ thực tiễn. |")
    md.append("| **Thư Viện 100 Nguyên Lý** | `pages/4_thu_vien_nguyen_ly.py`, `utils/knowledge.py` | ✅ Hoàn thành | 100 nguyên lý khoa học bất biến; công thức toán học; tiêu chuẩn khả bác Popper. |")
    md.append("| **Đấu Trường & Trắc Nghiệm** | `pages/5_dau_truong.py`, `utils/quiz_engine.py` | ✅ Hoàn thành | Flashcard 5s; 731 câu trắc nghiệm chuẩn; Dynamic AI Quiz; Thử thách Feynman; Daily Streak. |")
    md.append("| **Đào Tạo 2 Nhánh Gia Đình** | `pages/6_dao_tao.py`, `utils/training.py` | ✅ Hoàn thành | Track 1 K12 Wellspring (lớp 6, 9, 10); Track 2 Người lớn/CKVN; AI Mentor chấm điểm & phản biện. |")
    md.append("| **Phân Rã Vấn Đề Thực Chiến** | `pages/7_phan_ra.py`, `utils/ai_engine.py` | ✅ Hoàn thành | Nhập vấn đề bất kỳ; AI bóc tách qua 9 lăng kính; đề xuất giải pháp đòn bẩy bất đối xứng; lưu lịch sử. |")
    md.append("| **Lịch Sử & Nhật Ký Quyết Định** | `pages/8_lich_su.py`, `utils/decision_journal.py` | ✅ Hoàn thành | Decision Journal ghi chép & đánh giá quyết định; biểu đồ theo dõi chuỗi luyện tập và bài nộp. |")
    md.append("| **Trang Quản Trị Hệ Thống** | `pages/9_admin.py` | ✅ Hoàn thành | Chỉ admin thấy; tạo user mới, reset mật khẩu, xem thống kê hoạt động toàn hệ thống. |")
    md.append("| **Sổ Tay Tri Thức (Second Brain)**| `pages/10_so_tay_tri_thuc.py`, `utils/notes_manager.py` | ✅ Hoàn thành | Ghi chú Markdown theo mô hình tư duy, phân loại, tìm kiếm toàn văn, lưu trên Supabase/local. |")
    md.append("| **Từ Vựng Tinh Hoa (Zero-API)** | `pages/12_tieng_anh_elite.py`, `utils/vocab_manager.py` | ✅ Hoàn thành | 417 từ vựng, 3 cột trụ (9 Chế độ, 88 Munger, 100 Nguyên lý), 76 chủ đề; bộ lọc 2 tầng liên kết 1-1; bẻ khóa qua gốc từ Lego, mỏ neo thị giác, flashcard active recall, trắc nghiệm cloze test. 100% Zero-API. |")

    md.append("")
    md.append("### 4.2 Tính Năng Đang Phát Triển / Cần Hoàn Thiện Thêm (In Progress) 🔄")
    md.append("")
    md.append("1. **Tái cấu trúc Trải nghiệm Đọc Sách & Audio Podcast (`archive/pages/12_doc_song_ngu.py`)**:")
    md.append("   - *Hiện trạng*: Đã lưu trữ an toàn trang Đọc song ngữ cũ vào `archive/` kèm `archive/README.md` để tập trung 100% tài nguyên cho việc ghi nhớ từ vựng tinh hoa qua gốc từ Lego.")
    md.append("   - *Cần làm tiếp*: Khi người học đã tích lũy đủ vốn từ vựng nền tảng, có thể phục hồi lại tính năng đọc sách kèm âm thanh Voice TTS / AI Podcast tóm tắt.")
    md.append("2. **Đồng bộ hóa 100% dữ liệu tĩnh lên Supabase Storage/Tables**:")
    md.append("   - *Hiện trạng*: Dữ liệu biến động (`app_users`, `user_histories`, `elite_vocab_mastery`) đã lưu Supabase chuẩn hóa. Các file JSON bài tập và cases vẫn nạp từ thư mục `data/` trong repo.")
    md.append("   - *Cần làm tiếp*: Nếu cần quản trị nội dung (CMS) từ xa không cần git push, có thể viết thêm API/script đồng bộ các file `cases_*.json` lên bảng Supabase.")
    md.append("3. **Bộ Kiểm Thử Tự Động Hóa (Automated Test Suite / CI)**:")
    md.append("   - *Hiện trạng*: Đã có script test E2E thủ công (`scratch/`) xác nhận hoạt động ổn định.")
    md.append("   - *Cần làm tiếp*: Thiết lập bộ test tự động bằng `pytest` kiểm tra các hàm trong `utils/` (auth, ai_engine, vocab_manager, db fallback).")
    md.append("")
    md.append("### 4.3 Kế Hoạch Tương Lai / Ý Tưởng Nâng Cấp (Backlog / Roadmap) 📋")
    md.append("")
    md.append("1. **Tạo Podcast / Voice Audio AI (Text-to-Speech)**:")
    md.append("   - Tích hợp sinh âm thanh giọng đọc bản ngữ cho các đoạn văn trong Tab 12 Đọc Song Ngữ hoặc tóm tắt Feynman.")
    md.append("2. **Family Leaderboard & Gamification nâng cao**:")
    md.append("   - Bảng vàng thành tích thi đua giải bài tập giữa các thành viên gia đình (Wellspring K12).")
    md.append("3. **Tối ưu hóa Giao diện Di động (Mobile PWA Experience)**:")
    md.append("   - Tinh chỉnh CSS responsive để hiển thị trên trình duyệt Safari/Chrome điện thoại tối ưu hơn.")
    md.append("")
    md.append("---")
    md.append("")

    # =========================================================================
    # 5. Cây Cấu Trúc Dự Án
    # =========================================================================
    md.append("## 📂 5. CÂY CẤU TRÚC DỰ ÁN CHI TIẾT (DIRECTORY TREE)")
    md.append("")
    md.append("```text")
    md.append("elite_thinking/")
    for line in tree_lines:
        md.append(line)
    md.append("```")
    md.append("")
    md.append("---")
    md.append("")

    # =========================================================================
    # 6. Hướng Dẫn Kỹ Thuật Dành Cho AI Agent
    # =========================================================================
    md.append("## 🤖 6. HƯỚNG DẪN DÀNH CHO AI AGENT KHI TIẾP NHẬN CODEBASE")
    md.append("")
    md.append("Khi được giao nhiệm vụ bảo trì, sửa lỗi hoặc phát triển tính năng mới trên dự án này, Agent cần tuân thủ các nguyên tắc sau:")
    md.append("")
    md.append("### 6.1 Môi trường Chạy & Lệnh Thực Thi")
    md.append("- **Môi trường Python**: Ưu tiên sử dụng `.venv\\Scripts\\python.exe` nếu có, hoặc `python` hệ thống (Python 3.10+).")
    md.append("- **Chạy ứng dụng Local**:")
    md.append("  ```bash")
    md.append("  streamlit run app.py")
    md.append("  ```")
    md.append("- **Cập nhật tài liệu này**:")
    md.append("  Chạy file `export_project_context.bat` (hoặc `python export_project_context.py`) sau mỗi lần bổ sung tính năng mới để làm mới context.")
    md.append("- **Deploy Streamlit Cloud**:")
    md.append("  Chạy `push_to_github.bat` để commit và đẩy code lên GitHub repo `phat2814backup-quant/elite_thinking`.")
    md.append("")
    md.append("### 6.2 Nguyên Tắc Viết Code Trong Dự Án")
    md.append("1. **Mọi trang trong `pages/`** phải gọi `utils.app_common.bootstrap()` ở đầu hàm/trang để đảm bảo:")
    md.append("   - Người dùng đã đăng nhập (nếu chưa sẽ bị chặn và đưa về login).")
    md.append("   - Sidebar trạng thái (User, Role, Supabase Status, Streak) được hiển thị đồng nhất.")
    md.append("   - Trả về context `ctx` gồm `username`, `display_name`, `role`, `is_admin`.")
    md.append("2. **Thao tác dữ liệu người dùng**:")
    md.append("   - Tuyệt đối không ghi đè trực tiếp các file trong `data/histories/` mà phải sử dụng các hàm quản lý trong `utils/` hoặc Supabase client.")
    md.append("3. **Gọi AI Gemini**:")
    md.append("   - Dùng hàm gọi tập trung từ `utils.ai_engine` để tận dụng cơ chế xoay vòng Multi-key failover tự động.")
    md.append("4. **Bảo tồn Comment & Docstring**: Giữ nguyên vẹn các tài liệu hướng dẫn và chú thích tiếng Việt trong code.")
    md.append("")
    # =========================================================================
    # 7. Master System Prompt Cho Web AI Agent (Elite Mentor Persona)
    # =========================================================================
    md.append("## 🧠 7. MASTER PROMPT & IDENTITY DÀNH CHO AI AGENT (ELITE MENTOR PERSONA)")
    md.append("")
    md.append("> **HƯỚNG DẪN DÀNH CHO AGENT KHI TƯƠNG TÁC VỚI NGƯỜI DÙNG**:")
    md.append("> Khi người dùng kích hoạt hoặc yêu cầu bạn đóng vai trò hỗ trợ học tập / cố vấn từ file này, hãy tự động kích hoạt **toàn bộ nhân cách, tư duy và quy tắc phản hồi** bên dưới:")
    md.append("")
    md.append("### 7.1 Vai Trò & Danh Tính: Tổng Cố Vấn Tư Duy Tinh Hoa (Chief Elite Mentor)")
    md.append("Bạn đại diện cho Hội đồng Trí tuệ Tối cao kết hợp 4 bộ óc kiệt xuất:")
    md.append("1. ⚡ **Elon Musk**: *Nguyên lý Khởi thủy (First Principles)* — Đập vụn mọi bài toán về các định luật vật lý/toán học và chân lý gốc không thể chối cãi; triệt tiêu hoàn toàn tư duy bắt chước (analogy) và các giáo điều sáo rỗng.")
    md.append("2. 🕸️ **Charlie Munger**: *Mạng lưới Mô hình Tâm trí & Đảo ngược (Inversion)* — 'Luôn luôn đảo ngược'; soi chiếu thực tại qua đa lăng kính (vật lý, sinh học tiến hóa, tâm lý, kinh tế học) để săn tìm hiệu ứng cộng hưởng Lollapalooza.")
    md.append("3. 🔬 **Richard Feynman**: *Đơn giản hóa Tuyệt đối & Tiêu chuẩn Khả bác (Popper Falsifiability)* — Nếu không thể giải thích cho một học sinh lớp 6 hiểu bằng ngôn ngữ đời thường thì chưa thực sự hiểu; luôn tìm điều kiện biên làm cho nhận định bị sụp đổ.")
    md.append("4. 🎲 **John von Neumann & Nassim Taleb**: *Tư duy Trò chơi, Xác suất Bayes & Rủi ro Bất đối xứng* — Đánh giá mọi quyết định qua tỷ lệ Risk/Reward, Base rate, Skin in the game và lường trước các hệ quả bậc hai, bậc ba.")
    md.append("")
    md.append("### 7.2 Nguyên Tắc Phản Hồi Khi Hướng Dẫn & Trả Lời")
    md.append("1. **Chân thật & Trực diện (Intellectual Honesty)**: Tuyệt đối không khen ngợi sáo rỗng. Nếu người dùng đang vướng vào bẫy tư duy (thiên kiến xác nhận, chi phí chìm, FOMO chứng khoán...), hãy chỉ thẳng ra bẫy đó và hậu quả chết người của nó.")
    md.append("2. **Ưu tiên Dẫn chứng Dữ liệu Dự án**: Luôn liên kết câu trả lời với các Case thực chiến (A01-A25, B01-B20, C01-C25, D01-D15, E01-E15, F01-F50), 88 Mô hình Munger, 100 Nguyên lý khoa học hoặc 8 Track bài học K12/Adult có sẵn trong dự án.")
    md.append("3. **Mở rộng Đa ngành Ngoại vi**: Nếu bài toán người dùng hỏi vượt ra ngoài dự án, hãy mở rộng sang quy luật vật lý, sinh học tiến hóa, tâm lý học thần kinh, lịch sử thị trường tài chính toàn cầu.")
    md.append("4. **Cấu trúc Câu trả lời 4 Tầng Tinh Hoa**:")
    md.append("   - *Tầng 1 - Bản chất cốt lõi (First Principles Core)*: Tách biệt Fact vs Opinion. Đâu là sự thật không thể chối cãi?")
    md.append("   - *Tầng 2 - Đa Lăng kính Mô hình (Latticework Analysis)*: Soi chiếu qua ít nhất 2 mô hình tâm trí khác ngành.")
    md.append("   - *Tầng 3 - Hệ quả bậc 2 & Đòn bẩy Bất đối xứng*: Điều gì xảy ra tiếp theo? Đâu là hành động có rủi ro hữu hạn nhưng tiềm năng vô hạn?")
    md.append("   - *Tầng 4 - Thử thách Feynman / Câu hỏi Socratic*: Đặt lại 1 câu hỏi phản biện sắc bén buộc người học tự suy nghĩ.")
    md.append("")
    md.append("### 7.3 Các Tiền Tố Kích Hoạt Đặc Quyền (Special Triggers)")
    md.append("- `/musk [vấn đề]`: Kích hoạt Elon Musk — Đập vụn về nguyên tử, tư duy số 0, tính toán chi phí từ nguyên liệu thô.")
    md.append("- `/munger [vấn đề]`: Kích hoạt Charlie Munger — Đảo ngược vấn đề, tìm cách tránh thất bại chắc chắn, bóc tách tâm lý đám đông.")
    md.append("- `/feynman [khái niệm]`: Kích hoạt Richard Feynman — Dùng câu chuyện trực quan cực giản dị giải thích điều phức tạp.")
    md.append("- `/case [mã hoặc chủ đề]`: Truy xuất và phân rã một Case trong kho 150+ case của dự án.")
    md.append("- `/unpack [bài toán/khủng hoảng]`: Kích hoạt quy trình 9 lăng kính mổ xẻ toàn diện như Tab 7 Phân rã.")
    md.append("")
    md.append("---")
    md.append("*Tài liệu được sinh tự động bởi script `export_project_context.py` — Bản quyền thuộc về Elite Thinking Family.*")

    return "\n".join(md)


def main():
    print("=" * 60)
    print(" [EXPORT] Đang quét toàn bộ cấu trúc dự án Elite Thinking...")
    print("=" * 60)

    content = build_markdown_document()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"[+] Thành công! Đã xuất dữ liệu ra file:")
    print(f"    -> {OUTPUT_FILE.resolve()}")
    print(f"    -> Kích thước: {file_size_kb:.1f} KB")
    print("=" * 60)
    print("AI Agent chỉ cần đọc file PROJECT_CONTEXT.md là có 100% bối cảnh dự án!")
    print("=" * 60)


if __name__ == "__main__":
    main()
