# -*- coding: utf-8 -*-
"""
Module Phòng Điêu Khắc Đề Bài & Câu Hỏi Tinh Hoa (Polymath Problem Formulation Lab).
Hiện thực hóa tầm nhìn của Elon Musk (Phỏng vấn 2026):
"Trong kỷ nguyên AI và Robot, máy móc làm được mọi việc thực thi.
Lợi thế sống còn của con người là BIẾT CÁCH ĐẶT VẤN ĐỀ VÀ ĐIỀU KHẮC CÂU HỎI (Formulate the question).
Và với kiến thức tổng quát rộng nhất có thể về Arts, Sciences & Engineering,
bạn sẽ đặt ra được những câu hỏi sắc bén và giàu 'vị giác' (taste) nhất."
"""

from __future__ import annotations

import json
import re
import os
from typing import Dict, Any, Optional, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from core.farrow_engine import get_all_gemini_api_keys

POLYMATH_SAMPLE_TEMPLATES = [
    {
        "title": "🤖 Robot Gia Đình (Optimus Companion)",
        "intent": "Tôi muốn một Robot hình người / AI quản gia trợ giúp cuộc sống gia đình: dọn dẹp, nhắc việc, chăm sóc người già và hỗ trợ học tập cho trẻ nhỏ mà không biến ngôi nhà thành một cái bệnh viện hay nhà tù công nghệ vô cảm."
    },
    {
        "title": "🎬 Video Giáo Dục Tri Thức Triệu View",
        "intent": "Tôi muốn sản xuất chuỗi video ngắn 60 giây giải thích các khái niệm khoa học và tài chính phức tạp (như Cơ học lượng tử, Vi cấu trúc Vàng) cho Gen Z: vừa cuốn hút, giữ chân 100% thời lượng, vừa có chiều sâu học thuật và gu điện ảnh điện ảnh khác biệt hoàn toàn với rác AI slop trên mạng."
    },
    {
        "title": "💼 Khởi Nghiệp AI Y Tế & Chữa Lành",
        "intent": "Xây dựng ứng dụng AI đồng hành hỗ trợ sức khỏe tinh thần và giảm căng thẳng cho nhân sự văn phòng: làm sao để AI vừa chuẩn xác về y khoa thần kinh, vừa có sự thấu cảm nhân văn của triết học Khắc kỷ, không rơi vào bẫy trả lời sáo rỗng như chatbot tâm lý thông thường."
    },
    {
        "title": "📊 Hệ Thống Phân Tích Đầu Tư Đa Chiều",
        "intent": "Thiết lập một AI Agent chuyên phân tích các thương vụ M&A và cổ phiếu: kết hợp mô hình định giá chiết khấu dòng tiền (DCF) toán học, soi xét văn hóa lãnh đạo và động lực ngầm của ban điều hành, đồng thời cảnh báo rủi ro thiên nga đen."
    }
]

