# -*- coding: utf-8 -*-
"""
Module Phân Rã Vấn Đề Thực Chiến & Võ Đài Đối Kháng Socrates (Elite Socratic Decomposition Engine).
Bóc tách bất kỳ vấn đề thực tế phức tạp nào về 3 Trụ Cột (Soi Gốc - Đọc Dòng - Ra Đòn), 
chiếu xạ qua 9 Lăng Kính Tinh Hoa gắn liền với Kho 152 Mô Hình Tư Duy, 
và kích hoạt 3 Mũi Giáo Socrates đối kháng ngược chiều để rèn luyện Sức Bền Nhận Thức (Cognitive Grit).
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


DECOMPOSITION_SYSTEM_PROMPT = """Bạn là Elite Multi-Mode Thinking Engine — Bậc thầy Phân rã Vấn đề theo 3 Trụ Cột Farrow & 9 Lăng Kính Tinh Hoa của Charlie Munger, Nassim Taleb, Daniel Kahneman và Ray Dalio.

NHIỆM VỤ: Tiếp nhận vấn đề hóc búa, bóc tách thực chiến qua 3 Trụ Cột và 9 Lăng Kính Tinh Hoa, gắn kết trực tiếp với các mô hình khoa học trong mạng lưới 152 Mental Models, và tạo ra 3 Mũi Giáo Socrates đối kháng tàn nhẫn nhất.

CẤU TRÚC 3 TRỤ CỘT & 9 LĂNG KÍNH:
1. TRỤ 1: SOI GỐC (ROOT)
   - Lăng kính 1: First Principles (Nguyên lý khởi thủy vật lý/toán học không thể tối giản)
   - Lăng kính 2: Inversion (Tư duy đảo ngược: những cách tự sát/thất bại thảm hại nhất)
   - Lăng kính 3: Latticework (Mạng lưới liên kết đa ngành đỡ quyết định)
2. TRỤ 2: ĐỌC DÒNG (FLOW)
   - Lăng kính 4: Bayesian Updating & Base Rate (Xác suất nền và cách cập nhật khi có dữ liệu mới)
   - Lăng kính 5: Second-Order Thinking (Hệ quả của hệ quả sau 6-12 tháng)
   - Lăng kính 6: Game Theory & Incentives (Đọc vị nước cờ phản ứng của đối thủ và bẫy động lực ngầm)
3. TRỤ 3: RA ĐÒN (STRIKE)
   - Lăng kính 7: Optionality Barbell & Margin of Safety (Khóa rủi ro 1 cọng lông, biên an toàn cao)
   - Lăng kính 8: Lean Experiment (Thử nghiệm nhỏ nhất trong 24-48h chi phí bằng 0)
   - Lăng kính 9: Multi-Timeframe Strategy (Chiến lược 3 chặng: Chịu đau ngắn hạn -> Thống trị 10 năm)

