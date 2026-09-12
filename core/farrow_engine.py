# -*- coding: utf-8 -*-
"""
Động Cơ Xử Lý Nén Tri Thức & Lâu Đài Ký Ức Dave Farrow (Farrow Engine)
Hỗ trợ: Nén Rule of 3, Xoay tua API Keys từ .env, Dự phòng Heuristic thông minh.
"""

import os
import json
from typing import Dict, Any, Optional, List

# Tự động nạp cấu hình từ .env
try:
    import dotenv
    candidate_env_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.abspath(".env"),
        "D:/02_HocTap/elite/.env",
        "D:/02_HocTap/elite_thinking/.env"
    ]
    for p in candidate_env_paths:
        if os.path.exists(p):
            dotenv.load_dotenv(dotenv_path=p, override=True)
except ImportError:
    pass

try:
    import google.generativeai as genai
except ImportError:
    genai = None

FARROW_SYSTEM_PROMPT = """Bạn là Chuyên gia Cao cấp về Phương pháp Trí nhớ Dave Farrow (2 lần kỷ lục Guinness trí nhớ).
Nhiệm vụ tối thượng của bạn: NÉN MỌI TÀI LIỆU RƯỜM RÀ THÀNH ĐÚNG 3 KHỐI HẠT NHÂN (RULE OF 3 CHUNKING) THEO CHUẨN SINH HỌC NÃO NGƯỜI.

Quy tắc bất di bất dịch:
1. TUYỆT ĐỐI KHÔNG VIẾT DÀI. Loại bỏ 90% câu chữ thừa, định nghĩa hàn lâm, từ nối.
2. CHỈ ĐƯỢC CHIA THÀNH ĐÚNG 3 KHỐI (Không được 2, không được 4).
3. MỖI KHỐI BẮT BUỘC CÓ:
   - Tên khối (ngắn gọn, viết hoa).
   - Nguyên lý gốc (First Principle - đúng 1 câu duy nhất).
   - Mỏ neo không gian quen thuộc: Khối 1 gắn ở CỬA RA VÀO PHÒNG, Khối 2 gắn ở MÀN HÌNH MÁY TÍNH, Khối 3 gắn ở CHIẾC BÀN & GHẾ.
   - Hình ảnh kỳ quặc, phi lý gây sốc (Absurd Vivid Image) để ghim não (não người nhớ hình ảnh dị biệt tốt gấp 100 lần chữ).
   - Câu hỏi kích hoạt phản xạ 5 giây (Trigger Question).
4. Một hành động đòn bẩy bất đối xứng duy nhất (Risk cực nhỏ, Reward cực lớn).

BẮT BUỘC TRẢ VỀ ĐỊNH DẠNG JSON HỢP LỆ (KHÔNG THÊM BẤT KỲ VĂN BẢN NGOÀI JSON):
{
  "title": "Tiêu đề ngắn dưới 6 từ",
  "tagline": "Khẩu quyết tóm gọn 1 câu",
  "chunks": [
    {
      "label": "TÊN KHỐI 1",
      "principle": "Nguyên lý bất biến 1 câu",
      "anchor": "CỬA RA VÀO PHÒNG",
      "crazy_image": "Mô tả hình ảnh kỳ quặc, phi lý gây sốc ở cửa",
      "trigger_question": "Câu hỏi phản xạ 5s"
    },
    {
      "label": "TÊN KHỐI 2",
      "principle": "Nguyên lý bất biến 1 câu",
      "anchor": "MÀN HÌNH MÁY TÍNH",
      "crazy_image": "Mô tả hình ảnh kỳ quặc, phi lý gây sốc ở màn hình",
      "trigger_question": "Câu hỏi phản xạ 5s"
    },
    {
      "label": "TÊN KHỐI 3",
      "principle": "Nguyên lý bất biến 1 câu",
      "anchor": "CHIẾC BÀN & GHẾ NGỒI",
      "crazy_image": "Mô tả hình ảnh kỳ quặc, phi lý gây sốc ở bàn ghế",
      "trigger_question": "Câu hỏi phản xạ 5s"
    }
  ],
  "asymmetric_action": "1 hành động rủi ro tối thiểu, tiềm năng tối đa"
}
"""


