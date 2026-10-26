# -*- coding: utf-8 -*-
"""
Module Động Cơ Chưng Cất Nhận Thức Nữ Oa (Nuwa Cognitive Engine)
Dựa trên triết lý & kiến trúc Nuwa-Skill:
1. HOW they think thay vì WHAT they said.
2. 5 Tầng nhận thức: Lăng kính (Mental Models), Quy tắc quyết định (Heuristics), 
   DNA Biểu đạt (Expression DNA), Vùng cấm (Anti-patterns), Ranh giới trung thực (Honest Boundaries).
3. Chẩn đoán vấn đề & Đề xuất Cố vấn tinh hoa phù hợp (Phase 0B).
4. Hội Chẩn Đa Chiều (Council of Thinkers) giải quyết nan đề thực chiến.
5. Xưởng Chưng Cất Mở Rộng: Tự động chưng cất bất kỳ vĩ nhân/chuyên gia nào và lưu vào CSDL.
"""

from __future__ import annotations

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from core.farrow_engine import get_all_gemini_api_keys
from core.db_storage import (
    load_distilled_profiles_storage,
    save_distilled_profile_storage,
    delete_distilled_profile_storage
)

# =============================================================================
# 1. HỆ THỐNG PROMPT NỮ OA (NUWA COGNITIVE PROMPTS)
# =============================================================================

NUWA_DIAGNOSTIC_SYSTEM_PROMPT = """Bạn là Nữ Oa (Nuwa Diagnostic Engine) — Bậc thầy chẩn đoán nan đề và điều hướng Lăng Kính Nhận Thức.
Triết lý Nữ Oa: Không bắt chước vỏ bọc bề ngoài hay nhại lại danh ngôn. Chúng ta bóc tách HỆ ĐIỀU HÀNH NHẬN THỨC (HOW they think thay vì WHAT they said).

NHIỆM VỤ:
1. Tiếp nhận nan đề/bế tắc thực tế của người dùng.
2. Phân tích bản chất cốt lõi của vấn đề (Dimension):
   - Quyết định & Phán đoán (Decision & Judgment)
   - Khởi nghiệp, Sản phẩm & PMF (Startup & Product)
   - Kỹ thuật AI, Hệ thống & Tự động hóa (AI Engineering & Systems)
   - Chú ý, Content viral & Thu hút đám đông (Attention Engineering)
   - Đàm phán, Quyền lực & Thao túng tâm lý (Negotiation & Power)
   - Rủi ro, Chống mong manh & Đầu tư (Antifragile & Tail Risk)
   - Đơn giản hóa & Chân lý gốc (First Principles & Feynman Simplicity)
   - Tâm lý vô thức, Động lực ẩn & Thấu cảm (Psychology & Incentives)
   - Định hướng thực dụng & Bóc trần ảo tưởng (Pragmatic Navigation)
3. Từ danh sách các Hồ sơ Chưng cất (Profiles) được cung cấp, hãy CHỌN RA ĐÚNG 2 ĐẾN 3 HỒ SƠ PHÙ HỢP NHẤT để giải bài toán này.
4. Với mỗi hồ sơ được chọn, chỉ rõ:
   - match_reason: Tại sao tư duy người này trực tiếp bẻ khóa được nan đề?
   - core_lens: Lăng kính nhận thức cụ thể nào của họ sẽ được dùng?
   - blindspot_warning: Điểm mù / Ranh giới trung thực cần cảnh giác (Không có mô hình nào là vạn năng).

BẮT BUỘC TRẢ VỀ JSON HỢP LỆ VỚI CẤU TRÚC SAU:
{
  "problem_core": "Tóm tắt bản chất hạt nhân của vấn đề trong 1-2 câu",
  "dimension": "Tên chiều kích nhận thức chính",
  "recommendations": [
    {
      "profile_id": "id_cua_nhan_vat",
      "match_score": 95,
      "core_lens": "Tên lăng kính / mô hình tư duy cốt lõi",
      "match_reason": "Lý do vì sao lăng kính này giải quyết trúng tim đen vấn đề",
      "blindspot_warning": "Cảnh báo điểm mù / ranh giới trung thực"
    }
  ],
  "preliminary_insight": "Một nhận định sắc bén ban đầu về vấn đề dưới góc nhìn đa mô hình"
}
"""

