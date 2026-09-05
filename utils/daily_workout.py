# -*- coding: utf-8 -*-
"""
Module Elite Daily Workout (15 Phút Rèn Luyện Hằng Ngày & Chuỗi Streak).
Xây dựng phản xạ nhận thức vô thức thông qua bài toán thực chiến mỗi ngày:
- Quy trình 3 bước: Bóc tách Sự thật vs Ý kiến -> Chiếu lăng kính hạt nhân -> Hành động bất đối xứng
- Ngân hàng 54 tình huống tinh hoa phân bổ rạch ròi 3 nhóm: Đa lĩnh vực (18), Học sinh K12 Wellspring (18), Chuyên sâu Người lớn (18)
- Quản lý chuỗi ngày rèn luyện liên tục (Streak)
- Chấm điểm và phản hồi từ AI Mentor
"""

from __future__ import annotations

import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union

import streamlit as st
import google.generativeai as genai

from utils.knowledge import load_user_history, save_user_history
from utils.ai_engine import (
    _normalize_keys,
    _mask_key,
    _is_quota_or_auth_error,
    clean_json_response,
)

# -----------------------------------------------------------------------------
# 1. NGÂN HÀNG BÀI TẬP WORKOUT MẪU TINH HOA (54 TÌNH HUỐNG THỰC CHIẾN ĐỘC LẬP)
# -----------------------------------------------------------------------------
DAILY_WORKOUT_BANK: List[Dict[str, Any]] = [
    # =========================================================================
    # NHÓM 1: ĐA LĨNH VỰC & MÔ HÌNH TINH HOA TỔNG HỢP (TRACK: "all") - 18 BÀI
    # =========================================================================
    {
        "id": "DW-GEN-01",
        "day_num": 1,
        "title": "Cơn Sốt Công Nghệ Mới & Tâm Lý Đám Đông (FOMO)",
        "track": "all",
        "scenario": (
            "Một công nghệ mới xuất hiện và giá trị của các công ty liên quan tăng 500% trong 3 tháng. "
            "Mọi diễn đàn, mạng xã hội và bạn bè xung quanh đều bàn tán, khoe lãi và giục bạn: 'Không tham gia ngay là bỏ lỡ cơ hội đổi đời duy nhất trong thập kỷ!'. "
            "Bạn cảm thấy bồn chồn, sợ mình bị tụt hậu nếu đứng ngoài."
        ),
        "guiding_principles": ["Tâm lý bầy đàn", "First Principles", "Mr. Market & Biên an toàn"],
        "step1_prompt": "Bóc tách cội rễ: Đâu là SỰ THẬT khách quan đo lường được, và đâu chỉ là Ý KIẾN/CẢM XÚC/DỰ BÁO?",
        "step2_prompt": "Chiếu lăng kính: Mô hình hạt nhân nào (Tâm lý học, Kinh tế học) đang chi phối hiện tượng này?",
        "step3_prompt": "Hành động bất đối xứng: Nước cờ tối ưu nào giúp bạn vừa không dính rủi ro hủy diệt, vừa tận dụng được cơ hội nếu nó thực sự bùng nổ?",
        "elite_hint": "Phân biệt giữa công nghệ thực sự có giá trị và giá tài sản bị thổi phồng. Chiến lược Quả tạ (Barbell): Đừng all-in, hãy quan sát nút thắt khan hiếm liền kề.",
    },
    {
        "id": "DW-GEN-02",
        "day_num": 2,
        "title": "Ra Quyết Định Trong Sương Mù & Cập Nhật Xác Suất Bayes",
        "track": "all",
        "scenario": (
            "Bạn chuẩn bị thi vào một chương trình tuyển chọn danh giá với tỷ lệ chọi 1/50 (2%). "
            "Bạn làm một bài thi thử và đạt điểm thuộc top 5%. Bạn bè bảo bạn 'chắc chắn 95% sẽ đỗ'. "
            "Bạn có nên chủ quan ngừng ôn luyện và ăn mừng sớm?"
        ),
        "guiding_principles": ["Xác suất Bayes", "Base Rate Fallacy (Bỏ quên tỷ lệ nền)", "Biên an toàn"],
        "step1_prompt": "Bóc tách: Tỷ lệ chọi chung (Base Rate) là bao nhiêu? Bài thi thử đo lường được mức độ nào so với kỳ thi thật?",
        "step2_prompt": "Chiếu lăng kính: Áp dụng công thức Bayes để nhận diện tại sao 'Top 5% thi thử' không đồng nghĩa với '95% đỗ thật'.",
        "step3_prompt": "Hành động: Chiến lược ôn tập và quản trị tâm lý để tối đa hóa xác suất thực tế.",
        "elite_hint": "Bẫy ảo tưởng xác suất: Khi tỷ lệ nền rất thấp, một tín hiệu tích cực chưa đủ để đảm bảo kết quả.",
    },
    {
        "id": "DW-GEN-03",
        "day_num": 3,
        "title": "Bẫy Hậu Quả Bậc Hai Trong Quản Lý Thời Gian & Năng Lượng",
        "track": "all",
        "scenario": (
            "Để hoàn thành khối lượng bài vở và công việc dồn ứ, bạn quyết định uống 3 lon nước tăng lực/cà phê đậm đặc mỗi ngày và chỉ ngủ 4 tiếng suốt 1 tuần. "
            "Kết quả Bậc 1: Bạn nộp bài đúng hạn và cảm thấy mình làm việc siêu năng suất. "
            "Nhưng điều gì đang âm thầm chờ bạn ở Bậc 2 và Bậc 3?"
        ),
        "guiding_principles": ["Tư duy Bậc hai", "Entropy sinh học", "Nợ kỹ thuật & Nợ sức khỏe"],
        "step1_prompt": "Bóc tách: Năng lượng bạn có được tuần này là do bạn tạo ra hay đang 'vay nặng lãi' từ tuần sau?",
        "step2_prompt": "Chiếu lăng kính: Hệ quả Bậc 2 (miễn dịch suy giảm, sương mù não) và Bậc 3 (mất 2 tuần kiệt sức, lỗi sai chí mạng) diễn ra thế nào?",
        "step3_prompt": "Hành động đòn bẩy: Tái thiết kế quy trình làm việc theo chu kỳ nhịp sinh học thay vì dùng chất kích thích cưỡng ép.",
        "elite_hint": "Giới tinh hoa tối ưu hóa năng lượng (Energy Management), không tối ưu hóa thời gian đơn thuần.",
    },
    {
        "id": "DW-GEN-04",
        "day_num": 4,
        "title": "Tư Duy Đảo Ngược: Lập Kế Hoạch Bằng Cách Tìm Đường Thất Bại Chắc Chắn",
        "track": "all",
        "scenario": (
            "Bạn chuẩn bị bước vào một dự án hoặc mục tiêu trọng đại kéo dài 6 tháng. "
            "Thay vì lập kế hoạch 'Làm sao để thành công rực rỡ', bạn được Charlie Munger thách thức: "
            "'Hãy chỉ ra 5 cách chắc chắn nhất sẽ biến dự án này thành thảm họa bẽ bàng!'."
        ),
        "guiding_principles": ["Tư duy Đảo ngược (Inversion)", "Quản trị rủi ro chủ động", "Tính phản dễ vỡ"],
        "step1_prompt": "Bóc tách: Liệt kê 3-5 hành vi hoặc sai lầm cụ thể đảm bảo 100% bạn sẽ thất bại thảm hại.",
        "step2_prompt": "Chiếu lăng kính: Tại sao con người rất dở trong việc tìm ra điều vĩ đại, nhưng lại rất giỏi nhận biết điều ngu ngốc?",
        "step3_prompt": "Hành động: Xây dựng danh sách 'Checklist những việc TUYỆT ĐỐI KHÔNG LÀM' trong 6 tháng tới.",
        "elite_hint": "'Invert, always invert' — Tránh được mọi hành vi ngu ngốc sẽ tự động đưa bạn vào top 5% xuất sắc.",
    },
    {
        "id": "DW-GEN-05",
        "day_num": 5,
        "title": "Khủng Hoảng Chi Phí Cơ Hội & Bẫy Ôm Đồ Đa Nhiệm (Multitasking)",
        "track": "all",
        "scenario": (
            "Bạn đang nhận 5 dự án cùng lúc: học thêm kỹ năng mới, tham gia 2 câu lạc bộ, nhận làm thêm ngoài giờ và tự học ngoại ngữ. "
            "Bạn liên tục chuyển đổi qua lại giữa các tác vụ, ngày nào cũng bận rộn 14 tiếng nhưng sau 3 tháng không có dự án nào đạt kết quả xuất sắc."
        ),
        "guiding_principles": ["Chi phí cơ hội", "Định luật Pareto 80/20", "Thuyết điểm thắt (Theory of Constraints)"],
        "step1_prompt": "Bóc tách: Chi phí ẩn của việc chuyển đổi ngữ cảnh (Context Switching) đang ngốn bao nhiêu % năng lượng thực sự của bạn?",
        "step2_prompt": "Chiếu lăng kính: Nguyên lý Pareto 80/20 và Điểm thắt nút cổ chai (Bottleneck) chỉ ra điều gì về sự phân tán này?",
        "step3_prompt": "Hành động bất đối xứng: Hãy áp dụng quy tắc Warren Buffett 5/25 để dũng cảm loại bỏ 4 mục tiêu thứ yếu và dồn lực cho 1 mục tiêu số 1.",
        "elite_hint": "Tập trung cực độ vào một nút thắt duy nhất tạo ra hiệu ứng domino đánh sập mọi khó khăn khác.",
    },
    {
        "id": "DW-GEN-06",
        "day_num": 6,
        "title": "Tính Phản Dễ Vỡ (Antifragility): Mạnh Lên Sau Mỗi Lần Biến Động",
        "track": "all",
        "scenario": (
            "Hệ thống công việc hoặc quy trình làm việc thường ngày của bạn bất ngờ sụp đổ vì một đối tác rút lui hoặc một công cụ phần mềm cốt lõi ngừng hoạt động. "
            "Một người bình thường sẽ hoảng loạn và tìm cách khôi phục lại trạng thái cũ. Nhưng Taleb khuyên bạn phải trở nên 'Phản dễ vỡ'."
        ),
        "guiding_principles": ["Antifragile", "Chiến lược Quả tạ (Barbell)", "Tùy chọn (Optionality)"],
        "step1_prompt": "Bóc tách: Điểm dễ vỡ cốt tử (Fragile Point) của hệ thống cũ nằm ở đâu? Tại sao nó không chịu được rung lắc?",
        "step2_prompt": "Chiếu lăng kính: Hệ thống 'Phản dễ vỡ' khác hệ thống 'Bền bỉ (Robust)' ở điểm nào khi đối mặt với căng thẳng?",
        "step3_prompt": "Hành động đòn bẩy: Tái thiết kế hệ sinh thái của bạn với các phương án dự phòng đa tầng và khả năng hưởng lợi từ sự xáo trộn.",
        "elite_hint": "Gió dập tắt ngọn nến nhưng thổi bùng ngọn lửa. Hãy biến các cú sốc thành chất xúc tác tiến hóa.",
    },
    {
        "id": "DW-GEN-07",
        "day_num": 7,
        "title": "Hiệu Ứng Dunning-Kruger: Nhận Diện Đỉnh Cao Của Sự Ngu Ngốc",
        "track": "all",
        "scenario": (
            "Sau khi đọc 2 cuốn sách và xem 5 video YouTube về một lĩnh vực hoàn toàn mới (ví dụ: Kinh tế vĩ mô, AI hay Đầu tư), "
            "bạn cảm thấy mình đã nắm trọn bản chất và tự tin đi tranh luận, dạy dỗ những người đã làm việc trong ngành 5 năm."
        ),
        "guiding_principles": ["Dunning-Kruger", "Vòng tròn năng lực (Circle of Competence)", "Khiêm tốn trí tuệ"],
        "step1_prompt": "Bóc tách: Kiến thức bạn thực sự sở hữu có thể giải quyết được bài toán thực tế nào, hay chỉ là thuật ngữ vay mượn?",
        "step2_prompt": "Chiếu lăng kính: Bạn đang đứng ở vị trí nào trên biểu đồ Dunning-Kruger (Đỉnh cao của sự thiếu hiểu biết vs Thung lũng thất vọng)?",
        "step3_prompt": "Hành động: Thiết kế một bài kiểm tra thực tế có thể falsify (bác bỏ) sự hiểu biết của bạn để hiệu chuẩn lại nhận thức.",
        "elite_hint": "Người thông thái thực sự luôn nhận thức rõ giới hạn của Vòng tròn năng lực và ranh giới mình không biết.",
    },
    {
        "id": "DW-GEN-08",
        "day_num": 8,
        "title": "Ma Trận Tù Nhân (Prisoner's Dilemma) Trong Hợp Tác Lâu Dài",
        "track": "all",
        "scenario": (
            "Bạn và một đối tác đang cùng triển khai một dự án chia đôi lợi nhuận. "
            "Nếu cả hai cùng dốc sức (Hợp tác), mỗi bên nhận 100 triệu. Nếu bạn lười biếng mà đối tác làm hết (Phản bội), bạn nhận 80 triệu mà không tốn công. "
            "Nếu cả hai cùng tính toán lười biếng, dự án phá sản và mỗi bên mất 20 triệu."
        ),
        "guiding_principles": ["Lý thuyết trò chơi", "Cân bằng Nash", "Chiến lược Tit-for-Tat"],
        "step1_prompt": "Bóc tách: Cấu trúc động lực (Incentive Structure) hiện tại đang khuyến khích hành vi đạo đức hay hành vi tư lợi ngắn hạn?",
        "step2_prompt": "Chiếu lăng kính: Tại sao trò chơi một lần (One-shot Game) dẫn tới kết cục thảm họa, nhưng trò chơi lặp lại vô hạn (Iterated Game) lại kích hoạt hợp tác?",
        "step3_prompt": "Hành động: Thiết lập cơ chế giám sát minh bạch và nguyên tắc Tit-for-Tat (Tử tế ban đầu - Phản ứng ngay nếu bị chơi xấu - Sẵn sàng tha thứ).",
        "elite_hint": "Biến trò chơi ngắn hạn thành trò chơi dài hạn có bóng ma của tương lai (Shadow of the future) phủ bóng lên hiện tại.",
    },
    {
        "id": "DW-GEN-09",
        "day_num": 9,
        "title": "Phân Biệt Tín Hiệu (Signal) Khỏi Tạp Âm (Noise) Thời Kỷ Nguyên Số",
        "track": "all",
        "scenario": (
            "Mỗi ngày bạn tiếp nhận hàng trăm tin tức giật gân, thông báo mạng xã hội, các bài phân tích đa chiều và tin đồn hậu trường. "
            "Bạn luôn cảm thấy mệt mỏi, căng thẳng và không biết tin nào là yếu tố quyết định thay đổi cuộc chơi, tin nào chỉ là tiếng ồn rác rưởi."
        ),
        "guiding_principles": ["Signal vs Noise (Nate Silver)", "Bộ lọc Lindy", "Chi phí biên nhận thức"],
        "step1_prompt": "Bóc tách: Trong 20 thông tin bạn đọc hôm qua, có bao nhiêu thông tin còn giá trị sau 1 năm nữa?",
        "step2_prompt": "Chiếu lăng kính: Hiệu ứng Lindy (Thời gian kiểm chứng chân lý) và Quy luật bảo toàn năng lượng nhận thức vận hành ra sao?",
        "step3_prompt": "Hành động: Thiết lập bộ lọc thông tin cấp cao (Cai nghiện tin tức giật gân, chỉ đọc sách kinh điển và dữ liệu thô gốc).",
        "elite_hint": "Tạp âm biến động liên tục hàng giờ nhưng triệt tiêu lẫn nhau; Tín hiệu âm thầm tích lũy nhưng định hình tương lai.",
    },
    {
        "id": "DW-GEN-10",
        "day_num": 10,
        "title": "Chiếc Dao Cạo Ockham (Occam's Razor) & Bẫy Phức Tạp Hóa Vấn Đề",
        "track": "all",
        "scenario": (
            "Một sự cố xảy ra trong tổ chức của bạn. Một số thành viên đưa ra giả thuyết ly kỳ về âm mưu ngầm, đối thủ cài cắm gián điệp, "
            "trong khi thực tế có thể chỉ đơn giản là một nhân viên gõ nhầm một dòng cấu hình vì thiếu ngủ."
        ),
        "guiding_principles": ["Occam's Razor", "Hanlon's Razor", "Tiết kiệm giả định (Parsimony)"],
        "step1_prompt": "Bóc tách: Giả thuyết nào đòi hỏi ít giả định chưa được chứng minh nhất?",
        "step2_prompt": "Chiếu lăng kính: Tại sao tâm lý con người có xu hướng thích những câu chuyện âm mưu phức tạp hơn sự thật giản đơn tẻ nhạt?",
        "step3_prompt": "Hành động: Áp dụng Chiếc dao cạo Ockham để cắt bỏ mọi suy diễn rườm rà và xử lý đúng mắt xích cốt lõi.",
        "elite_hint": "Giữa hai lời giải thích cùng giải quyết được hiện tượng, lời giải thích đơn giản hơn thường là lời giải thích chính xác.",
    },
    {
        "id": "DW-GEN-11",
        "day_num": 11,
        "title": "Bẫy Gán Nhãn Động Cơ Ác Ý (Hanlon's Razor) Trong Giao Tiếp",
        "track": "all",
        "scenario": (
            "Một người đồng nghiệp hoặc đối tác quên gửi tài liệu quan trọng cho bạn trước cuộc họp, khiến bạn bị bất ngờ trước tập thể. "
            "Phản xạ đầu tiên của bạn là tức giận và nghĩ: 'Hắn cố tình muốn hạ bệ uy tín của mình trước mặt mọi người!'. Bạn chuẩn bị phản công."
        ),
        "guiding_principles": ["Hanlon's Razor", "Thiên kiến quy kết cơ bản (Fundamental Attribution Error)", "Trí tuệ cảm xúc"],
        "step1_prompt": "Bóc tách: Có bằng chứng khách quan nào chứng minh đối phương có ác ý, hay họ chỉ đơn thuần đãng trí/quá tải?",
        "step2_prompt": "Chiếu lăng kính: Hanlon's Razor ('Đừng bao giờ quy cho ác ý những gì có thể giải thích thỏa đáng bằng sự bất cẩn') bảo vệ bạn ra sao?",
        "step3_prompt": "Hành động: Cách tiếp cận khách quan, xây dựng để làm rõ tình huống mà không tự tạo thêm kẻ thù không cần thiết.",
        "elite_hint": "Giới tinh hoa không lãng phí năng lượng vào việc suy diễn động cơ xấu; họ giải quyết vấn đề bằng quy trình và giao tiếp thẳng thắn.",
    },
    {
        "id": "DW-GEN-12",
        "day_num": 12,
        "title": "Định Luật Goodhart: Khi Thước Đo Biến Thành Mục Tiêu Bị Bóp Méo",
        "track": "all",
        "scenario": (
            "Một tổ chức đặt chỉ tiêu: Đánh giá năng lực lập trình viên bằng 'Số dòng code viết ra mỗi ngày' hoặc đánh giá bác sĩ bằng 'Số bệnh nhân khám trong 1 giờ'. "
            "Chỉ sau 2 tháng, số lượng dòng code tăng gấp 5 lần và số bệnh nhân khám tăng vọt, nhưng chất lượng sản phẩm và sự hài lòng tụt dốc thảm hại."
        ),
        "guiding_principles": ["Định luật Goodhart", "Hiệu ứng Rắn hổ mang (Cobra Effect)", "Động lực méo mó"],
        "step1_prompt": "Bóc tách: Thước đo ban đầu nhằm đại diện cho giá trị gì? Người tham gia đã 'hack' thước đo đó như thế nào?",
        "step2_prompt": "Chiếu lăng kính: Định luật Goodhart ('Khi một thước đo trở thành mục tiêu, nó không còn là một thước đo tốt nữa') vận hành ra sao?",
        "step3_prompt": "Hành động: Thiết kế hệ thống đánh giá đa chiều (Ghép cặp thước đo Số lượng với thước đo Chất lượng/Hệ quả lâu dài).",
        "elite_hint": "Bất kỳ chỉ số đo lường đơn lẻ nào cũng sẽ bị hành vi con người bẻ cong để tối ưu hóa cục bộ.",
    },
    {
        "id": "DW-GEN-13",
        "day_num": 13,
        "title": "Tư Duy Vòng Phản Hồi Âm & Dương (Feedback Loops)",
        "track": "all",
        "scenario": (
            "Một công ty mới ra mắt sản phẩm: Càng nhiều người dùng tham gia thì sản phẩm càng có giá trị, càng thu hút thêm người mới (Vòng lặp dương). "
            "Tuy nhiên, lượng người dùng quá tải khiến máy chủ sập và trải nghiệm khách hàng tệ hại, bắt đầu kích hoạt làn sóng rời bỏ (Vòng lặp âm)."
        ),
        "guiding_principles": ["Feedback Loops (Hệ thống học)", "Hiệu ứng tuyết lăn", "Điểm cân bằng động"],
        "step1_prompt": "Bóc tách: Đâu là các yếu tố khuếch đại (Reinforcing Loop) và đâu là các yếu tố kìm hãm tự cân bằng (Balancing Loop)?",
        "step2_prompt": "Chiếu lăng kính: Làm thế nào để một hệ thống duy trì được sự tăng trưởng mà không tự bóp nghẹt chính mình?",
        "step3_prompt": "Hành động: Xác định độ trễ thời gian (Time Delay) trong vòng phản hồi để đưa ra can thiệp trước khi khủng hoảng bùng phát.",
        "elite_hint": "Mọi tăng trưởng theo hàm mũ trong thế giới vật lý đều sẽ chạm vào rào cản cân bằng âm. Nhận diện điểm uốn trước khi nó xảy ra.",
    },
    {
        "id": "DW-GEN-14",
        "day_num": 14,
        "title": "Bi Kịch Của Tài Sản Chung (Tragedy of the Commons)",
        "track": "all",
        "scenario": (
            "Trong một nhóm làm việc chung hoặc một cộng đồng mạng xã hội mở, một tài nguyên chung (ví dụ: kho tài liệu mở, không gian thảo luận) "
            "bị một số thành viên khai thác vô tội vạ để spam quảng cáo hoặc tải về bán kiếm lời riêng mà không ai đóng góp ngược lại. Tài nguyên dần suy tàn."
        ),
        "guiding_principles": ["Tragedy of the Commons", "Quyền sở hữu (Property Rights)", "Thiết chế Elinor Ostrom"],
        "step1_prompt": "Bóc tách: Tại sao hành vi tối ưu cho từng cá nhân riêng lẻ lại dẫn đến sự hủy diệt cho toàn thể tập thể?",
        "step2_prompt": "Chiếu lăng kính: Các giải pháp kinh điển (Tư nhân hóa, Luật lệ cưỡng chế, hay Quy tắc cộng đồng tự quản của Elinor Ostrom)?",
        "step3_prompt": "Hành động: Thiết lập cơ chế luật chơi rõ ràng với chi phí vi phạm cao hơn nhiều so với lợi ích đánh cắp.",
        "elite_hint": "Không thể trông đợi vào lòng vị tha vô điều kiện; thể chế bền vững phải làm cho hành vi bảo vệ tài sản chung đồng thuận với lợi ích cá nhân.",
    },
    {
        "id": "DW-GEN-15",
        "day_num": 15,
        "title": "Phân Phối Lũy Thừa (Power Law) vs Phân Phối Chuẩn (Gaussian)",
        "track": "all",
        "scenario": (
            "Bạn quản lý một danh mục gồm 20 bài viết, 20 sản phẩm hoặc 20 mối quan hệ. "
            "Bạn chia đều 5% thời gian và năng lượng cho từng mục với niềm tin rằng 'mọi thứ đều quan trọng như nhau' theo tư duy phân phối chuẩn."
        ),
        "guiding_principles": ["Power Law", "Nguyên lý Pareto 80/20", "Bất đối xứng lợi nhuận"],
        "step1_prompt": "Bóc tách: Trong thực tế thế giới tri thức và kinh doanh, 1-2 yếu tố top đầu thường chiếm bao nhiêu % tổng tác động?",
        "step2_prompt": "Chiếu lăng kính: Sự khác biệt bản chất giữa Thế giới Mediocristan (Chiều cao, cân nặng) vs Extremistan (Của cải, tác động công nghệ)?",
        "step3_prompt": "Hành động: Tái phân bổ 80% nguồn lực tinh hoa nhất của bạn vào 20% hạt nhân tạo ra kết quả lũy thừa.",
        "elite_hint": "Thế giới hiện đại bị thống trị bởi phân phối lũy thừa. Người bình thường cào bằng; người tinh hoa tìm kiếm biến số lũy thừa.",
    },
    {
        "id": "DW-GEN-16",
        "day_num": 16,
        "title": "Vòng Tròn Năng Lực (Circle of Competence): Sức Mạnh Của Việc Nói 'Tôi Không Biết'",
        "track": "all",
        "scenario": (
            "Bạn là một chuyên gia rất giỏi trong ngành của mình. Một người bạn thân rủ bạn góp vốn vào một chuỗi nhà hàng ẩm thực với cam kết lợi nhuận 30%/năm. "
            "Họ khen bạn thông minh và nói: 'Người giỏi như bạn làm cái gì mà chẳng thành công!'. Bạn cảm thấy hãnh diện và muốn thử sức."
        ),
        "guiding_principles": ["Circle of Competence", "Ảo tưởng chuyển di năng lực", "Biên an toàn"],
        "step1_prompt": "Bóc tách: Lợi thế cạnh tranh vượt trội thực sự của bạn nằm ở đâu? Bạn có hiểu sâu về vận hành F&B bằng đối thủ trong ngành không?",
        "step2_prompt": "Chiếu lăng kính: Bẫy tự phụ khi thành công ở lĩnh vực A khiến con người ảo tưởng mình cũng am tường lĩnh vực B.",
        "step3_prompt": "Hành động: Quy tắc ứng xử khi đứng trước cơ hội nằm ngoài Vòng tròn năng lực (Học hỏi nghiêm túc hoặc từ chối dứt khoát).",
        "elite_hint": "Độ lớn của vòng tròn năng lực không quan trọng bằng việc bạn biết chính xác đường biên giới hạn của nó ở đâu.",
    },
    {
        "id": "DW-GEN-17",
        "day_num": 17,
        "title": "Bẫy Thiên Kiến Xác Nhận (Confirmation Bias) & Thí Nghiệm Falsification",
        "track": "all",
        "scenario": (
            "Bạn vừa nảy ra một ý tưởng dự án mà bạn vô cùng tâm đắc. Khi lên mạng tìm kiếm tài liệu, bạn chỉ bấm đọc các bài viết khen ngợi ý tưởng đó "
            "và lập tức bỏ qua hoặc chỉ trích các bài phân tích rủi ro thất bại. Bạn tin chắc ý tưởng của mình là hoàn hảo 100%.",
        ),
        "guiding_principles": ["Confirmation Bias", "Karl Popper Falsification", "Phản biện tích cực (Devil's Advocate)"],
        "step1_prompt": "Bóc tách: Bạn đang tìm kiếm CHÂN LÝ khách quan hay chỉ đang tìm kiếm sự XÁC NHẬN cho cảm xúc yêu thích của mình?",
        "step2_prompt": "Chiếu lăng kính: Nguyên lý Khả bác của Karl Popper ('Một lý thuyết chỉ khoa học khi nó chỉ rõ điều kiện nào sẽ chứng minh nó sai') áp dụng thế nào?",
        "step3_prompt": "Hành động: Tự đóng vai 'Luật sư của quỷ' (Devil's Advocate) để tìm ra 3 lỗ hổng chí mạng nhất của dự án trước khi dốc vốn.",
        "elite_hint": "Người tầm thường tìm bằng chứng để chứng minh mình đúng; bậc thầy tìm kiếm bằng chứng để chứng minh mình sai càng sớm càng tốt.",
    },
    {
        "id": "DW-GEN-18",
        "day_num": 18,
        "title": "Nguyên Lý Chi Phí Biên Tiến Về 0 (Zero Marginal Cost) Thời Kỷ Nguyên AI",
        "track": "all",
        "scenario": (
            "Bạn đang cung cấp một dịch vụ tư vấn cá nhân: Mỗi khách hàng mới đòi hỏi bạn phải bỏ thêm 2 giờ làm việc trực tiếp. "
            "Thu nhập của bạn tăng lên nhưng bạn hoàn toàn kiệt sức vì thời gian sinh học bị kịch trần. Trong khi đó, một đối thủ đóng gói tri thức thành AI Agent phục vụ 10.000 người cùng lúc."
        ),
        "guiding_principles": ["Zero Marginal Cost", "Đòn bẩy Permissionless", "Tự do hóa tài chính cá nhân"],
        "step1_prompt": "Bóc tách: Chi phí biên (Marginal Cost) để bạn phục vụ thêm khách hàng thứ 101 là bao nhiêu so với đối thủ dùng AI?",
        "step2_prompt": "Chiếu lăng kính: Sự chuyển dịch từ mô hình Lao động tuyến tính sang mô hình Sở hữu tài sản trí tuệ và Đòn bẩy công nghệ.",
        "step3_prompt": "Hành động: Thiết kế một quy trình chuyển hóa 30% kiến thức chuyên môn của bạn thành công cụ số có chi phí nhân bản bằng 0.",
        "elite_hint": "Nếu bạn kiếm tiền bằng cách bán thời gian, bạn sẽ không bao giờ đạt được tự do đích thực. Hãy xây dựng sản phẩm làm việc thay bạn khi bạn ngủ.",
    },

    # =========================================================================
    # NHÓM 2: HỌC SINH K12 WELLSPRING (TRACK: "k12") - 18 BÀI THỰC CHIẾN
    # =========================================================================
    {
        "id": "DW-K12-01",
        "day_num": 1,
        "title": "Áp Lực Đồng Trang Lứa & Dự Án Bài Tập Nhóm STEM Wellspring",
        "track": "k12",
        "scenario": (
            "Trong một dự án STEM Wellspring gồm 4 học sinh, bạn được bầu làm nhóm trưởng. "
            "Có 2 bạn liên tục trễ hạn, nộp bài sơ sài do dùng AI xào xáo vô tội vạ và bảo: 'Thầy cô chỉ chấm hình thức thôi, làm kỹ làm gì cho mệt'. "
            "Hạn nộp còn 48 tiếng. Nếu bạn gánh hết thì kiệt sức, nếu để mặc thì cả nhóm bị điểm liệt."
        ),
        "guiding_principles": ["Lý thuyết trò chơi", "Cơ chế minh bạch đóng góp (Attribution)", "Chi phí cơ hội"],
        "step1_prompt": "Bóc tách cội rễ: Tách riêng hành vi thực tế đo lường được của 2 bạn khỏi cảm xúc thất vọng, bực bội của bạn.",
        "step2_prompt": "Chiếu lăng kính: Tại sao cơ chế làm việc nhóm hiện tại lại dung dưỡng bẫy 'Kẻ ăn không' (Free-rider)?",
        "step3_prompt": "Hành động đòn bẩy: Thiết lập ngay bảng phân công nhiệm vụ vi mô có gắn tên cá nhân và báo cáo tiến độ minh bạch cho giáo viên.",
        "elite_hint": "Đừng dùng lời trách móc đạo đức; hãy dùng quy trình minh bạch phần đóng góp công khai (Public attribution).",
    },
    {
        "id": "DW-K12-02",
        "day_num": 2,
        "title": "Ma Trận Quản Lý Thời Gian: Ôn Thi Cuối Kỳ vs Bẫy Lướt TikTok/Shorts",
        "track": "k12",
        "scenario": (
            "Chỉ còn 5 ngày nữa là bước vào kỳ thi học kỳ quan trọng tại trường. Bạn mở điện thoại lên định tra một công thức Toán, "
            "nhưng thuật toán đề xuất một video hài hước. Bạn tự nhủ 'chỉ xem 5 phút giải trí', và khi giật mình nhìn đồng hồ thì đã trôi qua 2 tiếng đồng hồ. Bạn cảm thấy tội lỗi sâu sắc."
        ),
        "guiding_principles": ["Vòng lặp Dopamine rẻ tiền", "Hệ quả bậc hai", "Thiết kế rào cản môi trường"],
        "step1_prompt": "Bóc tách: Cảm xúc thỏa mãn nhất thời (Bậc 1) đánh đổi bằng điều gì ở Bậc 2 (Điểm số, sự tự tin, giấc ngủ)?",
        "step2_prompt": "Chiếu lăng kính: Não bộ bị bẫy bởi Dopamine phần thưởng ngẫu nhiên (Variable Rewards) của mạng xã hội như thế nào?",
        "step3_prompt": "Hành động đòn bẩy: Tạo rào cản vật lý (Để điện thoại ở phòng khác, dùng chế độ Focus) thay vì chỉ dựa vào ý chí đơn thuần.",
        "elite_hint": "Ý chí là nguồn lực hữu hạn sẽ cạn kiệt vào buổi tối. Kẻ thông minh quản trị môi trường xung quanh, không chiến đấu tay đôi với cám dỗ.",
    },
    {
        "id": "DW-K12-03",
        "day_num": 3,
        "title": "Chọn Lớp / Khối Thi Chuyển Cấp Lớp 10: Kỳ Vọng Cha Mẹ vs Sở Trường Cốt Lõi",
        "track": "k12",
        "scenario": (
            "Gia đình muốn bạn chọn khối Tự nhiên / Song bằng để sau này học ngành Tài chính hoặc Y khoa vì 'ổn định và danh giá'. "
            "Tuy nhiên, thế mạnh vượt trội và đam mê thực sự của bạn lại là Thiết kế công nghệ, Xã hội và Tranh biện. "
            "Bạn sợ làm cha mẹ thất vọng nhưng cũng sợ chôn vùi 3 năm cấp 3 trong áp lực chán nản."
        ),
        "guiding_principles": ["First Principles", "Vòng tròn năng lực", "Kỹ năng đàm phán dựa trên dữ liệu"],
        "step1_prompt": "Bóc tách: Đâu là nỗi sợ thực sự của cha mẹ (Sợ bạn không nuôi nổi bản thân, sợ mất mặt) và đâu là năng lực cốt lõi đã được chứng minh của bạn?",
        "step2_prompt": "Chiếu lăng kính: Phân tích quy luật thành công dựa trên Vòng tròn năng lực so với việc chạy theo đám đông ở lĩnh vực mình không có thế mạnh.",
        "step3_prompt": "Hành động: Xây dựng bản đề án cá nhân 3 năm với lộ trình mục tiêu, giải thưởng và minh chứng cụ thể để thuyết phục phụ huynh.",
        "elite_hint": "Đừng tranh cãi bằng cảm xúc tuổi mới lớn; hãy thuyết phục bằng một bản kế hoạch hành động sắc bén và kết quả cụ thể.",
    },
    {
        "id": "DW-K12-04",
        "day_num": 4,
        "title": "Ứng Dụng AI / ChatGPT Làm Bài Tập: Công Cụ Trợ Lực Đòn Bẩy vs Bẫy Lười Não Bộ",
        "track": "k12",
        "scenario": (
            "Thầy cô giao một bài luận phân tích tác phẩm văn học hoặc hiện tượng lịch sử. "
            "Nhiều bạn trong lớp chỉ cần copy đề bài vào ChatGPT, sao chép kết quả nộp bài trong 30 giây và được 8 điểm. "
            "Bạn băn khoăn: Có nên làm như họ không? Nếu tự viết thì tốn 2 tiếng, nếu lạm dụng AI thì sau này đi thi trực tiếp sẽ ra sao?"
        ),
        "guiding_principles": ["Đòn bẩy nhận thức", "Entropy cơ bắp não bộ", "Hệ quả bậc hai"],
        "step1_prompt": "Bóc tách: Lợi ích trước mắt (Bậc 1: Tiết kiệm thời gian, điểm khá) vs Cái giá phải trả lâu dài (Bậc 2: Mất khả năng tư duy sâu, sụp đổ khi thi cử không có máy tính).",
        "step2_prompt": "Chiếu lăng kính: Phân biệt giữa 'Dùng AI làm hộ bài' (Bắt chước thụ động) vs 'Dùng AI làm đối tác phản biện Socratic' (Gia sư tư duy).",
        "step3_prompt": "Hành động đòn bẩy: Thiết kế quy trình 3 bước: Tự lập dàn ý First Principles -> Dùng AI tìm góc nhìn phản biện đối nghịch -> Tự tay viết bài hoàn chỉnh.",
        "elite_hint": "AI là bộ khuếch đại (Amplifier). Kẻ lười biếng dùng AI sẽ trở thành kẻ rỗng tuếch; người tinh hoa dùng AI để nhân bản sức mạnh tư duy độc bản.",
    },
    {
        "id": "DW-K12-05",
        "day_num": 5,
        "title": "Xung Đột Ý Kiến Dự Án Triển Lãm Khoa Học Giữa Hai Người Bạn Thân",
        "track": "k12",
        "scenario": (
            "Bạn và bạn thân cùng làm dự án tham gia Triển lãm Khoa học Wellspring. Bạn muốn tập trung làm sản phẩm phần cứng thực tế, "
            "còn bạn kia nhất quyết đòi làm mô hình ứng dụng phần mềm ảo. Hai bên cãi vã gay gắt và bắt đầu nói những lời làm tổn thương tình bạn."
        ),
        "guiding_principles": ["Tách con người khỏi vấn đề", "Tư duy Win-Win", "Mục tiêu tối thượng (Superordinate Goal)"],
        "step1_prompt": "Bóc tách: Vấn đề kỹ thuật cốt lõi của dự án là gì? Phần nào là cái tôi (Ego) muốn giành phần thắng trong cuộc tranh cãi?",
        "step2_prompt": "Chiếu lăng kính: Khái niệm 'Mục tiêu tối thượng' trong tâm lý học xã hội giúp giải quyết mâu thuẫn đồng đội như thế nào?",
        "step3_prompt": "Hành động: Đề xuất giải pháp tích hợp (ví dụ: Phần cứng IoT kết nối với Ứng dụng điều khiển) để cả hai cùng phát huy sở trường.",
        "elite_hint": "Bậc thầy giải quyết xung đột không chọn A hay B, mà tìm kiếm giải pháp C tích hợp cả hai ở tầm mức cao hơn.",
    },
    {
        "id": "DW-K12-06",
        "day_num": 6,
        "title": "Thất Bại Trong Kỳ Thi Đội Tuyển Học Sinh Giỏi / Học Bổng",
        "track": "k12",
        "scenario": (
            "Bạn đã dành trọn 3 tháng ôn luyện hết mình nhưng kết quả thi vừa công bố: bạn thiếu đúng 0.25 điểm để lọt vào đội tuyển chính thức. "
            "Bạn cảm thấy sụp đổ, xấu hổ với bạn bè và tự nhủ: 'Có lẽ mình vốn dĩ chẳng có tài năng gì cả'."
        ),
        "guiding_principles": ["Growth Mindset vs Fixed Mindset", "Tái cấu trúc nhận thức (Reframing)", "Tính phản dễ vỡ"],
        "step1_prompt": "Bóc tách: Khoảng cách 0.25 điểm đo lường điều gì (Một vài lỗi kỹ năng cụ thể) hay đo lường toàn bộ giá trị con người bạn?",
        "step2_prompt": "Chiếu lăng kính: Mô hình Tư duy Cố định (Fixed Mindset) đang đánh lừa bạn như thế nào khi coi thất bại là phán quyết chung cuộc?",
        "step3_prompt": "Hành động: Làm bản phân tích 'Khám nghiệm tử thi đề thi' (Post-mortem Analysis): Bóc tách chính xác 3 câu bị mất điểm và lên kế hoạch bù đắp lỗ hổng.",
        "elite_hint": "Thất bại chỉ là một điểm dữ liệu phản hồi (Feedback), không phải là định danh bản sắc (Identity) của bạn.",
    },
    {
        "id": "DW-K12-07",
        "day_num": 7,
        "title": "Bẫy Chi Phí Chìm: Theo Học Một Môn Năng Khiếu Không Còn Phù Hợp",
        "track": "k12",
        "scenario": (
            "Bạn đã theo học đàn Piano hoặc một môn thể thao suốt 4 năm qua vì sự định hướng ban đầu. "
            "Hiện tại bạn nhận thấy môn này không còn phục vụ cho mục tiêu phát triển tương lai và mỗi buổi học đều là một cực hình tinh thần. "
            "Nhưng bạn tiếc: 'Bỏ thì phí 4 năm công sức và tiền học phí của bố mẹ quá!'.",
        ),
        "guiding_principles": ["Chi phí chìm (Sunk Cost)", "Chi phí cơ hội", "Tư duy Đảo ngược"],
        "step1_prompt": "Bóc tách: Tiền bạc và 4 năm thời gian đã trôi qua có thể lấy lại được bằng cách cố học thêm 1 năm nữa không?",
        "step2_prompt": "Chiếu lăng kính: Mỗi giờ bạn tiếp tục ngồi bên cây đàn với sự chán chường đang cướp đi cơ hội phát triển kỹ năng nào khác?",
        "step3_prompt": "Hành động: Cách đối thoại chân thành với bố mẹ về việc kết thúc một chặng đường và chuyển hóa các bài học kỷ luật sang một đam mê mới.",
        "elite_hint": "Quá khứ đã là chi phí chìm = 0. Quyết định của ngày hôm nay chỉ nên dựa trên giá trị và chi phí biên của ngày mai.",
    },
    {
        "id": "DW-K12-08",
        "day_num": 8,
        "title": "Phương Pháp Học Lặp Lại Ngắt Quãng (Spaced Repetition) vs Nhồi Nhét 1 Đêm",
        "track": "k12",
        "scenario": (
            "Một người bạn trong lớp luôn đợi đến đêm trước ngày kiểm tra mới thức trắng đêm học vẹt 50 trang tài liệu. "
            "Hôm sau bạn ấy vẫn đạt 8.5 điểm và cười nhạo bạn: 'Học cả kỳ làm gì cho mệt, thức 1 đêm là xong!'. "
            "Tuy nhiên, 2 tuần sau khi làm bài thi tổng hợp, bạn ấy hoàn toàn quên sạch mọi kiến thức."
        ),
        "guiding_principles": ["Đường cong quên Ebbinghaus", "Lãi kép nhận thức", "Spaced Repetition"],
        "step1_prompt": "Bóc tách: Điểm số bài kiểm tra 15 phút đo lường trí nhớ ngắn hạn hay sự thấu hiểu sâu sắc kiến thức nền tảng?",
        "step2_prompt": "Chiếu lăng kính: Đường cong lãng quên của Ebbinghaus và cơ chế củng cố khớp thần kinh (Synaptic Consolidation) khi não ngủ nghỉ.",
        "step3_prompt": "Hành động: Xây dựng hệ thống học tập 15 phút mỗi ngày với Spaced Repetition để kiến thức đi vào tầng trí nhớ dài hạn vĩnh viễn.",
        "elite_hint": "Nhồi nhét là vay nóng trí nhớ với lãi suất cắt cổ; Spaced Repetition là gửi tiết kiệm nhận thức để hưởng lãi kép thần kỳ.",
    },
    {
        "id": "DW-K12-09",
        "day_num": 9,
        "title": "Thành Lập CLB Học Thuật / Dự Án Xã Hội Với Ngân Sách 0 Đồng",
        "track": "k12",
        "scenario": (
            "Bạn muốn thành lập một CLB Sách hoặc Dự án Dạy học cho trẻ em vùng cao nhưng nhà trường không có quỹ tài trợ. "
            "Nhiều bạn bè bảo: 'Không có tiền triệu thì làm sao tổ chức sự kiện hay truyền thông được, bỏ đi thôi!'.",
        ),
        "guiding_principles": ["Đòn bẩy không cần xin phép", "First Principles", "Lean Startup (Khởi nghiệp tinh gọn)"],
        "step1_prompt": "Bóc tách: Nhu cầu thực sự cốt lõi của một CLB là gì (Sự kết nối, tri thức chia sẻ) hay là hội trường sang trọng và băng rôn đắt tiền?",
        "step2_prompt": "Chiếu lăng kính: Sử dụng các công cụ đòn bẩy miễn phí thời đại số (Mạng xã hội, Google Workspace, Canva, Notion) để nhân bản giá trị.",
        "step3_prompt": "Hành động: Thiết kế một sự kiện thử nghiệm vi mô (MVP - Minimum Viable Project) với ngân sách 0đ phục vụ 15 thành viên đầu tiên trong 1 tuần.",
        "elite_hint": "Thiếu thốn nguồn lực không phải là rào cản, mà là chất xúc tác mạnh nhất kích hoạt sự sáng tạo đột phá.",
    },
    {
        "id": "DW-K12-10",
        "day_num": 10,
        "title": "Phân Biệt Tin Tức Thật Và Tin Đồn Thất Thiệt Trực Tuyến",
        "track": "k12",
        "scenario": (
            "Trên nhóm chat của khối, một bức ảnh chụp màn hình kèm tin đồn giật gân về việc 'Trường chuẩn bị đổi lịch thi và hủy toàn bộ kỳ nghỉ hè' "
            "khiến hàng trăm học sinh hoang mang, phẫn nộ và đồng loạt đăng bài phản đối trên mạng xã hội."
        ),
        "guiding_principles": ["Karl Popper Falsification", "Nguồn tin sơ cấp vs thứ cấp", "Tâm lý bầy đàn"],
        "step1_prompt": "Bóc tách: Đâu là nguồn tin gốc (Văn bản có dấu đỏ của Ban Giám hiệu hay chỉ là tin đồn chuyền miệng không rõ nguồn)?",
        "step2_prompt": "Chiếu lăng kính: Tại sao tin tức tiêu cực và giật gân luôn có tốc độ lan truyền nhanh gấp 6 lần sự thật (Khai thác hạch hạnh nhân Não bộ)?",
        "step3_prompt": "Hành động: Quy tắc 3 bước kiểm chứng trước khi chia sẻ: Tìm nguồn gốc -> Hỏi người có thẩm quyền -> Dừng lan truyền tin độc hại.",
        "elite_hint": "Người có tư duy phản biện tinh hoa là người biết giữ sự tĩnh lặng hoài nghi khi đám đông đang sôi sục vì một tin đồn chưa kiểm chứng.",
    },
    {
        "id": "DW-K12-11",
        "day_num": 11,
        "title": "Bẫy Tự Ti Khi Thấy Bạn Bè Khoe Thành Tích Trực Tuyến",
        "track": "k12",
        "scenario": (
            "Lướt Facebook/Instagram cuối tuần, bạn thấy bạn học cùng lớp đăng ảnh đạt IELTS 8.0, đi du lịch châu Âu và nhận giải thưởng quốc tế. "
            "Nhìn lại mình đang ngồi giải bài tập trong phòng ngủ chật hẹp, bạn cảm thấy mình thật tầm thường, kém cỏi và rơi vào trầm cảm."
        ),
        "guiding_principles": ["Selection Bias (Thiên kiến chọn lọc)", "Vòng tròn năng lực", "Trục thời gian riêng"],
        "step1_prompt": "Bóc tách: Mạng xã hội phản ánh bức tranh toàn diện cuộc đời một người hay chỉ là 'đoạn phim cắt cúp đẹp nhất' (Highlight Reel)?",
        "step2_prompt": "Chiếu lăng kính: Thiên kiến chọn lọc (Chỉ khoe điều tốt, giấu điều xấu) đang bóp méo nhận thức của bạn về thực tế như thế nào?",
        "step3_prompt": "Hành động: Chuyển đổi thước đo so sánh từ bên ngoài (So với người khác) sang bên trong (So với chính mình của ngày hôm qua).",
        "elite_hint": "Đừng so sánh hậu trường đầy mồ hôi của bạn với màn trình diễn lấp lánh trên sân khấu của người khác.",
    },
    {
        "id": "DW-K12-12",
        "day_num": 12,
        "title": "Đàm Phán Quyền Tự Chủ Thời Gian Với Cha Mẹ",
        "track": "k12",
        "scenario": (
            "Cha mẹ bạn kiểm soát rất gắt gao: Kiểm tra điện thoại mỗi tối, bắt học đúng giờ và không cho đi chơi cuối tuần với bạn bè. "
            "Bạn cảm thấy bị ngột ngạt và muốn phản kháng bằng cách đóng chặt cửa phòng hoặc to tiếng cãi lại."
        ),
        "guiding_principles": ["Lý thuyết trò chơi", "Xây dựng niềm tin thông qua dữ liệu", "Incentive Alignment"],
        "step1_prompt": "Bóc tách: Tại sao cha mẹ kiểm soát? Đâu là sự bất an cốt lõi của cha mẹ về sự an toàn và tương lai của bạn?",
        "step2_prompt": "Chiếu lăng kính: Niềm tin không được trao tặng miễn phí; niềm tin là tài sản được tích lũy từ các cam kết nhỏ hoàn thành đều đặn.",
        "step3_prompt": "Hành động: Đề xuất một thỏa thuận thử nghiệm 2 tuần: Bạn chủ động hoàn thành mọi mục tiêu điểm số và báo cáo minh bạch để đổi lấy 3 giờ tự do cuối tuần.",
        "elite_hint": "Tự do chỉ đến sau khi bạn chứng minh được năng lực tự chịu trách nhiệm. Hãy biến cha mẹ từ người giám sát thành đối tác đồng hành.",
    },
    {
        "id": "DW-K12-13",
        "day_num": 13,
        "title": "Chiến Lược Làm Bài Thi Trắc Nghiệm Chuẩn Hóa: Loại Trừ & Tỷ Lệ Nền",
        "track": "k12",
        "scenario": (
            "Trong phòng thi SAT/IELTS hoặc thi học kỳ, thời gian còn đúng 5 phút nhưng bạn còn 4 câu hỏi trắc nghiệm hóc búa chưa làm. "
            "Nhiều bạn chọn khoanh bừa một đáp án C cầu may. Liệu có chiến lược tư duy toán học nào tối ưu hơn?"
        ),
        "guiding_principles": ["Tư duy Xác suất", "Phương pháp loại trừ Bayes", "Biên an toàn"],
        "step1_prompt": "Bóc tách: Nếu khoanh bừa 4 đáp án, xác suất trúng là 25%. Nếu loại trừ được 2 phương án chắc chắn sai, xác suất tăng lên bao nhiêu?",
        "step2_prompt": "Chiếu lăng kính: Nhận diện bẫy ngữ nghĩa (Từ ngữ quá cực đoan như 'always', 'never') thường có tỷ lệ sai rất cao trong đề thi.",
        "step3_prompt": "Hành động: Quy trình 30 giây: Quét từ khóa cực đoan -> Triệt tiêu 2 phương án phi lý -> Đặt cược xác suất vào phương án có điều kiện biên hợp lý.",
        "elite_hint": "Khi không biết đáp án đúng, khả năng loại bỏ đáp án sai một cách có phương pháp chính là chiếc phao cứu sinh của người thông thái.",
    },
    {
        "id": "DW-K12-14",
        "day_num": 14,
        "title": "Quản Trị Năng Lượng Trước Vòng Chung Kết Tranh Biện (Debate)",
        "track": "k12",
        "scenario": (
            "Ngày mai là trận Chung kết cuộc thi Tranh biện Wellspring. Lúc 11 giờ đêm, bạn cảm thấy luận điểm của đội mình còn vài điểm yếu. "
            "Hai người bạn trong đội giục: 'Thức trắng đêm nay để tra cứu thêm tài liệu phản biện đi!'. Bạn đang đứng giữa hai lựa chọn."
        ),
        "guiding_principles": ["Biên an toàn nhận thức", "Entropy sinh học", "Tư duy Bậc hai"],
        "step1_prompt": "Bóc tách: Trong một trận tranh biện đỉnh cao, yếu tố nào quyết định chiến thắng: Thêm 1 mảnh tài liệu vụn vặt hay một bộ não minh mẫn phản xạ bén ngọt?",
        "step2_prompt": "Chiếu lăng kính: Hệ quả bậc 2 của việc thức trắng đêm: Mất khả năng lắng nghe tinh tế, nói năng lắp bắp và sập nguồn năng lượng vào buổi chiều.",
        "step3_prompt": "Hành động: Quyết định chốt khung tài liệu lúc 11h30, ngủ đủ 8 tiếng để bước vào sân khấu khấu với thần thái tự tin và năng lượng áp đảo.",
        "elite_hint": "Một khẩu súng tốt không có đạn thì vô dụng; một bộ não chất đầy kiến thức nhưng kiệt sức sẽ tự bắn vào chân mình.",
    },
    {
        "id": "DW-K12-15",
        "day_num": 15,
        "title": "Tư Duy Đảo Ngược: 5 Sai Lầm Chắc Chắn Khiến Hồ Sơ Du Học Bị Loại",
        "track": "k12",
        "scenario": (
            "Bạn chuẩn bị viết bài luận và xây dựng hồ sơ ứng tuyển học bổng du học Mỹ / Canada. "
            "Thay vì đọc hàng chục bài viết 'Bí kíp trúng tuyển Harvard', bạn quyết định mời Charlie Munger làm cố vấn đảo ngược.",
        ),
        "guiding_principles": ["Inversion (Tư duy Đảo ngược)", "Chống sáo rỗng (Authenticity)", "First Principles"],
        "step1_prompt": "Bóc tách: Liệt kê 3 chủ đề bài luận sáo rỗng nhất mà 90% học sinh viết (vd: Cố gắng thắng trận bóng rổ, đi từ thiện 1 ngày chụp ảnh sống ảo).",
        "step2_prompt": "Chiếu lăng kính: Giám khảo tuyển sinh đọc 5.000 bài luận mỗi mùa; điều gì khiến một bài luận trở nên giả tạo và đáng vứt vào sọt rác?",
        "step3_prompt": "Hành động: Viết danh sách 'Not-to-write' (Những điều cấm kỵ) và tìm kiếm một câu chuyện thật, độc bản thể hiện sự dễ bị tổn thương và bài học cá nhân.",
        "elite_hint": "Đừng cố trở thành người hoàn hảo mà mọi người muốn thấy; hãy trở thành một phiên bản chân thực, sâu sắc và độc nhất không thể sao chép.",
    },
    {
        "id": "DW-K12-16",
        "day_num": 16,
        "title": "Kỹ Thuật Feynman: Giảng Giải Khái Niệm Khó Cho Đứa Em Lớp 3 Hiểu",
        "track": "k12",
        "scenario": (
            "Bạn vừa học xong bài 'Định luật Vạn vật Hấp dẫn' hoặc 'Cơ chế Quang hợp' trong môn Khoa học. "
            "Bạn thuộc làu làu định nghĩa trong sách giáo khoa với đầy đủ thuật ngữ chuyên môn. "
            "Thử thách đặt ra: Hãy giải thích khái niệm này cho đứa em họ học lớp 3 hiểu trong 3 phút mà không dùng bất kỳ thuật ngữ khó nào."
        ),
        "guiding_principles": ["Kỹ thuật Feynman", "First Principles", "Nén nhận thức"],
        "step1_prompt": "Bóc tách: Thuật ngữ chuyên môn nào bạn đang dùng như một tấm bình phong để che giấu việc mình chưa thực sự hiểu bản chất?",
        "step2_prompt": "Chiếu lăng kính: Nếu bạn không thể giải thích điều gì một cách đơn giản, điều đó chứng minh bạn chưa hiểu nó đủ sâu.",
        "step3_prompt": "Hành động: Dùng một hình ảnh ẩn dụ đời thường (ví dụ: Tấm bạt lò xo bị quả bóng sắt đè lõm xuống) để giải thích sự uốn cong của không-thời gian.",
        "elite_hint": "Sự thông thái đỉnh cao thể hiện ở khả năng biến những điều phức tạp nhất thành sự giản dị trong sáng.",
    },
    {
        "id": "DW-K12-17",
        "day_num": 17,
        "title": "Bẫy Ngụy Biện Công Kích Cá Nhân (Ad Hominem) Khi Tranh Luận Học Đường",
        "track": "k12",
        "scenario": (
            "Trong một buổi thảo luận môn Lịch sử / Giáo dục công dân, một bạn đưa ra quan điểm trái ngược với bạn. "
            "Thay vì mổ xẻ luận cứ của bạn ấy, bạn hoặc một người khác buột miệng nói: 'Cậu học môn Toán còn lẹt đẹt thì hiểu gì về chính trị mà nói!'. Cả lớp cười ồ."
        ),
        "guiding_principles": ["Ngụy biện Ad Hominem", "Tách bạch Luận cứ vs Con người", "Chuẩn mực tranh luận trí tuệ"],
        "step1_prompt": "Bóc tách: Điểm số môn Toán của bạn kia có mối liên hệ logic tất yếu nào với tính đúng đắn của luận điểm Lịch sử bạn ấy đưa ra không?",
        "step2_prompt": "Chiếu lăng kính: Ngụy biện Ad Hominem hủy hoại môi trường học thuật và làm cùn mòn tư duy phản biện như thế nào?",
        "step3_prompt": "Hành động: Tái cấu trúc lại phản biện: Tôn trọng người nói và tập trung 100% vào việc bóc tách dữ liệu và giả định của luận cứ.",
        "elite_hint": "Tấn công con người là vũ khí của kẻ đuối lý; phân tích cấu trúc luận cứ là bản lĩnh của bậc trí giả.",
    },
    {
        "id": "DW-K12-18",
        "day_num": 18,
        "title": "Ma Trận Eisenhower & Định Luật Pareto 80/20 Lập Kế Hoạch Tuần",
        "track": "k12",
        "scenario": (
            "Mỗi đầu tuần bạn đều có một danh sách 25 việc cần làm: từ nộp bài tập, giặt quần áo, trả lời tin nhắn bạn bè, luyện đàn, đọc sách cho đến dọn phòng. "
            "Đến cuối tuần, bạn đã làm được 20 việc lặt vặt nhưng 2 việc quan trọng nhất quyết định tương lai học tập thì vẫn nguyên vẹn chưa đụng tới."
        ),
        "guiding_principles": ["Ma trận Eisenhower", "Định luật Pareto 80/20", "Bẫy bận rộn giả tạo"],
        "step1_prompt": "Bóc tách: Phân loại rạch ròi giữa việc 'Khẩn cấp' (Đòi hỏi phản ứng ngay) vs việc 'Quan trọng' (Xây dựng tương lai dài hạn).",
        "step2_prompt": "Chiếu lăng kính: Tại sao não bộ luôn thích làm những việc nhỏ nhặt dễ dàng để tạo cảm giác 'ảo tưởng năng suất'?",
        "step3_prompt": "Hành động: Áp dụng nguyên tắc 'Nuốt con ếch' (Eat that Frog): Luôn hoàn thành việc Quan trọng nhưng Không khẩn cấp nhất vào đầu mỗi ngày.",
        "elite_hint": "Bận rộn không đồng nghĩa với hiệu quả. Đừng nhầm lẫn giữa chuyển động hỗn loạn và sự tiến bộ thực chất.",
    },

    # =========================================================================
    # NHÓM 3: CHUYÊN SÂU NGƯỜI LỚN & CHUYÊN GIA (TRACK: "adult") - 18 BÀI
    # =========================================================================
    {
        "id": "DW-ADULT-01",
        "day_num": 1,
        "title": "Bẫy Chi Phí Chìm (Sunk Cost) Trong Dự Án Kinh Doanh / Đầu Tư Lỗ Triền Miên",
        "track": "adult",
        "scenario": (
            "Bạn đã dành 2 năm và 500 triệu đồng để theo đuổi một dự án kinh doanh. "
            "Hiện tại, số liệu thực tế cho thấy nhu cầu thị trường đã thay đổi hoàn toàn và mỗi tháng dự án tiếp tục đốt thêm 25 triệu. "
            "Tuy nhiên, bạn cảm thấy: 'Nếu dừng lại bây giờ thì toàn bộ công sức và tiền bạc 2 năm qua coi như mất trắng!'. Bạn định vay thêm 200 triệu để cầm cự."
        ),
        "guiding_principles": ["Chi phí chìm (Sunk Cost)", "Tư duy Đảo ngược (Inversion)", "Chi phí cơ hội"],
        "step1_prompt": "Bóc tách: Tiền và thời gian 2 năm qua có lấy lại được bằng cách cố thêm không? Hiện tại thực tế có gì?",
        "step2_prompt": "Chiếu lăng kính: Mô hình Chi phí chìm và Bẫy thiên kiến xác nhận đang đánh lừa não bộ của bạn như thế nào?",
        "step3_prompt": "Hành động dứt khoát: Hãy đóng vai một nhà đầu tư mới tiếp quản dự án hôm nay, bạn sẽ quyết định ra sao?",
        "elite_hint": "Quyết định tương lai chỉ phụ thuộc vào chi phí và lợi ích biên từ ngày mai trở đi. Quá khứ đã là sunk cost = 0.",
    },
    {
        "id": "DW-ADULT-02",
        "day_num": 2,
        "title": "Bắt Đáy CKVN Khi Vĩ Mô Biến Động Khủng Hoảng: Biên An Toàn vs Rơi Dao Lam",
        "track": "adult",
        "scenario": (
            "Thị trường chứng khoán Việt Nam (VN-Index) giảm 200 điểm sau các tin tức bắt bớ lãnh đạo và siết tín dụng trái phiếu. "
            "Một cổ phiếu đầu ngành giảm 60% từ đỉnh, P/E về mức thấp lịch sử trong 10 năm. Diễn đàn tràn ngập tiếng khóc than và kêu gọi tháo chạy. "
            "Bạn cầm tiền mặt và băn khoăn: Liệu đây là món hời thế kỷ hay là chiếc dao lam đang rơi?"
        ),
        "guiding_principles": ["Biên an toàn (Margin of Safety)", "Mr. Market (Benjamin Graham)", "Khả năng thanh toán (Solvency)"],
        "step1_prompt": "Bóc tách: Đâu là nỗi hoảng loạn tâm lý của đám đông ngắn hạn và đâu là giá trị tài sản ròng/dòng tiền thực chất của doanh nghiệp?",
        "step2_prompt": "Chiếu lăng kính: Mô hình 'Mr. Market' của Benjamin Graham và phép thử thanh khoản: Doanh nghiệp có nguy cơ phá sản vì nợ vay ngắn hạn không?",
        "step3_prompt": "Hành động: Chiến lược giải ngân từng phần theo tỷ lệ phân bổ kim tự tháp đảo ngược, tuyệt đối không dùng margin khi thị trường chưa tạo đáy.",
        "elite_hint": "Hãy tham lam khi người khác sợ hãi, nhưng chỉ tham lam với doanh nghiệp có bảng cân đối kế toán bằng pháo đài thép.",
    },
    {
        "id": "DW-ADULT-03",
        "day_num": 3,
        "title": "Bẫy Trả Thù Thị Trường (Revenge Trading) Sau Chuỗi Thua Lỗ Liên Tiếp",
        "track": "adult",
        "scenario": (
            "Trong phiên giao dịch Vàng (XAU/USD) phiên Mỹ biến động mạnh, bạn vừa dính 3 lệnh cắt lỗ liên tiếp mất 2.000 USD. "
            "Tim bạn đập nhanh, mặt nóng bừng và cảm giác căm phẫn dâng trào: 'Thị trường đang cố tình săn stoploss của mình!'. "
            "Bạn chuẩn bị bấm vào một lệnh mới với khối lượng gấp 3 lần bình thường (All-in) để gỡ gạc ngay trong đêm."
        ),
        "guiding_principles": ["Cơn giận vô thức (Tilt)", "Hệ thống 1 & Hệ thống 2 (Kahneman)", "Rủi ro phá sản (Gambler's Ruin)"],
        "step1_prompt": "Bóc tách: Thị trường có biết bạn là ai và có 'thù oán cá nhân' với bạn không? Trạng thái sinh học của bạn lúc này có đủ tỉnh táo để tính toán xác suất không?",
        "step2_prompt": "Chiếu lăng kính: Cơn say Dopamine và phản ứng chiến-hay-biến của hạch hạnh nhân đã đánh cắp quyền kiểm soát của thùy trán trước ra sao?",
        "step3_prompt": "Hành động: Quy tắc bàn tay sắt: Đóng toàn bộ ứng dụng biểu đồ, rời khỏi bàn làm việc ít nhất 12 tiếng và chấp nhận khoản lỗ như chi phí vận hành bình thường.",
        "elite_hint": "Khoản lỗ đầu tiên là khoản lỗ rẻ nhất. Revenge trading là chiếc xẻng nhanh nhất giúp một trader tự đào mồ chôn tài khoản của mình.",
    },
    {
        "id": "DW-ADULT-04",
        "day_num": 4,
        "title": "Thiết Kế Cơ Chế Thưởng Doanh Nghiệp Tránh Bẫy Hiệu Ứng Rắn Hổ Mang",
        "track": "adult",
        "scenario": (
            "Để giải quyết vấn đề khách hàng phàn nàn, giám đốc một công ty công bố chính sách: "
            "'Thưởng 100.000đ cho nhân viên chăm sóc khách hàng với mỗi khiếu nại được đóng lại thành công trong ngày'. "
            "Sau 1 tháng, số lượng cuộc gọi khiếu nại tăng vọt gấp 3 lần và chi phí thưởng vượt ngân sách mà khách hàng vẫn rời bỏ dịch vụ."
        ),
        "guiding_principles": ["Cobra Effect (Hiệu ứng rắn hổ mang)", "Động lực méo mó (Misaligned Incentives)", "Charlie Munger Incentive Law"],
        "step1_prompt": "Bóc tách: Nhân viên đã phát hiện ra lỗ hổng nào trong cơ chế thưởng để tư lợi (Tự tạo ra khiếu nại giả hoặc thông đồng để đóng lại nhận tiền)?",
        "step2_prompt": "Chiếu lăng kính: Bài học lịch sử chính quyền Anh trả tiền bắt rắn ở Ấn Độ dẫn đến việc người dân tự nuôi rắn để nộp lấy tiền thưởng.",
        "step3_prompt": "Hành động: Tái thiết kế cơ chế động lực gắn liền với mục tiêu thực chất: Thưởng theo tỷ lệ khách hàng hài lòng dài hạn (NPS / Retention Rate).",
        "elite_hint": "'Hãy cho tôi thấy cơ chế đãi ngộ, tôi sẽ chỉ cho bạn kết quả' — Charlie Munger.",
    },
    {
        "id": "DW-ADULT-05",
        "day_num": 5,
        "title": "Chiến Lược Quả Tạ Taleb (Barbell Strategy) Trong Tài Chính & Sự Nghiệp",
        "track": "adult",
        "scenario": (
            "Bạn có 1 tỷ đồng tiền tiết kiệm và đang băn khoăn cách phân bổ: "
            "Một cố vấn khuyên bạn dồn toàn bộ vào các sản phẩm 'rủi ro trung bình' với cam kết lãi suất 12%/năm (nhưng thực chất là trái phiếu doanh nghiệp rủi ro tiềm ẩn). "
            "Taleb khuyên bạn nên dùng Chiến lược Quả tạ (Barbell Strategy)."
        ),
        "guiding_principles": ["Chiến lược Quả tạ (Barbell)", "Bất đối xứng lồi (Convex Asymmetry)", "Tránh điểm vàng trung đạo giả tạo"],
        "step1_prompt": "Bóc tách: Tại sao vùng 'rủi ro trung bình' thường là cạm bẫy chết người nhất trong các cuộc khủng hoảng tài chính?",
        "step2_prompt": "Chiếu lăng kính: Hai đầu quả tạ: 85-90% nguồn lực đặt vào nơi siêu an toàn (Tiền gửi, Vàng, Trái phiếu chính phủ) + 10-15% đặt vào cơ hội có tiềm năng bùng nổ vô hạn (Startups, Đầu tư bất đối xứng).",
        "step3_prompt": "Hành động: Ứng dụng chiến lược Quả tạ vào cả sự nghiệp của bạn: Giữ công việc nền tảng vững chắc và dành 15% thời gian cho các dự án đột phá.",
        "elite_hint": "Bảo vệ tuyệt đối phần đáy khỏi nguy cơ phá sản, đồng thời mở toang cánh cửa đón nhận thiên nga đen tích cực.",
    },
    {
        "id": "DW-ADULT-06",
        "day_num": 6,
        "title": "Đàm Phán Hợp Đồng Thương Mại Với Đối Tác Nắm Vị Thế Thống Lĩnh",
        "track": "adult",
        "scenario": (
            "Doanh nghiệp nhỏ của bạn đang đàm phán cung cấp hàng hóa cho một chuỗi siêu thị bán lẻ khổng lồ. "
            "Họ ép giá bạn xuống mức hòa vốn và bắt bạn chịu thời hạn thanh toán công nợ 90 ngày. "
            "Nếu từ chối, bạn mất cơ hội tăng trưởng doanh thu; nếu đồng ý, dòng tiền của bạn có nguy cơ bị bóp nghẹt phá sản."
        ),
        "guiding_principles": ["BATNA (Best Alternative to a Negotiated Agreement)", "Chi phí chuyển đổi (Switching Costs)", "Lý thuyết trò chơi"],
        "step1_prompt": "Bóc tách: BATNA (Phương án thay thế tốt nhất nếu đàm phán đổ vỡ) của bạn là gì? Bạn có đang tự dồn mình vào thế 'buộc phải bán bằng mọi giá' không?",
        "step2_prompt": "Chiếu lăng kính: Phân tích sức mạnh mặc cả và giá trị độc bản không thể thay thế mà sản phẩm của bạn mang lại cho kệ hàng của họ.",
        "step3_prompt": "Hành động: Chiến lược đàm phán đa biến số: Chấp nhận giảm giá nhẹ để đổi lấy điều khoản thanh toán 15 ngày và quyền được đặt hàng ưu tiên.",
        "elite_hint": "Không bao giờ bước vào bàn đàm phán mà không có một BATNA vững chắc trong túi. Kẻ không dám đứng lên bỏ đi sẽ là kẻ bị lột sạch sành sanh.",
    },
    {
        "id": "DW-ADULT-07",
        "day_num": 7,
        "title": "Hệ Quả Bậc Hai Khi Ban Lãnh Đạo Cắt Giảm Ngân Sách Đào Tạo & R&D",
        "track": "adult",
        "scenario": (
            "Để làm đẹp báo cáo tài chính quý nhằm đạt mục tiêu lợi nhuận ngắn hạn, Giám đốc điều hành quyết định cắt giảm 60% ngân sách R&D và sa thải đội ngũ nghiên cứu tinh hoa. "
            "Kết quả Bậc 1: Lợi nhuận quý này tăng vọt 40%, cổ phiếu tăng giá, CEO được thưởng lớn. "
            "Nhưng điều gì đang đón chờ công ty sau 2 năm nữa?"
        ),
        "guiding_principles": ["Tư duy Bậc hai (Second-Order Thinking)", "Nợ kỹ thuật (Technical Debt)", "Ăn thịt tương lai"],
        "step1_prompt": "Bóc tách: Khoản lợi nhuận tăng thêm thực chất là do công ty tạo ra giá trị mới hay đang 'ăn thịt chính tương lai của mình'?",
        "step2_prompt": "Chiếu lăng kính: Hệ quả Bậc 2 (Sản phẩm lạc hậu, đối thủ vượt mặt) và Bậc 3 (Chảy máu chất xám không thể hồi phục, công ty mất thị phần vĩnh viễn).",
        "step3_prompt": "Hành động: Nếu là thành viên HĐQT hoặc cổ đông chiến lược, cách bạn chất vấn và thiết kế lại cơ chế thưởng của ban điều hành gắn với giá trị 5 năm.",
        "elite_hint": "Bất kỳ ai cũng có thể tăng lợi nhuận ngắn hạn bằng cách cắt bỏ bảo dưỡng động cơ. Nhưng chiếc máy bay sớm muộn gì cũng sẽ rơi tự do.",
    },
    {
        "id": "DW-ADULT-08",
        "day_num": 8,
        "title": "Chuyển Đổi Từ Bán Sức Lao Động Sang Đòn Bẩy Không Cần Xin Phép (Naval)",
        "track": "adult",
        "scenario": (
            "Bạn là một kế toán trưởng hoặc luật sư có chuyên môn 10 năm. Hiện tại bạn đang đổi 50 giờ mỗi tuần để lấy mức lương 40 triệu đồng. "
            "Nếu bạn ngừng làm việc 1 tháng vì ốm đau, thu nhập lập tức về 0. Bạn muốn xây dựng sự giàu có đích thực theo triết lý của Naval Ravikant."
        ),
        "guiding_principles": ["Permissionless Leverage (Code & Media)", "Chi phí biên = 0", "Tài sản trí tuệ"],
        "step1_prompt": "Bóc tách: Bạn đang sử dụng loại đòn bẩy nào: Lao động (phải thuê người), Vốn (phải xin tiền), hay Code/Media (tự do vận hành 24/7)?",
        "step2_prompt": "Chiếu lăng kính: Làm thế nào để đóng gói năng lực chuyên môn thành sản phẩm số (Khóa học chuyên sâu, Bộ công cụ mẫu, AI Agent hỗ trợ) có thể phục vụ 10.000 người cùng lúc?",
        "step3_prompt": "Hành động: Lập kế hoạch 90 ngày xây dựng 1 tài sản số không cần xin phép ai đầu tiên trong lĩnh vực chuyên môn của bạn.",
        "elite_hint": "Cho tôi một điểm tựa và một đòn bẩy, tôi sẽ nhấc bổng cả trái đất. Code và Media là hai cánh tay đòn vĩ đại nhất của thời đại số.",
    },
    {
        "id": "DW-ADULT-09",
        "day_num": 9,
        "title": "Quyết Định Sa Thải Một Ngôi Sao Bán Hàng Có Hành Vi Độc Hại Với Tổ Chức",
        "track": "adult",
        "scenario": (
            "Một nhân viên kinh doanh hàng đầu mang lại 35% tổng doanh số công ty nhưng liên tục lăng mạ đồng nghiệp, "
            "vi phạm quy tắc đạo đức và công khai thách thức các quy trình quản lý. Bạn là giám đốc và đang đứng trước tình thế tiến thoái lưỡng nan."
        ),
        "guiding_principles": ["Chi phí ngoại ứng tiêu cực (Negative Externalities)", "Văn hóa tổ chức", "Điểm sụp đổ hệ thống"],
        "step1_prompt": "Bóc tách: 35% doanh số bạn nhìn thấy có bù đắp được chi phí ẩn khổng lồ do tinh thần đồng đội sa sút, nhân sự giỏi khác bỏ đi và rủi ro kiện tụng không?",
        "step2_prompt": "Chiếu lăng kính: Khái niệm 'Trái táo độc' trong hệ sinh thái tổ chức: Một cá nhân độc hại có thể làm tha hóa cả một tập thể xuất sắc như thế nào?",
        "step3_prompt": "Hành động: Kế hoạch dứt khoát: Cách ly rủi ro, chuyển giao tệp khách hàng từng bước và kiên quyết sa thải để bảo vệ nền văn hóa bền vững.",
        "elite_hint": "Dung dưỡng một nhân tài độc hại là thông điệp ngầm tuyên bố rằng: Kết quả biện minh cho mọi hành vi bẩn thỉu. Đó là khởi đầu của sự sụp đổ.",
    },
    {
        "id": "DW-ADULT-10",
        "day_num": 10,
        "title": "Bẫy Thiên Kiến Xác Nhận (Confirmation Bias) Khi Đầu Tư Cổ Phiếu Tâm Huyết",
        "track": "adult",
        "scenario": (
            "Bạn đã đầu tư 50% tài sản vào một công ty công nghệ mà bạn từng nghiên cứu rất kỹ 3 năm trước. "
            "Gần đây, báo cáo tài chính cho thấy biên lợi nhuận sụt giảm, ban lãnh đạo bán tháo cổ phiếu và một đối thủ mới xuất hiện chiếm lĩnh thị phần. "
            "Nhưng bạn chỉ bấm vào các bài phân tích khen ngợi và tự trấn an: 'Đây chỉ là thử thách ngắn hạn, công ty này là số 1!'."
        ),
        "guiding_principles": ["Confirmation Bias", "Biên an toàn", "Bác bỏ giả thuyết (Falsification)"],
        "step1_prompt": "Bóc tách: Giả định cốt lõi ban đầu khi bạn mua cổ phiếu này (Moat - Con hào kinh tế) có còn nguyên vẹn trong hiện tại không?",
        "step2_prompt": "Chiếu lăng kính: Tâm lý học về sự dính mắc bản ngã (Ego Attachment): Não bộ thà mất tiền còn hơn phải thừa nhận mình đã phân tích sai lầm.",
        "step3_prompt": "Hành động: Thực hiện quy trình 'Pre-mortem' hoặc nhờ một chuyên gia phản biện chỉ ra 5 lý do tại sao công ty này có thể biến mất trong 5 năm tới.",
        "elite_hint": "Khi sự thật thay đổi, tôi thay đổi quyết định của mình. Còn ngài thì sao? — John Maynard Keynes.",
    },
    {
        "id": "DW-ADULT-11",
        "day_num": 11,
        "title": "Quản Trị Đòn Bẩy Vay Nợ (Margin / Nợ BĐS) Trước Chu Kỳ Lãi Suất Tăng",
        "track": "adult",
        "scenario": (
            "Bạn đang sở hữu 3 bất động sản với tỷ lệ vay nợ ngân hàng lên tới 70% giá trị tài sản. "
            "Khi lãi suất thả nổi bắt đầu tăng từ 8% lên 13%/năm, tiền trả gốc lãi hàng tháng vượt quá tổng thu nhập từ lương và tiền thuê nhà. "
            "Bạn phải vay mượn người thân để trả lãi và hy vọng thị trường sẽ sốt đất trở lại trong 6 tháng tới."
        ),
        "guiding_principles": ["Rào cản hấp thụ (Absorbing Barrier / Ruin Problem)", "Thanh khoản", "Tư duy Bậc hai"],
        "step1_prompt": "Bóc tách: Bạn có thể duy trì việc gồng lỗ này tối đa bao nhiêu tháng nếu thị trường đóng băng thêm 2 năm nữa?",
        "step2_prompt": "Chiếu lăng kính: Khái niệm 'Rào cản hấp thụ' trong xác suất: Một khi bạn chạm vào điểm phá sản (Ruin), mọi kỳ vọng về sự phục hồi sau đó đều vô nghĩa.",
        "step3_prompt": "Hành động: Dũng cảm hạ tỷ trọng: Bán cắt lỗ 1 bất động sản kém thanh khoản nhất để trả sạch nợ, bảo toàn dòng tiền sống sót cho gia đình.",
        "elite_hint": "Để thành công phi thường, trước hết bạn phải đảm bảo mình là kẻ không thể bị tiêu diệt. Đừng bao giờ chơi trò chơi có xác suất phá sản > 0.",
    },
    {
        "id": "DW-ADULT-12",
        "day_num": 12,
        "title": "Thực Hành Deep Work 90 Phút Thoát Khỏi Vòng Xoáy Họp Hành & Tin Nhắn Vô Tận",
        "track": "adult",
        "scenario": (
            "Một ngày làm việc điển hình của bạn: 8 tiếng ở văn phòng bị xé nát bởi 5 cuộc họp vô thưởng vô phạt, 50 tin nhắn Zalo/Slack và hàng chục email. "
            "Bạn luôn cảm thấy kiệt sức vào lúc 5h chiều nhưng nhìn lại thì chưa hoàn thành được một công việc tư duy chiến lược nào có giá trị cao."
        ),
        "guiding_principles": ["Deep Work (Cal Newport)", "Entropy nhận thức", "Bảo vệ tài sản thời gian"],
        "step1_prompt": "Bóc tách: Bao nhiêu % các cuộc họp bạn tham gia thực sự cần đến sự hiện diện của bạn và mang lại quyết định giá trị?",
        "step2_prompt": "Chiếu lăng kính: Chi phí chuyển đổi chú ý (Attention Residue): Mỗi khi liếc nhìn thông báo điện thoại, não bộ mất 20 phút để phục hồi trạng thái tập trung sâu.",
        "step3_prompt": "Hành động: Thiết lập 'Khung giờ vàng 90 phút thiêng liêng' vào đầu buổi sáng: Tắt toàn bộ thông báo, đóng cửa phòng để giải quyết bài toán đòn bẩy số 1.",
        "elite_hint": "Người làm việc hời hợt phản ứng với tiếng chuông réo của người khác; bậc thầy kiến tạo định hình ngày làm việc theo công trình của chính mình.",
    },
    {
        "id": "DW-ADULT-13",
        "day_num": 13,
        "title": "Ứng Dụng Trí Tuệ Vô Thường (Impermanence) Khi Doanh Nghiệp Gặp Khủng Hoảng",
        "track": "adult",
        "scenario": (
            "Mô hình kinh doanh từng đem lại cho bạn 100 triệu lợi nhuận mỗi tháng suốt 5 năm qua bỗng nhiên bị xóa sổ "
            "chỉ sau một đêm vì thay đổi thuật toán của nền tảng hoặc chính sách mới của nhà nước. Bạn rơi vào trạng thái hoang mang, u uất và phẫn uất với số phận."
        ),
        "guiding_principles": ["Quy luật Vô thường (Anicca)", "Tâm buông xả (Equanimity)", "Tính thích nghi tiến hóa"],
        "step1_prompt": "Bóc tách: Sự sụp đổ này có phải là bất công cá nhân, hay chỉ là sự vận hành tất yếu của quy luật đào thải tự nhiên trong nền kinh tế?",
        "step2_prompt": "Chiếu lăng kính: Trí tuệ Phật giáo về tính Không và Vô thường giúp gột rửa sự dính mắc vào vinh quang quá khứ như thế nào?",
        "step3_prompt": "Hành động: Tĩnh lặng tâm trí qua quan sát hơi thở 15 phút, sau đó nhìn vào đống tro tàn để nhận diện cơ hội tái sinh một mô hình mới kiên cường hơn.",
        "elite_hint": "Đau khổ sinh ra từ việc mong cầu những thứ vô thường phải trở nên bất biến. Chấp nhận sự biến dịch là chìa khóa của tự do nội tâm.",
    },
    {
        "id": "DW-ADULT-14",
        "day_num": 14,
        "title": "Bẫy Bước Ra Ngoài Vòng Tròn Năng Lực Khi Nghe Rủ Rê Đầu Tư BĐS Trái Ngành",
        "track": "adult",
        "scenario": (
            "Bạn là một bác sĩ phẫu thuật hoặc kỹ sư phần mềm xuất sắc. Sau khi tích lũy được 3 tỷ đồng, "
            "một nhóm bạn rủ bạn góp tiền mua đất rừng phân lô đón đầu quy hoạch du lịch sinh thái. "
            "Họ đưa ra các bản vẽ quy hoạch hào nhoáng và thúc giục bạn: 'Kèo này nội bộ, không vào ngay là mất phần!'."
        ),
        "guiding_principles": ["Vòng tròn năng lực (Circle of Competence)", "Bất cân xứng thông tin (Information Asymmetry)", "Biên an toàn"],
        "step1_prompt": "Bóc tách: Bạn có biết cách tự kiểm tra pháp lý quy hoạch tại Sở Tài nguyên không, hay bạn hoàn toàn phụ thuộc vào lời hứa của người khác?",
        "step2_prompt": "Chiếu lăng kính: Bất cân xứng thông tin: Trong một thương vụ đầu tư phức tạp, nếu bạn không biết ai là con gà trên bàn tiệc, thì chính bạn là con gà.",
        "step3_prompt": "Hành động: Dũng cảm nói 'Tôi không hiểu lĩnh vực này nên tôi xin phép đứng ngoài', tiếp tục tích lũy tài sản trong vùng mình làm chủ tuyệt đối.",
        "elite_hint": "Bảo vệ vốn là quy tắc số 1; không bao giờ quên quy tắc số 1 là quy tắc số 2. Giữ vững kỷ luật trong vòng tròn năng lực.",
    },
    {
        "id": "DW-ADULT-15",
        "day_num": 15,
        "title": "Phân Bổ Quy Mô Vị Thế Theo Tiêu Chuẩn Kelly (Kelly Criterion)",
        "track": "adult",
        "scenario": (
            "Bạn tìm ra một cơ hội giao dịch hoặc một phi vụ đầu tư mà bạn đánh giá có xác suất thắng 70% với tỷ lệ lời/lỗ là 2:1. "
            "Vì quá tự tin, bạn quyết định vay mượn thêm và đặt cược 80% tổng tài sản vào thương vụ này. "
            "Bạn tự nhủ: 'Xác suất thắng tận 70%, sợ gì không tất tay!'.",
        ),
        "guiding_principles": ["Tiêu chuẩn Kelly (Kelly Criterion)", "Xác suất sống còn", "Biến động vốn (Drawdown)"],
        "step1_prompt": "Bóc tách: Dù xác suất thắng là 70%, thì xác suất thua 30% có thể xảy ra trong lần cược đầu tiên không?",
        "step2_prompt": "Chiếu lăng kính: Công thức Kelly $f^* = (bp - q) / b$ chỉ ra tỷ lệ đặt cược tối ưu để tối đa hóa tốc độ tăng trưởng vốn mà không làm sụp đổ tài khoản.",
        "step3_prompt": "Hành động: Áp dụng Fractional Kelly (ví dụ: Half Kelly, chỉ cược 15-20% vốn) để vừa tối ưu tăng trưởng vừa chịu đựng được chuỗi rủi ro xui xẻo.",
        "elite_hint": "Thậm chí với lợi thế vượt trội, đặt cược quá tay (Over-betting) cũng sẽ đưa xác suất phá sản dài hạn tiến về 100%.",
    },
    {
        "id": "DW-ADULT-16",
        "day_num": 16,
        "title": "Tái Cấu Trúc Bản Thân Trước Nguy Cơ Khủng Hoảng Tuổi Trung Niên & Bị AI Thay Thế",
        "track": "adult",
        "scenario": (
            "Ở tuổi 38, bạn nhận thấy các công việc phân tích, dịch thuật, viết lách và lập trình mà bạn từng tự hào làm tốt suốt 15 năm "
            "bây giờ các mô hình AI có thể xử lý trong vài giây với chi phí gần bằng 0. Cảm giác hoang mang về sự vô dụng và khủng hoảng danh tính bắt đầu ập đến."
        ),
        "guiding_principles": ["First Principles", "Định vị lại năng lực cốt lõi", "Sự đồng cảm và khả năng ra quyết định"],
        "step1_prompt": "Bóc tách: Đâu là kỹ năng lặp lại máy móc (AI thay thế dễ dàng) và đâu là kỹ năng con người độc bản (Thấu cảm, phán đoán đạo đức, tổng hợp đa ngành, lãnh đạo)?",
        "step2_prompt": "Chiếu lăng kính: Tư duy tiến hóa: Bỏ qua việc cạnh tranh tốc độ tính toán với máy móc; chuyển sang định vị bản thân thành 'Kiến trúc sư chỉ huy hệ thống AI'.",
        "step3_prompt": "Hành động: Lập kế hoạch học tập siêu tốc 6 tháng: Làm chủ kỹ năng điều phối Agentic AI kết hợp với sự hiểu biết sâu sắc về tâm lý con người trong ngành của bạn.",
        "elite_hint": "AI không thay thế con người; con người biết kết hợp tư duy First Principles với đòn bẩy AI sẽ thay thế những người làm việc như những cỗ máy cũ kỹ.",
    },
    {
        "id": "DW-ADULT-17",
        "day_num": 17,
        "title": "Đọc Vị Dấu Chân Dòng Tiền Smart Money (VSA) Ở Vùng Phân Phối Đỉnh",
        "track": "adult",
        "scenario": (
            "Một mã cổ phiếu đã tăng 200% trong 6 tháng qua. Trên báo chí xuất hiện hàng loạt bài phỏng vấn lãnh đạo với những kế hoạch doanh thu nghìn tỷ. "
            "Tuy nhiên, trên biểu đồ kỹ thuật: Thanh khoản khớp lệnh đạt kỷ lục lịch sử nhưng giá cổ phiếu không thể tăng thêm, liên tục xuất hiện các cây nến có râu trên dài ngoằng (Upthrust). "
            "Môi giới giục bạn: 'Múc thêm đi, chuẩn bị vượt đỉnh lịch sử!'.",
        ),
        "guiding_principles": ["VSA (Volume Spread Analysis)", "Dòng tiền Smart Money vs Dòng tiền F0", "Cân bằng Cung - Cầu Wyckoff"],
        "step1_prompt": "Bóc tách: Sự thật đo lường được: Khối lượng giao dịch cực lớn nhưng biên độ giá không tăng (Effort vs Result bất thường) chứng minh điều gì?",
        "step2_prompt": "Chiếu lăng kính: Quá trình phân phối hàng của dòng tiền lớn Smart Money cho đám đông hưng phấn đang diễn ra như thế nào?",
        "step3_prompt": "Hành động: Kỷ luật dứt khoát: Chốt lời từng phần, nâng chặn lãi (Trailing Stop) và từ chối tham lam giọt mật cuối cùng trên lưỡi dao lam.",
        "elite_hint": "Khi báo chí rầm rộ tin tốt và thanh khoản bùng nổ mà giá không tăng, đó là lúc dòng tiền thông minh đang âm thầm trao lại 'củ khoai lang nóng' cho đám đông.",
    },
    {
        "id": "DW-ADULT-18",
        "day_num": 18,
        "title": "Quản Lý Kỳ Vọng Gia Đình & Thiết Lập Ranh Giới Giữa Sự Nghiệp & Con Cái",
        "track": "adult",
        "scenario": (
            "Bạn đang ở giai đoạn then chốt của sự nghiệp, mỗi ngày làm việc 12 tiếng để kiếm tiền lo cho tương lai con cái học trường quốc tế. "
            "Tuy nhiên, con bạn ngày càng xa cách, bướng bỉnh và không muốn nói chuyện với bạn. "
            "Bạn tự an ủi: 'Mình cày cuốc vất vả thế này cũng chỉ vì tương lai của nó thôi mà, sao nó không hiểu?'."
        ),
        "guiding_principles": ["Tư duy Bậc hai", "Khoảng cửa sổ phát triển tâm lý (Critical Windows)", "Chi phí cơ hội tình cảm"],
        "step1_prompt": "Bóc tách: Đứa trẻ 6-15 tuổi thực sự cần điều gì nhất: Trường học triệu đô hay sự hiện diện chất lượng của người cha/mẹ trong những năm tháng định hình nhân cách?",
        "step2_prompt": "Chiếu lăng kính: Khoảng cửa sổ phát triển tâm lý của con chỉ mở ra một lần duy nhất trong đời; một khi con đã lớn, tiền bạc không thể mua lại thời thơ ấu đó.",
        "step3_prompt": "Hành động: Thiết lập nguyên tắc bất khả xâm phạm: 1 giờ mỗi tối hoàn toàn không điện thoại/công việc, hiện diện 100% để lắng nghe và chơi cùng con.",
        "elite_hint": "Không có bất kỳ thành công rực rỡ nào ngoài xã hội có thể bù đắp được sự đổ vỡ ngay trong chính ngôi nhà của bạn.",
    },
]

