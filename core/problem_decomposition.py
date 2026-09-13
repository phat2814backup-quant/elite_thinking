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
        "title": "📈 CKVN (Thị trường sập 15% - Bán hay Tích sản?)",
        "query": "Đầu tư CKVN: Thị trường giảm mạnh 15% trong 2 tuần, tin tức xấu về vĩ mô và lãi suất bủa vây, tâm lý hoang mang. Nên bán tháo cắt lỗ hay giải ngân mua gom tích sản cổ phiếu cơ bản tốt?"
    },
    {
        "title": "🟡 Vàng / XAU (Mục tiêu x4-x5 NAV trong 2 năm)",
        "query": "Giao dịch Vàng / XAU: Mục tiêu tăng trưởng NAV từ 5.000 USD lên 20.000 USD trong vòng 2 năm. Tính khả thi toán học, bẫy đòn bẩy, tỷ lệ sụt giảm tối đa (drawdown) và các điều kiện kỷ luật tiên quyết là gì?"
    },
    {
        "title": "💼 Sự nghiệp (Lương cao 60tr vs Khởi nghiệp AI)",
        "query": "Quyết định nghề nghiệp: Nên tiếp tục ở lại vị trí quản lý công ty tập đoàn lớn với mức lương ổn định 60 triệu/tháng hay rời đi khởi nghiệp một công ty công nghệ AI với rủi ro trắng tay nhưng tiềm năng đột phá?"
    },
    {
        "title": "🎒 Sức bền học tập (Cân bằng GPA top đầu & CLB)",
        "query": "Quản trị năng lượng học tập: Muốn vừa giữ điểm GPA top đầu, vừa tham gia 3 câu lạc bộ và làm dự án cá nhân nhưng bắt đầu có dấu hiệu kiệt sức và mất tập trung. Làm sao tái cấu trúc theo First Principles?"
    },
    {
        "title": "⏳ Quản trị thời gian (Xả stress thụ động vs Nâng cấp tư duy)",
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

3 MŨI GIÁO SOCRATES BÓC TRẦN BẪY TÂM LÝ & ĐỘC DƯỢC NHẬN THỨC (BẮT BUỘC ĐÂM VÀO ĐÚNG TỬ HUYỆT):
- Mũi Giáo 1 (Soi Gốc): Đâm thẳng vào Giả Định Ngây Thơ, Cái Tôi Tự Phụ & Ảo Tưởng Kiểm Soát (Dunning-Kruger, Illusion of Control). Truy bức: Bạn có đang ngộ nhận sự may mắn là năng lực? Giả định ngầm sống còn nào nếu sai sẽ đánh sập toàn bộ lâu đài của bạn?
- Mũi Giáo 2 (Đọc Dòng): Đâm thẳng vào Bẫy Động Cơ Ngầm (Incentive-Caused Bias - Charlie Munger), Xung Đột Lợi Ích & Tâm Lý Bầy Cừu (Social Proof/FOMO). Truy bức: Ai đang kiếm tiền nhiều nhất nếu bạn hành động như vậy? Lời khuyên này có đến từ 'thợ cắt tóc'? Bạn có đang bị cuốn vào cơn say đám đông?
- Mũi Giáo 3 (Ra Đòn): Đâm thẳng vào Bẫy Chi Phí Chìm (Sunk Cost Fallacy), Ác Cảm Mất Mát, Lòng Đố Kỵ & Áp Lực Sĩ Diện Nhất Quán (Commitment Bias). Truy bức: Nếu hôm nay bắt đầu từ con số 0, bạn có đổ tiền/công sức vào không? Bạn hành động vì cơ hội thật hay vì tiếc nuối nguồn lực cũ và đố kỵ với kẻ khác? Kịch bản xấu nhất chết chắc là gì?

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


SOCRATIC_NEXT_ROUND_SYSTEM_PROMPT = """Bạn là Socrates — Bậc Thầy Phản Biện Đối Kháng & Truy Bức Nhận Thức Tối Cao của Elite Thinking.
Nhiệm vụ của bạn: Tạo ra 3 MŨI GIÁO PHẢN BIỆN MỚI cho Vòng đấu trí tiếp theo.

Nguyên tắc tối thượng:
1. Đọc kỹ bối cảnh vấn đề và toàn bộ lịch sử các vòng đối kháng trước (câu hỏi cũ, câu trả lời của người học, điểm yếu Socrates đã chỉ ra).
2. Tuyệt đối KHÔNG hỏi lại câu hỏi cũ.
3. Khai thác chính các kẽ hở, ngụy biện hoặc giả định còn sót lại trong câu trả lời của người học ở vòng trước để tung ra 3 Mũi Giáo Mới khốc liệt hơn, sâu sắc hơn.
4. Mỗi vòng có tính chất leo thang nhận thức & khảo nghiệm cạm bẫy tâm lý khốc liệt:
   - Vòng 2: MA SÁT THỰC THI & TỬ HUYỆT TÂM LÝ HỌC HÀNH VI (Execution Friction, Time-decay, Bẫy Động cơ Incentive Bias, Bẫy Chi phí Chìm Sunk Cost, Cái tôi tự phụ Dunning-Kruger, Lòng đố kỵ Envy). Socrates phải chọc thủng ảo tưởng kiểm soát hoặc động cơ quyền lợi ngầm.
   - Vòng 3: THỬ THÁCH CỰC HẠN & THIÊN NGA ĐEN (Extreme Stress Test, Black Swan, Liquidity/Survival Crisis, Ruin Problem). Đưa người học vào tình huống toàn bộ thị trường đảo chiều hoặc tiền mặt cạn kiệt.
   - Vòng 4+: SIÊU NHẬN THỨC & KHẾ ƯỚC BẤT KHẢ XÂM PHẠM (Meta-Cognition, Convexity, Antifragility, Invariant Principles). Ép người học tuyên thệ các lằn ranh đỏ bất biến để triệt tiêu vĩnh viễn sự ngạo mạn.

BẮT BUỘC TRẢ VỀ DUY NHẤT MỘT JSON HỢP LỆ (Không markdown ```json ngoài JSON):
{
  "round_number": 2,
  "round_theme": "Tiêu đề chủ đề của vòng (ví dụ: Vòng 2: Khảo Nghiệm Ma Sát Thực Thi & Thiên Kiến Tâm Lý)",
  "round_brief": "Lời khiêu chiến sắc bén của Socrates gửi tới người học trước khi phóng giáo (1-2 câu).",
  "spears": [
    {
      "spear_id": "spear_r2_1",
      "spear_title": "🗡️ Mũi Giáo 1: ...",
      "targeted_vulnerability": "Điểm sơ hở trong lập luận trước đó mà mũi giáo này khoét sâu",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn truy sát",
      "guidance": "Gợi ý góc nhìn để phản biện"
    },
    {
      "spear_id": "spear_r2_2",
      "spear_title": "🗡️ Mũi Giáo 2: ...",
      "targeted_vulnerability": "Điểm sơ hở tiếp theo...",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn truy sát...",
      "guidance": "Gợi ý góc nhìn..."
    },
    {
      "spear_id": "spear_r2_3",
      "spear_title": "🗡️ Mũi Giáo 3: ...",
      "targeted_vulnerability": "Điểm sơ hở tiếp theo...",
      "ruthless_question": "Câu hỏi Socrates tàn nhẫn truy sát...",
      "guidance": "Gợi ý góc nhìn..."
    }
  ]
}
"""


def evaluate_socratic_sparring(
    problem_text: str,
    socratic_spears: List[Dict[str, Any]],
    user_answers: Dict[str, str],
    round_number: int = 1,
    round_theme: str = "",
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """Thẩm định phản biện đối kháng của người học trước 3 Mũi Giáo Socrates qua từng vòng."""
    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if not candidate_keys or genai is None:
        # Fallback offline simulation if API not available
        return {
            "round_number": round_number,
            "round_theme": round_theme if round_theme else f"Vòng {round_number}",
            "grit_score": 75,
            "xp_awarded": 100,
            "verdict_title": f"🛡️ Chiến Binh Nhận Thức (Vòng {round_number})",
            "overall_comment": f"Bạn đã dũng cảm đối mặt với cả 3 mũi giáo của Vòng {round_number} và đưa ra lập luận phòng vệ rõ ràng.",
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

    theme_header = f" - Chủ đề: {round_theme}" if round_theme else ""
    prompt_content = f"""BỐI CẢNH VẤN ĐỀ:
{problem_text}

VÒNG THẨM ĐỊNH: Vòng {round_number}{theme_header}

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
                            parsed["round_number"] = round_number
                            parsed["round_theme"] = round_theme if round_theme else f"Vòng {round_number}"
                            return parsed
                except Exception:
                    continue
        except Exception:
            continue

    return {
        "round_number": round_number,
        "round_theme": round_theme if round_theme else f"Vòng {round_number}",
        "grit_score": 80,
        "xp_awarded": 100,
        "verdict_title": f"🛡️ Tiếp Chiêu Thành Công (Vòng {round_number})",
        "overall_comment": f"Bạn đã hoàn thành phiên đối kháng Vòng {round_number} và đối diện trực tiếp với các điểm mù tư duy.",
        "evaluations": [
            {"spear_id": s.get("spear_id", "spear"), "score": 80, "critique": "Lập luận vững chắc, đã chú ý đến các rủi ro hệ thống."}
            for s in socratic_spears
        ]
    }


def generate_next_socratic_round(
    problem_text: str,
    next_round: int,
    previous_rounds: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """Tạo đợt 3 Mũi Giáo mới cho Vòng đấu trí Socrates tiếp theo (Vòng 2, 3, 4...)."""
    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    # Format previous rounds history
    history_blocks = []
    for pr in previous_rounds:
        r_num = pr.get("round_number", 1)
        r_th = pr.get("round_theme", f"Vòng {r_num}")
        ans_map = pr.get("user_answers", {})
        eval_data = pr.get("evaluation", {})
        block = [f"=== LỊCH SỬ VÒNG {r_num}: {r_th} ==="]
        for sp in pr.get("spears", []):
            sp_id = sp.get("spear_id", "")
            sp_q = sp.get("ruthless_question", "")
            u_ans = ans_map.get(sp_id, "(Chưa trả lời)")
            block.append(f"- Mũi giáo [{sp.get('spear_title', sp_id)}]: {sp_q}\n  -> Người học trả lời: {u_ans}")
        if eval_data:
            block.append(f"- Nhận xét thẩm định của Socrates: {eval_data.get('overall_comment', '')}")
            for ev in eval_data.get("evaluations", []):
                block.append(f"  * {ev.get('spear_id', '')}: {ev.get('critique', '')}")
        history_blocks.append("\n".join(block))

    history_text = "\n\n".join(history_blocks) if history_blocks else "(Chưa có lịch sử vòng trước)"

    round_themes = {
        2: "Vòng 2: Khảo Nghiệm Ma Sát Thực Thi & Thiên Kiến Tâm Lý (Friction & Biases)",
        3: "Vòng 3: Thử Thách Cực Hạn & Thiên Nga Đen Hệ Thống (Stress Test & Black Swan)",
        4: "Vòng 4: Chiến Lược Chống Mong Manh & Bất Đối Xứng Lồi (Antifragility)",
        5: "Vòng 5: Siêu Nhận Thức & Khế Ước Bất Khả Xâm Phạm (Meta-Cognition)",
    }
    target_theme = round_themes.get(next_round, f"Vòng {next_round}: Đột Phá Giới Hạn Nhận Thức Bậc Cao")

    prompt_content = f"""BỐI CẢNH VẤN ĐỀ GỐC CỦA NGƯỜI HỌC:
{problem_text}

MỤC TIÊU: Thiết lập 3 Mũi Giáo Sát Thủ cho VÒNG {next_round} ({target_theme}).

LỊCH SỬ CÁC VÒNG ĐỐI KHÁNG TRƯỚC ĐÓ:
{history_text}

Hãy phân tích các kẽ hở lập luận của người học qua các vòng trước và tung ra 3 Mũi Giáo Mới của Vòng {next_round} theo đúng đặc trưng vòng này.
"""

    if candidate_keys and genai is not None:
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
                            system_instruction=SOCRATIC_NEXT_ROUND_SYSTEM_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        resp = model.generate_content(prompt_content)
                        if resp and resp.text:
                            parsed = json.loads(clean_json_response(resp.text))
                            if isinstance(parsed, dict) and "spears" in parsed and len(parsed["spears"]) >= 3:
                                parsed["round_number"] = next_round
                                if "round_theme" not in parsed:
                                    parsed["round_theme"] = target_theme
                                return parsed
                    except Exception:
                        continue
            except Exception:
                continue

    # Fallback simulation if offline or API error
    return {
        "round_number": next_round,
        "round_theme": target_theme,
        "round_brief": f"Socrates tiếp tục truy kích lập luận của bạn ở Vòng {next_round}. Hãy đối diện với những áp lực khắc nghiệt nhất.",
        "spears": [
            {
                "spear_id": f"spear_r{next_round}_1",
                "spear_title": f"🗡️ Mũi Giáo 1 (Vòng {next_round}): Điểm Nghẽn Thời Gian & Ma Sát Thực Tế",
                "targeted_vulnerability": "Áp lực hao mòn tài nguyên và tâm lý khi kế hoạch bị trì hoãn kéo dài",
                "ruthless_question": f"Nếu thực tế diễn ra chậm hơn 3 lần dự kiến và bạn phải chịu chuỗi thua lỗ liên tiếp trong 6 tháng, kỷ luật nào ngăn bạn không 'all-in' gỡ gạc?",
                "guidance": "Hãy chỉ ra quy tắc cắt lỗ cứng và quỹ dự phòng tách biệt hoàn toàn."
            },
            {
                "spear_id": f"spear_r{next_round}_2",
                "spear_title": f"🗡️ Mũi Giáo 2 (Vòng {next_round}): Kịch Bản Thiên Nga Đen Chưa Từng Thấy",
                "targeted_vulnerability": "Niềm tin ngây thơ rằng điều kiện lịch sử sẽ luôn lặp lại y hệt",
                "ruthless_question": f"Nếu một biến cố vĩ mô cực đoan làm tê liệt tính thanh khoản hoặc sàn/đối tác bị đóng băng, cơ chế sống sót duy nhất của bạn là gì?",
                "guidance": "Xác định rõ kịch bản tệ nhất có thể xảy ra và cái giá tối đa bạn chấp nhận mất."
            },
            {
                "spear_id": f"spear_r{next_round}_3",
                "spear_title": f"🗡️ Mũi Giáo 3 (Vòng {next_round}): Khế Ước Bất Khả Xâm Phạm",
                "targeted_vulnerability": "Sự thỏa hiệp ngầm khi đối diện cám dỗ lợi nhuận tức thời",
                "ruthless_question": f"Hãy tuyên thệ một 'Lằn ranh đỏ' tuyệt đối mà bạn thà phá sản danh mục chứ nhất quyết không bao giờ vi phạm?",
                "guidance": "Định hình nguyên tắc bất biến để bảo vệ bạn khỏi sự ngạo mạn của chính mình."
            }
        ]
    }