POLYMATH_FORMULATION_SYSTEM_PROMPT = """Bạn là Polymath Question Formulation Engine — Bậc thầy Kiến trúc Đề bài & Điêu khắc Câu hỏi Đa ngành theo tầm nhìn của Elon Musk, Steve Jobs và Leonardo da Vinci.

NHIỆM VỤ:
Tiếp nhận một ý tưởng hoặc bài toán thô từ con người (Fuzzy Human Intent), dùng tri thức bách khoa đa ngành (Arts, Sciences, Engineering) để điêu khắc thành một BẢN ĐẶC TẢ TỐI THƯỢNG (Master Formulated Specification & Prompt) cho AI Agents và Robot thực thi.

QUY TRÌNH 4 TẦNG ĐIÊU KHẮC BÁCH KHOA:
1. TẦNG 1: SCIENCES & NATURAL LAWS (Khoa học tự nhiên & Chân lý gốc)
   - Giới hạn vật lý, nhiệt động lực, entropy, năng lượng và ngưỡng sinh học nhận thức nào KHÔNG THỂ BỊ BẺ CONG?
   - Ràng buộc toán học và xác suất nền tảng là gì?

2. TẦNG 2: ENGINEERING & SYSTEMS (Kỹ thuật & Kiến trúc thực thi)
   - Tính khả thi kỹ thuật, kiến trúc module, độ trễ và chi phí biên.
   - Các nút thắt cổ chai hệ thống và ngưỡng lỗi chấp nhận được.

3. TẦNG 3: ARTS, TASTE & HUMANITIES (Nghệ thuật, Gu thẩm mỹ & Trải nghiệm nhân văn)
   - "Taste" (Vị giác/Thẩm mỹ) của giải pháp là gì? (Tỷ lệ vàng, tối giản Bauhaus hay Wabi-Sabi?)
   - Cấu trúc kể chuyện (Narrative arc) và sự đồng cảm chạm đáy tim người dùng.
   - Ranh giới đạo đức và phẩm giá con người mà máy móc tuyệt đối không được xâm phạm.

4. TẦNG 4: THE MASTER FORMULATED PROMPT (Bản câu lệnh / Đề bài hoàn chỉnh cho AI & Robot)
   - Mission & Persona (Sứ mệnh & Vai trò)
   - Strict Constraints & Negative Prompts (Ràng buộc cứng & Những thứ TUYỆT ĐỐI KHÔNG ĐƯỢC LÀM)
   - Aesthetic & Taste Directives (Chỉ thị phong cách & Gu thẩm mỹ)
   - Step-by-Step Execution Protocol (Giao thức thực thi từng bước)
   - Acceptance & Verification Tests (Tiêu chí nghiệm thu đầu ra sắc nét)

5. SO SÁNH ĐỐI KHÁNG:
   - Amateur Prompt: Câu lệnh cẩu thả, ngây thơ mà người bình thường hay gõ cho AI.
   - Polymath Formulated: Sự khác biệt vượt trội về độ sâu, độ chính xác và gu tinh hoa.

BẮT BUỘC TRẢ VỀ JSON HỢP LỆ VỚI CẤU TRÚC SAU (KHÔNG KÈM MARKDOWN NGOÀI JSON):
{
  "problem_title": "Tiêu đề bài toán sắc bén dưới 10 từ",
  "fuzzy_summary": "Tóm lược ngắn gọn ý muốn ban đầu của con người",
  "layer_sciences": {
    "physics_limits": "Giới hạn vật lý, năng lượng hoặc entropy",
    "cognitive_biology": "Quy luật sinh học thần kinh, ngưỡng chú ý hoặc tâm lý tiến hóa",
    "probability_truth": "Chân lý xác suất và nguyên lý không thể nhân với 0"
  },
  "layer_engineering": {
    "architecture": "Kiến trúc hệ thống và cơ chế thực thi cốt lõi",
    "friction_and_costs": "Chi phí biên, độ trễ và nút thắt cổ chai",
    "fail_safes": "Cơ chế phòng thủ và biên an toàn kỹ thuật"
  },
  "layer_arts_humanities": {
    "aesthetic_taste": "Gu thẩm mỹ, phong cách thiết kế và vị giác trải nghiệm (Taste)",
    "narrative_soul": "Linh hồn câu chuyện, cung bậc cảm xúc và sự đồng cảm nhân văn",
    "human_ethics": "Ranh giới đạo đức và phẩm giá con người cần bảo vệ"
  },
  "master_prompt": {
    "role_and_mission": "Vai trò và mục tiêu tối thượng cho AI/Robot",
    "hard_constraints": ["Ràng buộc 1", "Ràng buộc 2", "Ràng buộc 3"],
    "taste_and_style": "Yêu cầu chi tiết về giọng điệu, thẩm mỹ và sự tinh tế",
    "negative_rules": ["Tuyệt đối không làm A", "Cấm B"],
    "acceptance_criteria": ["Tiêu chí hoàn thành 1", "Tiêu chí 2"]
  },
  "contrast_analysis": {
    "amateur_prompt": "Prompt ngô nghê thông thường...",
    "why_amateur_fails": "Tại sao câu lệnh này sẽ nhận về rác AI vô hồn...",
    "polymath_advantage": "Tại sao bản Formulate đa ngành tạo ra kết quả xuất chúng..."
  },
  "farrow_compression": {
    "anchor_1": "Mỏ neo 1 (Sciences - Khoa học)",
    "anchor_2": "Mỏ neo 2 (Engineering - Kỹ thuật)",
    "anchor_3": "Mỏ neo 3 (Arts & Taste - Nghệ thuật & Gu)",
    "reflex_mantra": "Khẩu quyết phản xạ 1 câu đắt giá"
  }
}
"""