# -----------------------------------------------------------------------------
# 2. LOGIC LẤY BÀI TẬP WORKOUT THEO CHỦ ĐỀ & THEO NGÀY
# -----------------------------------------------------------------------------
def get_workouts_by_track(track: str = "all") -> List[Dict[str, Any]]:
    """Lấy toàn bộ danh sách bài tập thuộc về một chủ đề cụ thể."""
    if track == "k12":
        return [w for w in DAILY_WORKOUT_BANK if w.get("track") == "k12"]
    elif track == "adult":
        return [w for w in DAILY_WORKOUT_BANK if w.get("track") == "adult"]
    else:
        return [w for w in DAILY_WORKOUT_BANK if w.get("track") == "all"]


def get_workout_by_id(workout_id: str) -> Optional[Dict[str, Any]]:
    """Tìm kiếm một bài tập cụ thể theo ID."""
    for w in DAILY_WORKOUT_BANK:
        if w.get("id") == workout_id:
            return w
    return None


def get_today_workout(track: str = "all", day_offset: int = 0) -> Dict[str, Any]:
    """
    Lấy bài tập hôm nay dựa trên ngày trong năm và bộ lọc đối tượng độc lập.
    Đảm bảo 100% không bị trùng lặp giữa các phân hệ Đa lĩnh vực vs K12 vs Người lớn.
    """
    candidates = get_workouts_by_track(track)
    if not candidates:
        candidates = DAILY_WORKOUT_BANK

    day_of_year = datetime.now().timetuple().tm_yday + day_offset
    idx = day_of_year % len(candidates)
    return candidates[idx]