NUWA_COUNCIL_SYSTEM_PROMPT = """Bạn là Hội Đồng Cố Vấn Tinh Hoa Nữ Oa (Nuwa Council of Thinkers).
Bạn quy tụ những bộ óc xuất chúng đã được chưng cất thành Hệ điều hành nhận thức độc lập.

QUY TẮC BẤT DI BẤT DỊCH CHO TỪNG NHÀ TƯ TƯỞNG:
1. KHÔNG NÓI SÁO RỖNG. Nói đúng giọng điệu, nhịp điệu và DNA biểu đạt đặc trưng của nhân vật.
2. Áp dụng chuẩn xác 5 tầng nhận thức:
   - Lăng kính nhận thức (Mental Model): Họ nhìn bài toán này bằng lăng kính nào?
   - Quy tắc quyết định (Decision Heuristic): Trực giác ra quyết định thực tế.
   - Vùng cấm & Bẫy ngụy biện (Anti-pattern / Inversion): Bóc trần sai lầm ngu xuẩn nhất mà người dùng đang hoặc có thể mắc phải.
   - Phản biện sắc lạnh (Brutally honest feedback): Đánh thẳng vào điểm yếu cốt tử, không xoa dịu cảm xúc giả tạo.
   - Hành động thực chiến (Actionable Step): Bước đi cụ thể, không lý thuyết suông.
3. PHẦN TỔNG HỢP HIỆU ỨNG LOLLAPALOOZA (CỘNG HƯỞNG ĐA MÔ HÌNH):
   - Tìm ra điểm giao thoa tối thượng giữa các góc nhìn.
   - Đưa ra 1 NƯỚC ĐI BẤT ĐỐI XỨNG (Asymmetric Next Step) trong 24 giờ tới: Rủi ro tối thiểu, tiềm năng xoay chuyển cục diện tối đa.

BẮT BUỘC TRẢ VỀ JSON HỢP LỆ THEO CẤU TRÚC:
{
  "problem_summary": "Tóm tắt vấn đề được hội chẩn",
  "thinkers_advice": [
    {
      "profile_id": "id_nhan_vat",
      "name": "Tên nhân vật",
      "applied_mental_model": "Tên mô hình & diễn giải cách áp dụng",
      "applied_heuristic": "Quy tắc quyết định cụ thể",
      "trap_warning": "Bẫy ngụy biện / Điều tuyệt đối không được làm (Anti-pattern)",
      "brutal_critique": "Lời phản biện sắc bén, vạch trần ảo tưởng theo DNA biểu đạt của nhân vật",
      "action_step": "Hành động thực chiến cụ thể"
    }
  ],
  "lollapalooza_synthesis": {
    "convergence_point": "Điểm đồng thuận tối thượng giữa các nhà tư tưởng",
    "asymmetric_action_24h": "Hành động bất đối xứng cần làm ngay trong 24 giờ tới",
    "long_term_rule": "Nguyên lý bất biến giữ lại cho dài hạn"
  }
}
"""