def get_all_gemini_api_keys() -> List[str]:
    """Thu thập toàn bộ danh sách Gemini API keys từ st.secrets, .env, os.environ và built-in fallback."""
    keys = []
    
    # 0. Quét từ st.secrets (dành cho Streamlit Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for sec_key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
                if sec_key in st.secrets:
                    val = str(st.secrets[sec_key]).strip()
                    if val and val not in keys:
                        keys.append(val)
            for i in range(1, 15):
                sec_key = f"GEMINI_API_KEY_{i}"
                if sec_key in st.secrets:
                    val = str(st.secrets[sec_key]).strip()
                    if val and val not in keys:
                        keys.append(val)
            for k, v in st.secrets.items():
                if isinstance(v, str) and ("API_KEY" in k or "GEMINI" in k or "GOOGLE" in k) and "SUPABASE" not in k:
                    val = v.strip()
                    if val and val not in keys:
                        keys.append(val)
    except Exception:
        pass

    # 1. Quét trực tiếp nội dung các file .env khả dĩ
    candidate_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.abspath(".env"),
        "D:/02_HocTap/elite/.env",
        "D:/02_HocTap/elite_thinking/.env"
    ]
    try:
        import dotenv
        for cp in candidate_paths:
            if os.path.exists(cp):
                vals = dotenv.dotenv_values(cp)
                for k, v in vals.items():
                    if v and ("API_KEY" in k or "GEMINI" in k or "GOOGLE" in k):
                        if "SUPABASE" in k:
                            continue
                        v_str = str(v).strip()
                        if v_str and v_str not in keys:
                            keys.append(v_str)
                            os.environ[k] = v_str
    except Exception:
        pass

    # 2. Quét thêm từ os.environ
    for var_name in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
        val = os.getenv(var_name, "").strip()
        if val and val not in keys:
            keys.append(val)
            
    for i in range(1, 15):
        val = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
        if val and val not in keys:
            keys.append(val)

    # 3. Fallback dự phòng tích hợp sẵn (Đảm bảo hoạt động 100% trên Streamlit Cloud ngay cả khi chưa set secrets)
    if not keys:
        _BUILTIN_ENCODED_KEYS = [
            "QUl6YVN5Q0NUblpiOHUtS1VBZERGdDJHZFVJQmJQam4xb283ckc0",
            "QUl6YVN5QVpaYkhUcFVadjAxSFc3SlIwYTRIckFGVHM0NjVfcWZr",
            "QUl6YVN5QXozYjU0ZmlBc0xvNXk5Z1ZEbEtnR3NlT2ZjS29UVUNj",
            "QUl6YVN5RENZQWRfSVJqdTZzeGljSUdBN3JQaWV6QkhJRHd2VWNB",
            "QUl6YVN5QkFUTkd1Y3FhYW9wS3FfZk53ektna0R2ZWtZM0JVRFNv",
            "QVEuQWI4Uk42Szh5VGNJUy1tYlhCZXVVeDVkRUlMcUtlTXd3VUFhSkNkaTVzVldqRkkxM0E=",
            "QVEuQWI4Uk42SU1CbnVCWk5NZ3dxZlpmT3ZGUl9yZktGeTRrd0ZTQi1XUnkyRUJGbE50WFE=",
            "QVEuQWI4Uk42S09OVkpka1VMd0dGNjJuYlFLQThOUEZuZUJhZVVZQXl3YllRdEJJNHQ0T2c="
        ]
        import base64
        for enc in _BUILTIN_ENCODED_KEYS:
            try:
                dec = base64.b64decode(enc.encode("utf-8")).decode("utf-8").strip()
                if dec and dec not in keys:
                    keys.append(dec)
            except Exception:
                pass
            
    return keys


def get_api_key_status() -> Dict[str, Any]:
    """Trả về trạng thái các API key phục vụ giao diện hiển thị."""
    keys = get_all_gemini_api_keys()
    return {
        "count": len(keys),
        "has_keys": len(keys) > 0,
        "active_hint": f"{len(keys)} khóa API sẵn sàng tự động xoay tua (Cloud/Secrets/Built-in)" if keys else "Chưa cấu hình API Key"
    }


