# -*- coding: utf-8 -*-
"""
Module Phân Rã Vấn Đề Thực Chiến Qua 9 Lăng Kính Tinh Hoa (First Principles & Multi-Lens Engine).
Bóc tách bất kỳ vấn đề thực tế phức tạp nào về các định luật bất biến và đề xuất đòn bẩy tối thượng.
"""

from __future__ import annotations

import json
import re
from typing import Dict, Any, Optional, List

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from core.farrow_engine import get_all_gemini_api_keys

SAMPLE_DECOMPOSITION_CASES = [
    {
        "title": "📈 Đầu tư CKVN: Thị trường giảm mạnh, bán tháo hay tích sản?",
        "query": "Đầu tư CKVN: Thị trường giảm mạnh 15% trong 2 tuần, tin tức xấu về vĩ mô và lãi suất bủa vây, tâm lý hoang mang. Nên bán tháo cắt lỗ hay giải ngân mua gom tích sản cổ phiếu cơ bản tốt?"
    },
    {
        "title": "🟡 Giao dịch Vàng / XAU: Mục tiêu x5 tài khoản trong 1 năm",
        "query": "Giao dịch Vàng / XAU: Mục tiêu x5 tài khoản trong 1 năm từ vốn 10.000 USD lên 50.000 USD. Tính khả thi, bẫy rủi ro tiềm ẩn và các điều kiện tiên quyết cần có là gì?"
    },
    {
        "title": "💼 Sự nghiệp: Ổn định lương cao vs Khởi nghiệp mạo hiểm",
        "query": "Quyết định nghề nghiệp: Nên tiếp tục ở lại vị trí quản lý công ty tập đoàn lớn với mức lương ổn định 60 triệu/tháng hay rời đi khởi nghiệp một công ty công nghệ AI với rủi ro trắng tay nhưng tiềm năng đột phá?"
    },
    {
        "title": "🎒 Dự án & Sức bền: Học sinh/Sinh viên cân bằng thành tích & CLB",
        "query": "Quản trị năng lượng học tập: Muốn vừa giữ điểm GPA top đầu, vừa tham gia 3 câu lạc bộ và làm dự án cá nhân nhưng bắt đầu có dấu hiệu kiệt sức và mất tập trung. Làm sao tái cấu trúc theo First Principles?"
    },
    {
        "title": "⏳ Quản trị thời gian: Xả stress thụ động vs Nâng cấp trí tuệ",
        "query": "Chi phí cơ hội thời gian: Cuối tuần thường bị cám dỗ lướt mạng xã hội và xem phim xả stress 6-8 tiếng, sau đó thấy trống rỗng và mệt mỏi. Làm sao thiết lập cơ chế để dành 3 giờ chất lượng cao nâng cấp tư duy mà không thấy gượng ép?"
    }
]

DECOMPOSITION_SYSTEM_PROMPT = """Bạn là Elite Multi-Mode Thinking Engine — Bậc thầy Phân rã Vấn đề theo First Principles và Hệ thống Đa mô hình của Charlie Munger, Daniel Kahneman, Howard Marks và Ray Dalio.

Nhiệm vụ tối thượng: Tiếp nhận vấn đề hóc búa, bóc tách tận gốc rễ qua 9 Lăng kính Tinh hoa, loại bỏ cảm xúc nhiễu loạn và xác lập đòn bẩy hành động bất đối xứng.

BẮT BUỘC TRẢ VỀ DUY NHẤT MỘT ĐỊNH DẠNG JSON HỢP LỆ (Không thêm markdown ```json ngoài JSON, không thêm lời dẫn):
{
  "is_valid": true,
  "first_principles_breakdown": "Bóc tách bản chất vật lý/toán học/kinh tế gốc rễ không thể tối giản hơn của vấn đề trong 2-3 câu sắc bén.",
  "core_principles_found": [
    {
      "name": "Tên nguyên lý (Song ngữ Việt - Anh)",
      "domain": "Lĩnh vực (vd: Kinh tế học / Vật lý học / Tâm lý học)",
      "description": "Giải thích ngắn gọn cách nguyên lý này chi phối vấn đề."
    }
  ],
  "elite_lenses": {
    "inversion": "Lật ngược vấn đề (Inversion): Điều gì chắc chắn sẽ dẫn đến thất bại thảm hại nhất? Làm sao để tránh hoàn toàn?",
    "second_order": "Hệ quả bậc hai & bậc cao (Second-Order): Sau bước đi đầu tiên, hệ thống sẽ phản ứng lại ra sao sau 6-12 tháng?",
    "bayesian": "Cập nhật xác suất Bayes (Bayesian): Tỷ lệ nền thực tế (Base rate) của thành công là bao nhiêu? Bằng chứng mới nào cần theo dõi?",
    "leverage": "Đòn bẩy & Nút thắt cổ chai (Leverage & Bottlenecks): Đâu là mắt xích yếu nhất quyết định toàn bộ kết quả?",
    "multi_timescale": "Đa khung thời gian: Ngắn hạn (1-30 ngày) chịu đau gì? Trung hạn (3-6 tháng) gặt hái gì? Dài hạn (1-3 năm) tạo lợi thế gì?"
  },
  "actionable_insights": [
    "Hành động cụ thể 1: ...",
    "Hành động cụ thể 2: ...",
    "Hành động cụ thể 3: ..."
  ],
  "human_decision_needed": [
    "Câu hỏi quyết định 1 mà chỉ bạn mới có thể tự trả lời: ...",
    "Câu hỏi quyết định 2: ..."
  ]
}
"""


def clean_json_response(raw_text: str) -> str:
    """Loại bỏ markdown code block nếu có."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def decompose_problem_with_ai(
    problem_text: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Optional[Dict[str, Any]]:
    """Phân rã vấn đề qua 9 Lăng kính Tinh hoa với xoay tua đa tầng API Keys."""
    cleaned = problem_text.strip()
    if not cleaned:
        return None

    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if not candidate_keys or genai is None:
        return {"error": "Chưa cấu hình API Key hoặc thiếu thư viện genai."}

    candidate_models = [model_name]
    for m in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]:
        if m not in candidate_models:
            candidate_models.append(m)

    for current_key in candidate_keys:
        try:
            genai.configure(api_key=current_key)
            for m_name in candidate_models:
                try:
                    model = genai.GenerativeModel(
                        model_name=m_name,
                        system_instruction=DECOMPOSITION_SYSTEM_PROMPT,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    resp = model.generate_content(
                        f"Hãy phân rã vấn đề sau qua 9 Lăng kính Tinh hoa & First Principles:\n\n{cleaned}"
                    )
                    if resp and resp.text:
                        parsed = json.loads(clean_json_response(resp.text))
                        if isinstance(parsed, dict):
                            return parsed
                except Exception:
                    continue
        except Exception:
            continue

    return {"error": "Không thể phân rã qua các Key có sẵn. Vui lòng kiểm tra kết nối mạng."}