NUWA_DISTILLATION_FORGE_PROMPT = """Bạn là Nữ Oa Cognitive Forge (Lò nung Chưng cất Nhận thức Nữ Oa).
Phương châm: "你想蒸馏的下一个员工，何必是同事。" (Người tiếp theo bạn muốn chưng cất tư duy, việc gì phải là đồng nghiệp).
Chưng cất nhận thức KHÔNG PHẢI là tóm tắt tiểu sử hay nhại lại danh ngôn. Đó là chiết xuất HỆ ĐIỀU HÀNH NHẬN THỨC (HOW they think) để một người khác hoặc AI có thể nạp vào và tư duy như họ.

BÓC TÁCH CHUẨN 5 TẦNG NHẬN THỨC:
1. Bản sắc (Identity) & Khẩu quyết (Tagline): Tinh thần cốt tử, điểm khởi đầu và niềm tin hạt nhân.
2. 4-5 Lăng kính nhận thức (Mental Models): Các mô hình bất biến họ dùng để quan sát và diễn giải thế giới.
3. 4-6 Quy tắc trực giác quyết định (Decision Heuristics): Phím tắt tư duy khi đứng trước ngã ba đường.
4. DNA Biểu đạt (Expression DNA): Nhịp điệu câu, từ ngữ cấm kỵ, cách dùng ẩn dụ và cách đặt câu hỏi ngược.
5. Vùng cấm & Phản mẫu (Anti-patterns): Những điều họ TUYỆT ĐỐI KHÔNG LÀM.
6. Ranh giới trung thực (Honest Boundaries): Những việc hệ tư tưởng này BẤT LỰC, điểm mù và giới hạn (Skill không nói rõ giới hạn là skill không đáng tin).

BẮT BUỘC TRẢ VỀ JSON HỢP LỆ:
{
  "name": "Tên nhân vật đầy đủ",
  "avatar": "Emoji đại diện phù hợp nhất (ví dụ: 🚀, 💡, 🏛️, 📈)",
  "domain": "Lĩnh vực chuyên môn & Thế mạnh đòn bẩy",
  "tagline": "Khẩu quyết kinh điển hoặc câu châm ngôn mang tính hệ điều hành",
  "identity": "Đoạn văn 150-250 từ mô tả bản sắc nhận thức, xuất phát điểm và sứ mệnh",
  "mental_models": [
    {
      "name": "Tên mô hình 1",
      "one_liner": "Tóm tắt trong 1 câu",
      "content": "Giải thích chi tiết nguyên lý, bằng chứng thực tế và cách áp dụng"
    }
  ],
  "decision_heuristics": [
    "Quy tắc 1: Tên quy tắc — Diễn giải quy tắc ra quyết định kèm ví dụ",
    "Quy tắc 2: Tên quy tắc — Diễn giải quy tắc ra quyết định kèm ví dụ"
  ],
  "expression_dna": [
    "Đặc trưng nhịp điệu và độ dài câu",
    "Cách dùng ẩn dụ hoặc ví von đặc trưng",
    "Từ ngữ ưa chuộng và từ ngữ cấm kỵ",
    "Cách phản biện và thái độ đối với sự thật"
  ],
  "anti_patterns": [
    "Điều cấm kỵ 1: Những việc tuyệt đối không làm",
    "Điều cấm kỵ 2: Bẫy ngụy biện luôn tránh xa"
  ],
  "honest_boundaries": [
    "Ranh giới 1: Những loại bài toán mà mô hình này không giải được",
    "Ranh giới 2: Điểm mù tự nhiên do môi trường/kinh nghiệm cá nhân"
  ]
}
"""


# =============================================================================
# 2. HÀM QUẢN TRỊ KHO HỒ SƠ CHƯNG CẤT (DATABASE & CACHE)
# =============================================================================

def get_all_distilled_profiles(username: str = "Phat") -> List[Dict[str, Any]]:
    """Tải toàn bộ hồ sơ chưng cất từ storage, bảo toàn thứ tự: hồ sơ cốt lõi trước, hồ sơ mở rộng mới nhất lên đầu."""
    profiles = load_distilled_profiles_storage(username=username)
    if not profiles:
        # Fallback an toàn nếu file chưa kịp load
        return []
    
    # Tách built-in và custom
    builtin = [p for p in profiles if p.get("is_builtin", False)]
    custom = [p for p in profiles if not p.get("is_builtin", False)]
    
    # Custom sắp xếp theo created_at giảm dần
    custom_sorted = sorted(custom, key=lambda x: x.get("created_at", ""), reverse=True)
    return builtin + custom_sorted


def get_profile_by_id(profile_id: str, username: str = "Phat") -> Optional[Dict[str, Any]]:
    """Tìm hồ sơ chưng cất theo ID."""
    all_p = get_all_distilled_profiles(username=username)
    for p in all_p:
        if p.get("id") == profile_id:
            return p
    return None


def save_new_distilled_profile(profile_data: Dict[str, Any], username: str = "Phat") -> bool:
    """Lưu hồ sơ đã chưng cất mới vào database, tự động sinh ID chuẩn nếu chưa có."""
    if "id" not in profile_data or not profile_data["id"]:
        safe_name = re.sub(r'[^a-zA-Z0-9]', '-', profile_data.get("name", "custom").lower()).strip('-')
        profile_data["id"] = f"custom-{safe_name}-{int(datetime.now().timestamp())}"
    
    if "created_at" not in profile_data:
        profile_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    profile_data["is_builtin"] = False
    return save_distilled_profile_storage(profile_data, username=username)