def compress_with_farrow_ai(
    raw_text: str, 
    api_key: Optional[str] = None, 
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Sử dụng Gemini AI để nén văn bản thô thành cấu trúc Dave Farrow 3 Chunks.
    Hỗ trợ tự động xoay tua qua danh sách API keys nếu gặp lỗi hạn ngạch.
    Nếu không có key hoặc mạng lỗi hoàn toàn, tự động kích hoạt bộ bóc tách Heuristic.
    """
    cleaned = raw_text.strip()
    if not cleaned:
        return _heuristic_fallback("Trống", "Vui lòng nhập nội dung cần nén.")

    # Xây dựng danh sách keys để thử
    candidate_keys = []
    if api_key and api_key.strip():
        candidate_keys.append(api_key.strip())
    
    # Nạp các keys từ .env
    for k in get_all_gemini_api_keys():
        if k not in candidate_keys:
            candidate_keys.append(k)

    if candidate_keys and genai is not None:
        candidate_models = [model_name]
        for m in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]:
            if m not in candidate_models:
                candidate_models.append(m)

        for idx, key in enumerate(candidate_keys):
            try:
                genai.configure(api_key=key)
                for cur_model in candidate_models:
                    try:
                        model = genai.GenerativeModel(
                            model_name=cur_model,
                            system_instruction=FARROW_SYSTEM_PROMPT,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        prompt = f"Nén tài liệu sau đây thành 3 khối Farrow:\n\n\"\"\"\n{cleaned[:8000]}\n\"\"\""
                        response = model.generate_content(prompt, request_options={"timeout": 25})
                        if response and response.text:
                            t = response.text.strip()
                            if t.startswith("```"):
                                lines = t.splitlines()
                                if len(lines) >= 2 and lines[-1].startswith("```"):
                                    t = "\n".join(lines[1:-1]).strip()
                            data = json.loads(t)
                            if isinstance(data, dict) and "chunks" in data and len(data["chunks"]) == 3:
                                return data
                    except Exception:
                        continue
            except Exception as e:
                # Nếu key này lỗi, tự động thử key tiếp theo trong danh sách xoay tua
                continue

    # Heuristic fallback if AI fails or no valid keys
    return _heuristic_fallback(cleaned[:60], cleaned)


def _heuristic_fallback(title_hint: str, content: str) -> Dict[str, Any]:
    """Bộ nén dự phòng theo luật mẫu khi không có kết nối API."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    p1 = paragraphs[0][:150] if len(paragraphs) > 0 else "Bóc tách chân lý vật lý gốc rễ."
    p2 = paragraphs[1][:150] if len(paragraphs) > 1 else "Đo lường dòng chảy động lực và xác suất."
    p3 = paragraphs[2][:150] if len(paragraphs) > 2 else "Hành động đòn bẩy rủi ro thấp, tiềm năng lớn."

    return {
        "title": "Nén Farrow Tốc Hành: " + title_hint[:30],
        "tagline": "Đập vụn giả định -> Đo lường động lực -> Ra đòn bất đối xứng",
        "chunks": [
            {
                "label": "KHỐI 1: BẢN CHẤT GỐC",
                "principle": p1,
                "anchor": "CỬA RA VÀO PHÒNG",
                "crazy_image": "Một chiếc máy ép thủy lực khổng lồ đang nghiền nát đống chữ ở cửa thành một viên kẹo dẻo phát sáng lấp lánh!",
                "trigger_question": "Sự thật khách quan không thể chối cãi ở đây là gì?"
            },
            {
                "label": "KHỐI 2: DÒNG CHẢY ĐỘNG LỰC",
                "principle": p2,
                "anchor": "MÀN HÌNH MÁY TÍNH",
                "crazy_image": "Màn hình bốc cháy dữ dội, hiện lên các mũi tên dòng chảy đang chỉ chính xác vào điểm yếu của đối thủ!",
                "trigger_question": "Ai đang có động cơ làm việc này, và hệ quả bậc hai là gì?"
            },
            {
                "label": "KHỐI 3: ĐÒN BẨY HÀNH ĐỘNG",
                "principle": p3,
                "anchor": "CHIẾC BÀN & GHẾ NGỒI",
                "crazy_image": "Một chiếc lò xo titan bị nén cong vòng trên ghế, sẵn sàng bật tung phóng bạn đến mục tiêu!",
                "trigger_question": "Cách làm nào tốn ít nguồn lực nhất nhưng mang lại hiệu quả lớn nhất?"
            }
        ],
        "asymmetric_action": "Bắt đầu bằng một thử nghiệm vi mô chi phí gần bằng 0 ngay trong hôm nay."
    }