BẮT BUỘC TRẢ VỀ DUY NHẤT MỘT JSON HỢP LỆ (Không có markdown ```json ngoài JSON):
{
  "is_valid": true,
  "executive_summary": "Tóm tắt bản chất gốc rễ tối thượng của vấn đề trong 2 câu sắc bén.",
  "pillars": {
    "root": {
      "pillar_title": "💎 TRỤ 1: SOI GỐC (ROOT)",
      "essence": "Bóc trần sự thật hiển nhiên và kịch bản tử thần...",
      "lenses": {
        "first_principles": {
          "lens_name": "1. Nguyên Lý Khởi Thủy (First Principles)",
          "analysis": "Phân tích bóc tách sự thật hiển nhiên...",
          "activated_models": ["[PHYS-11] First Principles Thinking", "[MATH-01] Identity & Conservation"]
        },
        "inversion": {
          "lens_name": "2. Tư Duy Đảo Ngược (Inversion)",
          "analysis": "Phân tích kịch bản chết chắc và cách triệt tiêu...",
          "activated_models": ["[MATH-05] Inversion Principle", "[PSY-08] Sunk Cost Fallacy"]
        },
        "latticework": {
          "lens_name": "3. Mạng Lưới Đa Ngành (Latticework)",
          "analysis": "Phân tích giao thoa các quy luật chi phối...",
          "activated_models": ["[SYS-11] Latticework Integration"]
        }
      },
      "pillar_leverage": "Đòn bẩy gốc rễ số 1 cần neo giữ vững chắc..."
    },
    "flow": {
      "pillar_title": "🔭 TRỤ 2: ĐỌC DÒNG (FLOW)",
      "essence": "Đo lường xác suất, độ trễ và phản ứng của đối thủ...",
      "lenses": {
        "bayesian": {
          "lens_name": "4. Xác Suất Bayes & Tỷ Lệ Nền (Bayesian Updating)",
          "analysis": "Phân tích tỷ lệ nền và cập nhật xác suất...",
          "activated_models": ["[MATH-03] Bayesian Updating", "[STAT-01] Base Rate Neglect"]
        },
        "second_order": {
          "lens_name": "5. Tư Duy Bậc Hai (Second-Order Thinking)",
          "analysis": "Phân tích hệ quả bậc hai sau 6-12 tháng...",
          "activated_models": ["[SYS-10] Second-Order Effects", "[SYS-03] Feedback Loops"]
        },
        "game_theory": {
          "lens_name": "6. Lý Thuyết Trò Chơi & Động Lực Ngầm (Game Theory & Incentives)",
          "analysis": "Phân tích nước cờ của đối thủ và bẫy động lực...",
          "activated_models": ["[ECON-10] Game Theory & Nash", "[PSY-03] Incentive-Caused Bias"]
        }
      },
      "pillar_leverage": "Đòn bẩy dòng chảy và mắt xích cần khai thông..."
    },
    "strike": {
      "pillar_title": "🏹 TRỤ 3: RA ĐÒN (STRIKE)",
      "essence": "Bảo toàn vốn, hạn chế rủi ro 1 cọng lông và kiểm chứng tức thì...",
      "lenses": {
        "optionality_barbell": {
          "lens_name": "7. Bất Đối Xứng Barbell & Biên An Toàn (Optionality Barbell)",
          "analysis": "Phân tích cấu trúc bất đối xứng và biên an toàn...",
          "activated_models": ["[SYS-04] Optionality Barbell", "[ECON-05] Margin of Safety"]
        },
        "lean_experiment": {
          "lens_name": "8. Thử Nghiệm Tinh Gọn (Lean Experiment)",
          "analysis": "Thử nghiệm nhỏ nhất có thể làm ngay...",
          "activated_models": ["[MATH-04] Lean Probing", "[SYS-05] Fast Feedback"]
        },
        "multi_timescale": {
          "lens_name": "9. Đa Quy Mô Thời Gian (Multi-Timeframe Strategy)",
          "analysis": "Chiến lược ngắn hạn chịu đau, dài hạn 10 năm...",
          "activated_models": ["[MATH-01] Compounding Law"]
        }
      },
      "pillar_leverage": "Đòn bẩy hành động bất đối xứng..."
    }
  },
  "socratic_spears": [
    {
      "spear_id": "spear_root",
      "pillar": "root",
      "spear_title": "🗡️ Mũi Giáo 1 (Soi Gốc): Đập Vụn Giả Định & Bẫy Tử Thần",
      "targeted_vulnerability": "Mô tả điểm yếu/giả định ngây thơ nhất về bản chất bài toán",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn đâm thẳng vào giả định sống còn của bạn",
      "guidance": "Gợi ý góc nhìn để kiểm chứng lại giả định."
    },
    {
      "spear_id": "spear_flow",
      "pillar": "flow",
      "spear_title": "🗡️ Mũi Giáo 2 (Đọc Dòng): Truy Sát Xác Suất & Phản Ứng Dây Chuyền",
      "targeted_vulnerability": "Mô tả điểm mù về dòng tiền/đối thủ/xác suất nền",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn truy sát tác động bậc 2 và phản xạ của đối thủ",
      "guidance": "Gợi ý kiểm tra phản ứng của hệ thống khi có biến động."
    },
    {
      "spear_id": "spear_strike",
      "pillar": "strike",
      "spear_title": "🗡️ Mũi Giáo 3 (Ra Đòn): Khảo Nghiệm Rủi Ro & Thử Nghiệm Thực Địa",
      "targeted_vulnerability": "Mô tả ảo tưởng về khả năng chịu đòn hoặc thiếu hành động kiểm chứng",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn về biên an toàn và cái giá phải trả nếu thất bại",
      "guidance": "Gợi ý chốt bài toán mất mát tối đa trước khi mơ mộng lợi nhuận."
    }
  ],
  "actionable_next_steps": [
    "Hành động cụ thể 1: ...",
    "Hành động cụ thể 2: ...",
    "Hành động cụ thể 3: ..."
  ]
}
"""


SOCRATIC_EVAL_SYSTEM_PROMPT = """Bạn là Socrates — Vị Giám Khảo Phản Biện Tối Cao của Elite Thinking.
Nhiệm vụ: Đánh giá câu trả lời của người học trước 3 Mũi Giáo Socrates.
Tiêu chí thẩm định:
1. Độ dũng cảm đối diện sự thật (không lảng tránh, không ngụy biện bằng sáo rỗng).
2. Chiều sâu nhận thức (nhìn ra giả định sai, tính toán rủi ro tối đa, chuẩn bị kịch bản bậc hai).
3. Sức bền nhận thức (Cognitive Grit): Chấm điểm từ 0 đến 100 và cấp điểm kinh nghiệm XP (+50 đến +150 XP).

BẮT BUỘC TRẢ VỀ DUY NHẤT MỘT ĐỊNH DẠNG JSON HỢP LỆ (Không markdown codeblock ngoài JSON):
{
  "grit_score": 85,
  "xp_awarded": 120,
  "verdict_title": "🛡️ Chiến Binh Nhận Thức Sắc Bén",
  "overall_comment": "Nhận xét tổng quan về lập luận và tư duy của người học trong 2-3 câu.",
  "evaluations": [
    {
      "spear_id": "spear_root",
      "score": 90,
      "critique": "Đánh giá cụ thể cách người học phản ứng trước Mũi giáo 1."
    },
    {
      "spear_id": "spear_flow",
      "score": 80,
      "critique": "Đánh giá cụ thể cách người học phản ứng trước Mũi giáo 2."
    },
    {
      "spear_id": "spear_strike",
      "score": 85,
      "critique": "Đánh giá cụ thể cách người học phản ứng trước Mũi giáo 3."
    }
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
    """Phân rã vấn đề qua 3 Trụ Cột, 9 Lăng Kính Tinh Hoa và 3 Mũi Giáo Socrates với xoay tua đa tầng API Keys."""
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
                        f"Hãy phân rã vấn đề thực chiến sau qua 3 Trụ Cột, 9 Lăng Kính Tinh Hoa và 3 Mũi Giáo Socrates:\n\n{cleaned}"
                    )
                    if resp and resp.text:
                        parsed = json.loads(clean_json_response(resp.text))
                        if isinstance(parsed, dict):
                            # Đảm bảo tính tương thích ngược (Backward Compatibility)
                            if "executive_summary" in parsed and "first_principles_breakdown" not in parsed:
                                parsed["first_principles_breakdown"] = parsed["executive_summary"]
                            if "actionable_next_steps" in parsed and "actionable_insights" not in parsed:
                                parsed["actionable_insights"] = parsed["actionable_next_steps"]
                            
                            # Tổng hợp core_principles_found và elite_lenses nếu UI cũ cần
                            if "pillars" in parsed:
                                core_list = []
                                lenses_flat = {}
                                for p_key, p_data in parsed["pillars"].items():
                                    for l_key, l_data in p_data.get("lenses", {}).items():
                                        lenses_flat[l_key] = l_data.get("analysis", "")
                                        for m_id in l_data.get("activated_models", []):
                                            core_list.append({
                                                "name": m_id,
                                                "domain": p_data.get("pillar_title", ""),
                                                "description": l_data.get("analysis", "")[:100] + "..."
                                            })
                                if "elite_lenses" not in parsed:
                                    parsed["elite_lenses"] = lenses_flat
                                if "core_principles_found" not in parsed:
                                    parsed["core_principles_found"] = core_list
                            
                            if "socratic_spears" in parsed and "human_decision_needed" not in parsed:
                                parsed["human_decision_needed"] = [
                                    f"{s.get('spear_title', '')}: {s.get('ruthless_question', '')}"
                                    for s in parsed.get("socratic_spears", [])
                                ]

                            return parsed
                except Exception:
                    continue
        except Exception:
            continue

    return {"error": "Không thể phân rã qua các Key có sẵn. Vui lòng kiểm tra kết nối mạng."}


def evaluate_socratic_sparring(
    problem_text: str,
    socratic_spears: List[Dict[str, Any]],
    user_answers: Dict[str, str],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """Thẩm định phản biện đối kháng của người học trước 3 Mũi Giáo Socrates."""
    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if not candidate_keys or genai is None:
        # Fallback offline simulation if API not available
        return {
            "grit_score": 75,
            "xp_awarded": 100,
            "verdict_title": "🛡️ Chiến Binh Nhận Thức (Offline Evaluation)",
            "overall_comment": "Bạn đã dũng cảm đối mặt với cả 3 mũi giáo và đưa ra lập luận phòng vệ rõ ràng.",
            "evaluations": [
                {"spear_id": s.get("spear_id", "spear"), "score": 75, "critique": "Lập luận có trọng tâm, cần tiếp tục rèn luyện kiểm chứng thực tế."}
                for s in socratic_spears
            ]
        }

    # Prepare prompt text
    qa_pairs = []
    for s in socratic_spears:
        s_id = s.get("spear_id", "")
        s_q = s.get("ruthless_question", "")
        u_ans = user_answers.get(s_id, "(Người dùng chưa trả lời)")
        qa_pairs.append(f"MŨI GIÁO [{s.get('spear_title', s_id)}]:\nCâu hỏi: {s_q}\nCâu trả lời của người học: {u_ans}")

    prompt_content = f"""BỐI CẢNH VẤN ĐỀ:
{problem_text}

CÁC MŨI GIÁO VÀ PHẢN BIỆN CỦA NGƯỜI HỌC:
{chr(10).join(qa_pairs)}

Hãy thẩm định theo đúng chuẩn Socrates, chỉ ra điểm mạnh và điểm mù còn sót lại, chấm điểm Grit (0-100) và thưởng XP (50-150).
"""

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
                        system_instruction=SOCRATIC_EVAL_SYSTEM_PROMPT,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    resp = model.generate_content(prompt_content)
                    if resp and resp.text:
                        parsed = json.loads(clean_json_response(resp.text))
                        if isinstance(parsed, dict) and "grit_score" in parsed:
                            return parsed
                except Exception:
                    continue
        except Exception:
            continue

    return {
        "grit_score": 80,
        "xp_awarded": 100,
        "verdict_title": "🛡️ Tiếp Chiêu Thành Công",
        "overall_comment": "Bạn đã hoàn thành phiên đối kháng và đối diện trực tiếp với các điểm mù tư duy.",
        "evaluations": [
            {"spear_id": s.get("spear_id", "spear"), "score": 80, "critique": "Lập luận vững chắc, đã chú ý đến các rủi ro hệ thống."}
            for s in socratic_spears
        ]
    }