def remove_distilled_profile(profile_id: str, username: str = "Phat") -> bool:
    """Xóa hồ sơ chưng cất do người dùng tạo (chặn xóa 14 hồ sơ cốt lõi)."""
    return delete_distilled_profile_storage(profile_id, username=username)


# =============================================================================
# 3. BỘ CHẨN ĐOÁN & TÌM CỐ VẤN PHÙ HỢP (PHASE 0B)
# =============================================================================

def _heuristic_match_thinkers(problem_text: str, profiles: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, Any]:
    """Bộ chẩn đoán Fallback Heuristic dựa trên từ khóa ngữ nghĩa sâu khi không có mạng hoặc hết quota AI."""
    lower_text = problem_text.lower()
    scores = {}
    
    keywords_map = {
        "paul-graham": ["khởi nghiệp", "startup", "founder", "viết", "essay", "pmf", "khách hàng", "scale", "ý tưởng", "code"],
        "zhang-yiming": ["sản phẩm", "tiktok", "app", "thuật toán", "tổ chức", "nhân tài", "quy mô", "trì hoãn", "ngắn hạn", "toàn cầu"],
        "karpathy": ["ai", "mô hình", "code", "kỹ thuật", "llm", "học máy", "lập trình", "phần mềm", "tự động hóa", "dữ liệu"],
        "ilya-sutskever": ["an toàn ai", "scaling", "siêu trí tuệ", "agi", "nghiên cứu", "dài hạn", "triết lý công nghệ"],
        "mrbeast": ["video", "youtube", "nội dung", "viral", "view", "thumbnail", "giữ chân", "truyền thông", "đám đông", "kênh"],
        "trump": ["đàm phán", "thương lượng", "quyền lực", "áp đảo", "đối tác", "hợp đồng", "truyền thông", "tâm lý", "chính trị"],
        "elon-musk": ["nguyên lý gốc", "first principles", "vật lý", "sản xuất", "tối ưu", "cắt giảm", "chi phí", "tốc độ", "tên lửa", "xe điện"],
        "feynman": ["đơn giản", "giải thích", "học tập", "bản chất", "hiểu sâu", "khoa học", "nghi ngờ", "thuật ngữ"],
        "munger": ["inversion", "đảo ngược", "sai lầm", "đa mô hình", "đầu tư", "chứng khoán", "tâm lý học", "lollapalooza", "cổ phiếu"],
        "naval": ["đòn bẩy", "tự do", "hạnh phúc", "giàu có", "thụ động", "phán đoán", "tâm trí", "không xin phép", "media"],
        "steve-jobs": ["thiết kế", "nghệ thuật", "trải nghiệm", "tối giản", "sản phẩm đỉnh cao", "khách hàng", "khắt khe", "nói không"],
        "taleb": ["rủi ro", "chống mong manh", "antifragile", "thiên nga đen", "skin in the game", "thất bại", "bất định", "khủng hoảng"],
        "zhangxuefeng": ["chọn ngành", "đại học", "việc làm", "thực tế", "tiền bạc", "thực dụng", "nghề nghiệp", "thất nghiệp", "ảo tưởng"],
        "sun-yuchen": ["marketing ngược", "chú ý", "pr", "crypto", "tiền số", "đòn bẩy vốn", "tận dụng sự kiện"]
    }
    
    for p in profiles:
        pid = p.get("id", "")
        base_score = 50
        kw_list = keywords_map.get(pid, [])
        for kw in kw_list:
            if kw in lower_text:
                base_score += 15
        
        # Check domain & tagline
        domain = p.get("domain", "").lower()
        tagline = p.get("tagline", "").lower()
        for word in lower_text.split():
            if len(word) >= 3:
                if word in domain:
                    base_score += 5
                if word in tagline:
                    base_score += 5
        scores[pid] = min(base_score, 98)
        
    sorted_p = sorted(profiles, key=lambda p: scores.get(p.get("id", ""), 0), reverse=True)
    top_picks = sorted_p[:top_k]
    
    recommendations = []
    for tp in top_picks:
        models = tp.get("mental_models", [])
        lens_name = models[0].get("name", "Lăng kính đặc trưng") if models else "Hệ điều hành nhận thức"
        heuristics = tp.get("decision_heuristics", [])
        heur_sample = heuristics[0][:80] if heuristics else tp.get("tagline", "")
        boundaries = tp.get("honest_boundaries", [])
        bound_sample = boundaries[0] if boundaries else "Không áp dụng cho các vấn đề nằm ngoài vòng tròn năng lực."
        
        recommendations.append({
            "profile_id": tp.get("id"),
            "match_score": scores.get(tp.get("id"), 85),
            "core_lens": lens_name,
            "match_reason": f"Thế mạnh chuyên sâu về {tp.get('domain')}. Vận dụng quy tắc: {heur_sample}...",
            "blindspot_warning": bound_sample
        })
        
    return {
        "problem_core": f"Phân tích nan đề thực tế: {problem_text[:120]}...",
        "dimension": "Chẩn đoán Thực Chiến Đa Mô Hình (Heuristic Match)",
        "recommendations": recommendations,
        "preliminary_insight": "Nan đề này đòi hỏi sự kết hợp giữa việc tối ưu hóa đòn bẩy và kiểm soát rủi ro đuôi bất đối xứng."
    }