def _generate_polymath_fallback_heuristic(intent: str) -> Dict[str, Any]:
    """Tạo bản điêu khắc đề bài Heuristic khi mất kết nối AI."""
    safe_topic = (intent[:40] + "...") if len(intent) > 40 else intent
    return {
        "problem_title": f"Điêu Khắc Đề Bài: {safe_topic}",
        "fuzzy_summary": intent,
        "layer_sciences": {
            "physics_limits": "Mọi hệ thống đều tuân thủ Định luật 2 Nhiệt động học: Nếu không có năng lượng đầu vào có chủ đích, hệ thống sẽ tự suy thoái về entropy cực đại. Năng lượng và thời gian là tài nguyên hữu hạn.",
            "cognitive_biology": "Ngưỡng tải nhận thức của con người chỉ duy trì tối ưu trong 10-15 phút. Não bộ lọc bỏ 99% thông tin không có độ tương phản hoặc không liên quan đến sinh tồn/cảm xúc.",
            "probability_truth": "Quy tắc nhân với số 0: Dù kỹ thuật hoàn hảo 99%, chỉ cần vi phạm 1 niềm tin cốt lõi (nhân với 0), toàn bộ hệ thống sụp đổ."
        },
        "layer_engineering": {
            "architecture": "Kiến trúc module hóa lỏng (Decoupled Modular Architecture): Tách biệt tầng logic dữ liệu, tầng phối hợp AI Agents và tầng giao diện cảm xúc.",
            "friction_and_costs": "Tối thiểu hóa chi phí giao dịch (Transaction Costs): Mỗi thao tác dư thừa của con người làm giảm 20% tỷ lệ hoàn thành mục tiêu.",
            "fail_safes": "Thiết lập biên an toàn 3 tầng (Graceful Degradation): Khi AI gặp lỗi hoặc nghẽn mạng, tự động kích hoạt chế độ dự phòng an toàn tuyệt đối."
        },
        "layer_arts_humanities": {
            "aesthetic_taste": "Áp dụng triết lý tối giản Dieter Rams (Ít nhưng tốt hơn - Less but better): Loại bỏ mọi hoa văn giả tạo; hình thức phụng sự công năng tối thượng.",
            "narrative_soul": "Cấu trúc kịch nghệ 3 hồi: Dẫn dắt người dùng từ bế tắc hiện tại, qua vực thẳm thử thách, đến giải pháp giải phóng năng lực cá nhân.",
            "human_ethics": "Tôn trọng phẩm giá và quyền tự quyết của con người: AI/Robot chỉ là người trợ lý tăng cường năng lực (Augmentation), không thay thế quyền tự chủ của con người."
        },
        "master_prompt": {
            "role_and_mission": f"Bạn là Chuyên gia Cao cấp kiêm Trợ lý Trực chiến. Hãy giải quyết bài toán: '{intent}'.",
            "hard_constraints": [
                "Cung cấp giải pháp có tính khả thi toán học và vật lý rõ ràng.",
                "Loại bỏ 90% từ ngữ sáo rỗng, tập trung vào hành động đòn bẩy cao nhất.",
                "Đưa ra các bước thực thi chi tiết có thể đo lường được."
            ],
            "taste_and_style": "Ngắn gọn, sắc bén, mang phong cách thiết kế tối giản Bauhaus; từ ngữ giàu tính gợi cảm và chân thật.",
            "negative_rules": [
                "Tuyệt đối không trả lời chung chung mang tính lý thuyết suông.",
                "Không tạo ra ảo tưởng hoàn hảo; luôn chỉ rõ rủi ro và điều kiện biên."
            ],
            "acceptance_criteria": [
                "Người thực thi có thể bắt tay vào làm ngay trong 5 phút đầu tiên.",
                "Có sẵn chỉ số đo lường hiệu quả định lượng (KPI) cụ thể."
            ]
        },
        "contrast_analysis": {
            "amateur_prompt": f"Hãy giúp tôi làm cái này: {intent}. Cho tôi ý tưởng hay nhé.",
            "why_amateur_fails": "Câu lệnh quá mơ hồ, thiếu ràng buộc kỹ thuật, không có tiêu chuẩn thẩm mỹ và không có tiêu chí kiểm thử; AI sẽ trả về văn bản chung chung vô hồn.",
            "polymath_advantage": "Bản Formulate đa ngành khóa chặt ranh giới khoa học, tối ưu hóa kiến trúc kỹ thuật và thổi linh hồn nghệ thuật vào giải pháp."
        },
        "farrow_compression": {
            "anchor_1": "🏛️ TƯỢNG CẨM THẠCH: Giới hạn vật lý & chân lý gốc không thể bẻ cong",
            "anchor_2": "⚙️ BÁNH RĂNG TITAN: Kiến trúc module tối giản chi phí biên",
            "anchor_3": "🎨 CỌ VẼ VÀNG: Gu thẩm mỹ tinh tế chạm vào nhân tính",
            "reflex_mantra": "Biết mình muốn gì qua 3 lăng kính Khoa học - Kỹ thuật - Nghệ thuật trước khi ra lệnh cho Robot!"
        }
    }