# -----------------------------------------------------------------------------
# 3. QUẢN LÝ CHUỖI STREAK & LỊCH SỬ NGƯỜI DÙNG
# -----------------------------------------------------------------------------
def get_user_streak_info(username: str) -> Dict[str, Any]:
    """Lấy thông tin chuỗi rèn luyện liên tục (Streak) của người dùng."""
    hist = load_user_history(username)
    dw_data = hist.setdefault("daily_workouts", {
        "current_streak": 0,
        "longest_streak": 0,
        "last_workout_date": None,
        "total_completed": 0,
        "history": []
    })

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    last_date = dw_data.get("last_workout_date")

    is_done_today = (last_date == today_str)

    # Nếu ngày cuối làm bài trước hôm qua và chưa làm hôm nay -> chuỗi bị đứt (reset về 0)
    current_streak = dw_data.get("current_streak", 0)
    if last_date and last_date != today_str and last_date != yesterday_str:
        current_streak = 0
        dw_data["current_streak"] = 0
        save_user_history(username, hist)

    return {
        "current_streak": current_streak,
        "longest_streak": dw_data.get("longest_streak", current_streak),
        "is_done_today": is_done_today,
        "total_completed": dw_data.get("total_completed", 0),
        "last_workout_date": last_date,
        "history": dw_data.get("history", []),
    }