def diagnose_and_match_thinkers(
    problem_text: str,
    profiles: List[Dict[str, Any]],
    top_k: int = 3,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Sử dụng Nuwa Phase 0B để bóc tách vấn đề và đề xuất 2-3 nhà tư tưởng phù hợp nhất."""
    cleaned = problem_text.strip()
    if not cleaned:
        return _heuristic_match_thinkers("Vấn đề mẫu", profiles, top_k)

    # Thu thập candidate keys
    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if candidate_keys and genai is not None:
        # Chuẩn bị danh sách profile tóm tắt gửi cho AI
        summary_profiles = []
        for p in profiles:
            models_brief = [m.get("name", "") for m in p.get("mental_models", [])[:3]]
            summary_profiles.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "domain": p.get("domain"),
                "tagline": p.get("tagline"),
                "key_models": models_brief
            })

        user_prompt = f"""VẤN ĐỀ / TÌNH HUỐNG CỦA NGƯỜI DÙNG:
\"\"\"
{cleaned}
\"\"\"

DANH SÁCH {len(profiles)} HỒ SƠ CHƯNG CẤT CÓ TRONG CƠ SỞ DỮ LIỆU:
{json.dumps(summary_profiles, ensure_ascii=False, indent=2)}

HÃY CHẨN ĐOÁN VÀ CHỌN RA ĐÚNG 2 ĐẾN {top_k} HỒ SƠ PHÙ HỢP NHẤT."""

        for key in candidate_keys:
            try:
                genai.configure(api_key=key)
                for cur_model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=cur_model,
                            system_instruction=NUWA_DIAGNOSTIC_SYSTEM_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        resp = model.generate_content(user_prompt, request_options={"timeout": 25})
                        if resp and resp.text:
                            raw_t = resp.text.strip()
                            if raw_t.startswith("```"):
                                lines = raw_t.splitlines()
                                if len(lines) >= 2 and lines[-1].startswith("```"):
                                    raw_t = "\n".join(lines[1:-1]).strip()
                            data = json.loads(raw_t)
                            if "recommendations" in data and isinstance(data["recommendations"], list):
                                return data
                    except Exception:
                        continue
            except Exception:
                continue

    # Fallback nếu AI không khả dụng
    return _heuristic_match_thinkers(cleaned, profiles, top_k)


# =============================================================================
# 4. HỘI ĐỒNG CỐ VẤN GIẢI QUYẾT VẤN ĐỀ (COUNCIL OF THINKERS)
# =============================================================================

def consult_thinkers_council(
    problem_text: str,
    selected_profile_ids: List[str],
    profiles: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Triệu tập Hội đồng các nhà tư tưởng được chọn để cùng mổ xẻ và đưa ra giải pháp toàn diện."""
    cleaned = problem_text.strip()
    selected_profiles = [p for p in profiles if p.get("id") in selected_profile_ids]
    if not selected_profiles:
        selected_profiles = profiles[:2]

    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if candidate_keys and genai is not None:
        # Chuẩn bị dữ liệu chi tiết của các nhân vật được chọn
        dossiers = []
        for p in selected_profiles:
            dossiers.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "domain": p.get("domain"),
                "tagline": p.get("tagline"),
                "identity": p.get("identity"),
                "mental_models": p.get("mental_models", [])[:4],
                "decision_heuristics": p.get("decision_heuristics", [])[:5],
                "anti_patterns": p.get("anti_patterns", [])[:4],
                "expression_dna": p.get("expression_dna", [])[:4]
            })

        user_prompt = f"""VẤN ĐỀ NAN GIẢI:
\"\"\"
{cleaned}
\"\"\"

CÁC HỒ SƠ NHẬN THỨC CỐ VẤN THAM GIA HỘI CHẨN:
{json.dumps(dossiers, ensure_ascii=False, indent=2)}

HÃY TIẾN HÀNH HỘI CHẨN ĐA CHIỀU THEO ĐÚNG GIỌNG ĐIỆU VÀ HỆ ĐIỀU HÀNH NHẬN THỨC CỦA TỪNG NHÀ TƯ TƯỞNG."""

        for key in candidate_keys:
            try:
                genai.configure(api_key=key)
                for cur_model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=cur_model,
                            system_instruction=NUWA_COUNCIL_SYSTEM_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        resp = model.generate_content(user_prompt, request_options={"timeout": 35})
                        if resp and resp.text:
                            raw_t = resp.text.strip()
                            if raw_t.startswith("```"):
                                lines = raw_t.splitlines()
                                if len(lines) >= 2 and lines[-1].startswith("```"):
                                    raw_t = "\n".join(lines[1:-1]).strip()
                            data = json.loads(raw_t)
                            if "thinkers_advice" in data:
                                return data
                    except Exception:
                        continue
            except Exception:
                continue

    # Fallback Heuristic nếu không kết nối được AI
    fallback_advice = []
    for p in selected_profiles:
        models = p.get("mental_models", [])
        m_name = models[0].get("name", "Lăng kính bản nguyên") if models else "Mô hình cốt lõi"
        heuristics = p.get("decision_heuristics", [])
        h_val = heuristics[0] if heuristics else "Tập trung vào giá trị thực và loại bỏ tạp âm."
        anti = p.get("anti_patterns", [])
        anti_val = anti[0] if anti else "Tuyệt đối không ra quyết định dựa trên cảm xúc nhất thời."
        
        fallback_advice.append({
            "profile_id": p.get("id"),
            "name": p.get("name"),
            "applied_mental_model": f"{m_name}: Bóc tách vấn đề về những biến số cốt tử có thể đo lường và kiểm soát được.",
            "applied_heuristic": h_val,
            "trap_warning": anti_val,
            "brutal_critique": f"Bạn đang bị phân tâm bởi các yếu tố bề nổi thay vì đi sâu vào bản chất. Nếu tiếp tục theo hướng này, bạn sẽ tiêu tốn tài nguyên vào những thứ không tạo ra đòn bẩy.",
            "action_step": f"Khoanh vùng đúng 1 biến số quan trọng nhất trong ngày hôm nay và giải quyết dứt điểm."
        })
        
    return {
        "problem_summary": cleaned[:150],
        "thinkers_advice": fallback_advice,
        "lollapalooza_synthesis": {
            "convergence_point": "Cả hai lăng kính đều thống nhất rằng: Cần lập tức cắt bỏ các chi phí chìm và tập trung toàn lực vào mắt xích tạo ra đòn bẩy cao nhất.",
            "asymmetric_action_24h": "Viết rõ ràng quyết định ra giấy (Writing = Thinking), xác định ngưỡng chịu lỗ tối đa và hành động ngay không chần chừ.",
            "long_term_rule": "Luôn giữ tỷ lệ rủi ro/lợi nhuận bất đối xứng và kiểm tra định kỳ sai số."
        }
    }