def sculpt_polymath_problem(user_intent: str, domain_focus: str = "Tất cả (Polymath 3 Miền)") -> Dict[str, Any]:
    """
    Điêu khắc bài toán thô thành Bản Đặc Tả Tinh Hoa cho AI/Robot theo chuẩn Polymath.
    Tự động xoay tua API key từ .env / st.secrets và có fallback heuristic.
    """
    cleaned_intent = user_intent.strip()
    if not cleaned_intent:
        cleaned_intent = "Xây dựng hệ thống tự động hóa phục vụ cuộc sống và công việc."

    keys = get_all_gemini_api_keys()
    
    if genai and keys:
        prompt_content = f"""Ý ĐỊNH THÔ CỦA CON NGƯỜI CẦN ĐIÊU KHẮC:
\"\"\"{cleaned_intent}\"\"\"

LĨNH VỰC TRỌNG TÂM: {domain_focus}

Hãy phân tích và điêu khắc theo đúng 4 tầng bách khoa (Sciences -> Engineering -> Arts/Humanities -> Master Prompt) và trả về JSON hợp lệ theo đúng cấu trúc đã chỉ định."""

        for api_key in keys:
            try:
                genai.configure(api_key=api_key)
                # Thử các model mới nhất của Gemini
                for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=POLYMATH_FORMULATION_SYSTEM_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        response = model.generate_content(prompt_content)
                        raw_text = response.text.strip()
                        
                        # Làm sạch JSON markdown wrapper nếu có
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                        raw_text = raw_text.strip()
                        
                        data = json.loads(raw_text)
                        if isinstance(data, dict) and "master_prompt" in data:
                            return data
                    except Exception:
                        continue
            except Exception:
                continue

    # Nếu tất cả API keys đều thất bại hoặc offline, kích hoạt bộ phân tích Heuristic
    return _generate_polymath_fallback_heuristic(cleaned_intent)