def record_daily_workout_answer(
    username: str,
    workout_id: str,
    workout_title: str,
    step1_ans: str,
    step2_ans: str,
    step3_ans: str,
    ai_feedback: str = "",
) -> Dict[str, Any]:
    """Ghi nhận bài làm 15 phút hôm nay và cập nhật chuỗi Streak."""
    hist = load_user_history(username)
    dw_data = hist.setdefault("daily_workouts", {
        "current_streak": 0,
        "longest_streak": 0,
        "last_workout_date": None,
        "total_completed": 0,
        "history": []
    })

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    last_date = dw_data.get("last_workout_date")

    if last_date == today_str:
        # Đã hoàn thành hôm nay, chỉ cập nhật bài mới nhất
        pass
    elif last_date == yesterday_str:
        # Nối tiếp chuỗi từ hôm qua
        dw_data["current_streak"] = dw_data.get("current_streak", 0) + 1
        dw_data["total_completed"] = dw_data.get("total_completed", 0) + 1
    else:
        # Chuỗi mới bắt đầu
        dw_data["current_streak"] = 1
        dw_data["total_completed"] = dw_data.get("total_completed", 0) + 1

    if dw_data["current_streak"] > dw_data.get("longest_streak", 0):
        dw_data["longest_streak"] = dw_data["current_streak"]

    dw_data["last_workout_date"] = today_str

    entry = {
        "workout_id": workout_id,
        "title": workout_title,
        "date": today_str,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "step1": step1_ans,
        "step2": step2_ans,
        "step3": step3_ans,
        "ai_feedback": ai_feedback,
    }

    history_list = dw_data.setdefault("history", [])
    history_list.insert(0, entry)
    dw_data["history"] = history_list[:50]  # Giữ 50 bài gần nhất

    save_user_history(username, hist)
    return dw_data