# =============================================================================
# 5. XƯỞNG CHƯNG CẤT BẤT KỲ AI (NUWA DISTILLATION FORGE)
# =============================================================================

def distill_new_thinker_ai(
    name: str,
    domain: str,
    corpus_or_bio: str = "",
    focus_aspect: str = "Toàn diện",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Chưng cất hệ điều hành nhận thức của bất kỳ nhân vật nào theo quy chuẩn Nữ Oa."""
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Tên nhân vật không được để trống.")

    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    user_prompt = f"""YÊU CẦU CHƯNG CẤT NHÂN VẬT:
- Tên nhân vật: {cleaned_name}
- Lĩnh vực chuyên môn: {domain or 'Đa lĩnh vực / Xuất chúng'}
- Tiêu điểm chưng cất: {focus_aspect or 'Toàn diện'}

TÀI LIỆU CUNG CẤP / GHI CHÚ BỔ SUNG (NẾU CÓ):
\"\"\"
{corpus_or_bio[:12000] if corpus_or_bio else 'Hãy tự động truy xuất từ toàn bộ tri thức công khai, sách vở, bài phát biểu, bài phỏng vấn và các quyết định lịch sử của nhân vật này.'}
\"\"\"

HÃY TIẾN HÀNH CHƯNG CẤT TOÀN DIỆN 5 TẦNG NHẬN THỨC VÀ TRẢ VỀ JSON."""

    if candidate_keys and genai is not None:
        for key in candidate_keys:
            try:
                genai.configure(api_key=key)
                for cur_model in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=cur_model,
                            system_instruction=NUWA_DISTILLATION_FORGE_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        resp = model.generate_content(user_prompt, request_options={"timeout": 45})
                        if resp and resp.text:
                            raw_t = resp.text.strip()
                            if raw_t.startswith("```"):
                                lines = raw_t.splitlines()
                                if len(lines) >= 2 and lines[-1].startswith("```"):
                                    raw_t = "\n".join(lines[1:-1]).strip()
                            data = json.loads(raw_t)
                            if "mental_models" in data and "decision_heuristics" in data:
                                # Tạo ID chuẩn
                                safe_slug = re.sub(r'[^a-zA-Z0-9]', '-', cleaned_name.lower()).strip('-')
                                data["id"] = f"custom-{safe_slug}-{int(datetime.now().timestamp())}"
                                data["is_builtin"] = False
                                data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                return data
                    except Exception:
                        continue
            except Exception:
                continue

    # Fallback nếu không có AI
    safe_slug = re.sub(r'[^a-zA-Z0-9]', '-', cleaned_name.lower()).strip('-')
    return {
        "id": f"custom-{safe_slug}-{int(datetime.now().timestamp())}",
        "name": cleaned_name,
        "avatar": "🧠",
        "domain": domain or "Chuyên gia / Nhà tư tưởng xuất chúng",
        "tagline": f"Tư duy độc lập và hành động đột phá trong {domain or 'thế giới thực'}.",
        "identity": f"Hồ sơ chưng cất của {cleaned_name}. Tập trung vào việc khai thác các đòn bẩy tri thức và tối ưu hóa quyết định trong điều kiện bất định.",
        "mental_models": [
            {
                "name": f"Nguyên lý vận hành cốt lõi của {cleaned_name}",
                "one_liner": "Luôn quy chiếu về các chân lý nền tảng không thể phủ định.",
                "content": "Phân tích các hệ thống phức tạp thành các thành phần đơn giản nhất và tối ưu hóa từ gốc rễ."
            },
            {
                "name": "Tư duy đòn bẩy bất đối xứng",
                "one_liner": "Chỉ đặt cược vào những cơ hội rủi ro giới hạn nhưng tiềm năng không giới hạn.",
                "content": "Loại bỏ các giao dịch hoặc dự án có nguy cơ triệt hạ sinh tồn."
            }
        ],
        "decision_heuristics": [
            "Hành động dứt khoát khi có từ 70% thông tin — Đừng đợi 90% vì cơ hội đã biến mất.",
            "Nói 'KHÔNG' với 99% các lời mời không phục vụ trực tiếp mục tiêu hạt nhân."
        ],
        "expression_dna": [
            "Trực diện, súc tích, không rào đón.",
            "Thường xuyên sử dụng các câu hỏi đảo ngược để kiểm tra giả định."
        ],
        "anti_patterns": [
            "Không bao giờ theo đuổi sự hoàn hảo viển vông mà trì hoãn ra mắt.",
            "Không tham gia vào các trò chơi tổng bằng không (Zero-sum games)."
        ],
        "honest_boundaries": [
            "Không thể giải quyết các bài toán đòi hỏi sự an toàn tuyệt đối không có rủi ro.",
            "Bị giới hạn trong bối cảnh và thị trường cụ thể của lĩnh vực chuyên môn."
        ],
        "is_builtin": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