# -----------------------------------------------------------------------------
# 4. AI MENTOR PHẢN HỒI BÀI TẬP WORKOUT
# -----------------------------------------------------------------------------
DAILY_WORKOUT_FEEDBACK_PROMPT = """Bạn là Elite Thinking Mentor (Gia sư Tư duy Tinh hoa).
Học viên vừa hoàn thành bài tập rèn luyện tư duy 15 phút theo quy trình 3 bước:
1. Bóc tách Sự thật vs Ý kiến
2. Chiếu lăng kính mô hình hạt nhân
3. Đề xuất hành động đòn bẩy bất đối xứng

Nhiệm vụ: Hãy đưa ra nhận xét sắc bén, sâu sắc, ngắn gọn (4-6 câu) bằng tiếng Việt.
Cấu trúc phản hồi:
- 🌟 Điểm sắc sảo nhất trong câu trả lời của học viên.
- 🔍 Một góc nhìn sâu hơn hoặc điểm mù họ còn bỏ sót (gợi ý thêm mô hình liên quan).
- ⚡ Lời khuyên hành động thực tế tiếp theo.
Văn phong: Đĩnh đạc, thông tuệ, khích lệ nhưng khắt khe chuẩn mực tinh hoa.
"""

def evaluate_daily_workout(
    api_keys: Union[str, List[str], tuple],
    model_name: str,
    workout: Dict[str, Any],
    step1_ans: str,
    step2_ans: str,
    step3_ans: str,
) -> str:
    """Gọi AI Mentor để phản biện bài tập 15 phút."""
    keys = _normalize_keys(api_keys)
    if not keys:
        return "Chưa có API key để sinh phản hồi AI. Hãy đối chiếu với Gợi ý tinh hoa của bài tập."

    prompt = f"""Tình huống: {workout.get('title')}
Bối cảnh: {workout.get('scenario')}
Nguyên lý định hướng: {', '.join(workout.get('guiding_principles', []))}

BÀI LÀM CỦA HỌC VIÊN:
Bước 1 (Sự thật vs Ý kiến):
{step1_ans}

Bước 2 (Chiếu lăng kính mô hình):
{step2_ans}

Bước 3 (Hành động bất đối xứng):
{step3_ans}
"""

    candidates = [model_name, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
    last_err = None

    for idx, current_key in enumerate(keys, 1):
        mask = _mask_key(current_key)
        try:
            genai.configure(api_key=current_key)
        except Exception as e:
            last_err = f"Lỗi cấu hình Key #{idx}: {e}"
            continue

        for candidate in candidates:
            try:
                model = genai.GenerativeModel(
                    model_name=candidate,
                    system_instruction=DAILY_WORKOUT_FEEDBACK_PROMPT,
                )
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                err_msg = str(e)
                last_err = f"Key #{idx} ({mask}) lỗi: {err_msg}"
                if _is_quota_or_auth_error(err_msg):
                    break
                continue

    return f"Không thể tạo phản hồi từ AI. Lỗi: {last_err}"
