# -*- coding: utf-8 -*-
"""Quiz & Active Recall Engine (Elite Cognitive Mastery System).

Hệ thống luyện nhớ và phản xạ tư duy:
1. Curated Scenario-Based Quizzes for:
   - 9 Chế độ Tư duy Elite
   - 88 Mô hình Hạt nhân (Munger Latticework)
   - 100 Nguyên lý Khởi thủy
2. Spaced Retrieval Flashcard Generator (Active Recall)
3. AI Dynamic Quiz Generator (Gemini Multi-key Failover)
4. AI Feynman Challenge Evaluator
5. User Mastery Stats Tracking
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

try:
    import google.generativeai as genai
except Exception:
    genai = None

from utils.knowledge import load_user_history, save_user_history, load_knowledge_base
from utils.mental_models import get_all_models, filter_models

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# =============================================================================
# 0. NGÂN HÀNG TRẮC NGHIỆM LÝ THUYẾT RÀNH MẠCH (THEORY FOUNDATION QUIZ)
# =============================================================================
THEORY_MODES_QUIZ = [
    {
        "id": "TH-MODE-01",
        "concept": "First Principles (Tư duy Nguyên bản)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Theo Aristotle và Elon Musk, bản chất lý thuyết cốt lõi của Tư duy Nguyên bản (First Principles Thinking) là gì?",
        "options": [
            "A. Phân rã bài toán về những chân lý cơ bản nhất không thể suy diễn thêm, tách biệt Sự thật (Fact) khỏi Ý kiến (Opinion) và tái thiết kế giải pháp từ số 0.",
            "B. Tìm giải pháp đơn giản nhất trong số các phương án đang có sẵn trên thị trường.",
            "C. Lập kế hoạch tài chính chi tiết 5 năm dựa trên kết quả của các công ty đi trước.",
            "D. Phân tích điểm mạnh, điểm yếu, cơ hội và thách thức (SWOT) theo thông lệ ngành."
        ],
        "correct_index": 0,
        "explanation": "First Principles là phương pháp tư duy bóc tách tận cùng chân lý bất biến (vật lý, toán học), đối lập hoàn toàn với Reasoning by Analogy (suy luận bắt chước theo kinh nghiệm đám đông).",
        "trap_analysis": "Bẫy bắt chước (Analogy Trap): Tin rằng điều gì người khác đang làm thì mặc định là tối ưu nhất."
    },
    {
        "id": "TH-MODE-02",
        "concept": "Tư duy Xác suất & Cập nhật Bayes (Probabilistic & Bayesian)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Trong tư duy xác suất Bayes, công thức cốt lõi để cập nhật niềm tin khi xuất hiện dữ kiện mới là gì?",
        "options": [
            "A. Posterior (Xác suất mới) ∝ Prior (Niềm tin ban đầu / Tỷ lệ nền) × Likelihood (Khả năng xuất hiện của dữ kiện mới).",
            "B. Posterior = Trung bình cộng của tất cả các ý kiến chuyên gia uy tín trong ngành.",
            "C. Posterior = Niềm tin ban đầu cộng thêm cảm xúc và trực giác nhạy bén của nhà đầu tư.",
            "D. Posterior = 100% nếu có ít nhất một bài báo hoặc nguồn tin nội bộ xác nhận."
        ],
        "correct_index": 0,
        "explanation": "Định lý Bayes ép tư duy không nhìn nhận thế giới theo nhị nguyên Đúng/Sai, mà nhìn theo phổ xác suất liên tục được điều chỉnh khách quan theo dữ kiện thực nghiệm.",
        "trap_analysis": "Bẫy thờ ơ tỷ lệ nền (Base Rate Fallacy) & Bẫy Cố chấp: Quên mất xác suất ban đầu hoặc không chịu hạ xác suất khi dữ kiện thực tế xấu đi."
    },
    {
        "id": "TH-MODE-03",
        "concept": "Tư duy Đảo ngược (Inversion — Charlie Munger)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Quy tắc cốt lõi của phương pháp Tư duy Đảo ngược (Inversion / Premortem) trong việc ra quyết định là gì?",
        "options": [
            "A. Thay vì tìm cách để thành công rực rỡ, hãy liệt kê mọi điều chắc chắn dẫn tới thảm họa/thất bại rồi chủ động né tránh chúng.",
            "B. Luôn làm điều ngược lại với những gì đồng nghiệp hoặc đối thủ đang làm.",
            "C. Bán tháo toàn bộ danh mục tài sản khi thị trường vừa mới xuất hiện một tin tức xấu.",
            "D. Đảo ngược thứ tự các công việc trong ngày từ việc dễ nhất làm trước đến việc khó nhất."
        ],
        "correct_index": 0,
        "explanation": "Charlie Munger đúc kết: 'Người ta thường quá tập trung vào việc làm sao để trở nên xuất chúng, mà quên mất rằng việc bền bỉ tránh những điều ngu ngốc mới tạo ra kết quả phi thường'.",
        "trap_analysis": "Bẫy chỉ nhìn về phía trước (Forward-only): Chỉ vẽ kịch bản màu hồng mà mù tịt trước những lỗ thủng làm chìm tàu."
    },
    {
        "id": "TH-MODE-04",
        "concept": "Tư duy Bậc hai (Second-Order Thinking — Howard Marks)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Điểm phân định cốt lõi giữa Tư duy Bậc một và Tư duy Bậc hai (Second-Order Thinking) là gì?",
        "options": [
            "A. Bậc một chỉ nhìn tác động hiển hiện trước mắt; Bậc hai luôn hỏi 'Và sau đó điều gì xảy ra?' để tính phản ứng của các tác nhân và hệ quả lan truyền 1–3 năm tới.",
            "B. Bậc một là suy nghĩ định tính, Bậc hai là suy nghĩ định lượng bằng máy tính.",
            "C. Bậc một dành cho người mới đi làm, Bậc hai chỉ dành riêng cho các tỷ phú.",
            "D. Bậc hai là suy nghĩ đi suy nghĩ lại hai lần trước khi phát biểu."
        ],
        "correct_index": 0,
        "explanation": "Hầu hết các sai lầm thảm họa xã hội và kinh tế đều bắt nguồn từ tư duy bậc một: làm một việc có vẻ tốt tức thời nhưng hủy hoại cấu trúc hệ thống về lâu dài.",
        "trap_analysis": "Bẫy tầm nhìn ngắn hạn: Coi hệ quả trước mắt là toàn bộ câu chuyện mà không dự phóng phản ứng dây chuyền."
    },
    {
        "id": "TH-MODE-05",
        "concept": "Tư duy Tùy chọn & Bất đối xứng (Optionality & Barbell — Nassim Taleb)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Chiến lược Đòn tạ (Barbell Strategy) của Nassim Nicholas Taleb được cấu trúc lý thuyết như thế nào?",
        "options": [
            "A. 85-90% nguồn lực đặt vào các tài sản an toàn tuyệt đối (tránh rủi ro hủy diệt), 10-15% phân bổ vào các tùy chọn có rủi ro giới hạn nhưng tiềm năng lợi nhuận vô hạn bất đối xứng.",
            "B. Dồn toàn bộ 100% tài sản vào các cơ hội có rủi ro trung bình để sinh lời ổn định quanh năm.",
            "C. Vay nợ tối đa (đòn bẩy cao) khi nhận thấy một cơ hội có vẻ chắc thắng 99%.",
            "D. Chia đều tài sản thành 10 phần bằng nhau và đầu tư dàn trải không phân biệt rủi ro."
        ],
        "correct_index": 0,
        "explanation": "Chiến lược Barbell giúp hệ thống đạt trạng thái Chống Mong Manh (Antifragile): Tuyệt đối không bị xóa sổ khi có thiên nga đen, nhưng luôn có cửa bùng nổ khi cơ hội lớn đến.",
        "trap_analysis": "Bẫy vùng giữa chết chóc (Middle Ground): Chọn vị thế rủi ro trung bình — vừa đủ bấp bênh để mất sạch, nhưng tiềm năng tăng trưởng lại bị chặn trần."
    },
    {
        "id": "TH-MODE-06",
        "concept": "Mạng lưới Đa ngành Latticework (Charlie Munger)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Tại sao Charlie Munger khẳng định việc nắm vững các mô hình hạt nhân từ nhiều ngành khoa học cơ bản là bắt buộc?",
        "options": [
            "A. Để tránh Hội chứng Người cầm búa (Man with a Hammer) và kích hoạt hiệu ứng cộng hưởng Lollapalooza khi các quy luật từ nhiều ngành cùng hội tụ.",
            "B. Để có thể thể hiện sự uyên bác trong các cuộc đàm phán kinh doanh phức tạp.",
            "C. Vì chỉ cần một môn khoa học duy nhất là kinh tế học đã đủ sức giải thích toàn bộ thế giới nếu học đủ sâu.",
            "D. Để không bao giờ cần phải tham khảo ý kiến của các chuyên gia tư vấn."
        ],
        "correct_index": 0,
        "explanation": "Thực tế là một mạng lưới liên kết phức tạp. Người chỉ có một lăng kính duy nhất sẽ luôn bóp méo thực tế để vừa vặn với chuyên môn hạn hẹp của mình.",
        "trap_analysis": "Hội chứng chuyên gia hạn hẹp: Cầm búa thì nhìn đâu cũng thấy đinh."
    },
    {
        "id": "TH-MODE-07",
        "concept": "Thực nghiệm Nhanh (Iterative Lean Thinking)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Vòng lặp học hỏi cốt lõi trong Tư duy Thực nghiệm Nhanh (Build - Measure - Learn) nhằm mục đích giải quyết căn bệnh tư duy nào?",
        "options": [
            "A. Bệnh Phân tích Tê liệt (Analysis Paralysis): Ngồi suy diễn lý thuyết trong phòng kín mà không đưa giả thuyết ra va chạm với thực tế đo lường được.",
            "B. Bệnh thiếu vốn đầu tư mạo hiểm giai đoạn hạt giống.",
            "C. Bệnh không thể xin được giấy phép kinh doanh của cơ quan quản lý.",
            "D. Bệnh tuyển dụng nhân sự quá nhanh so với quy mô doanh thu."
        ],
        "correct_index": 0,
        "explanation": "Trong môi trường bất định cao, mọi kế hoạch trên giấy đều là giả định chưa được chứng minh. Tốc độ thực nghiệm vi mô với chi phí thấp quyết định tốc độ chạm vào sự thật.",
        "trap_analysis": "Bẫy ảo tưởng kế hoạch hoàn hảo: Bỏ hàng năm trời làm sản phẩm mà không chịu tiếp xúc với phản hồi của người dùng."
    },
    {
        "id": "TH-MODE-08",
        "concept": "Lý thuyết Trò chơi & Ma trận Động lực (Game Theory & Incentives)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Quy tắc thiết kế cơ chế (Mechanism Design) trong Lý thuyết Trò chơi đòi hỏi điều gì để tổ chức tự vận hành bền vững?",
        "options": [
            "A. Căn chỉnh động lực (Aligned Incentives) sao cho việc hành động vì lợi ích chung cũng chính là phương án tối đa hóa lợi ích cá nhân của từng tác nhân.",
            "B. Sử dụng camera giám sát dày đặc và các hình phạt tiền nặng nề cho mọi sai sót nhỏ.",
            "C. Kêu gọi tinh thần trách nhiệm và lòng yêu nghề tự nguyện của các thành viên.",
            "D. Thay đổi toàn bộ đội ngũ quản lý sau mỗi quý để tránh việc thông đồng lợi ích."
        ],
        "correct_index": 0,
        "explanation": "Con người phản ứng với động lực (Incentives), không phản ứng với khẩu hiệu. Khi cơ chế win-win được thiết kế chuẩn, sự tự giác xuất hiện mà không cần cưỡng chế.",
        "trap_analysis": "Bẫy ngây thơ: Trông đợi con người hành động vì sự tốt đẹp khi mà cơ chế lương thưởng ngầm lại đang khuyến khích họ gian lận."
    },
    {
        "id": "TH-MODE-09",
        "concept": "Đa quy mô Thời gian (Multi-Scale Time Horizons — Jeff Bezos)",
        "angle": "concept",
        "angle_label": "🔬 Bản chất & Định nghĩa",
        "question": "Theo triết lý kinh doanh của Jeff Bezos, đâu là trọng tâm của Tư duy Đa quy mô Thời gian (10-year horizon)?",
        "options": [
            "A. Xác định những nguyên lý và nhu cầu cốt lõi KHÔNG THAY ĐỔI trong 10-20 năm tới để dồn toàn lực đầu tư vào đó, thay vì mải miết chạy theo trào lưu ngắn hạn.",
            "B. Bỏ qua hoàn toàn việc kiếm lợi nhuận và kiểm soát dòng tiền của ngày hôm nay.",
            "C. Thay đổi chiến lược cốt lõi của công ty sau mỗi tháng dựa trên biến động giá cổ phiếu.",
            "D. Thuê các nhà chiêm tinh học để dự báo chính xác nền kinh tế của 2 thập kỷ tới."
        ],
        "correct_index": 0,
        "explanation": "Lợi thế cạnh tranh khổng lồ và sức mạnh lãi kép luôn thuộc về người dám neo giữ tầm nhìn vào những thứ không đổi và kiên định thực thi trong 10 năm.",
        "trap_analysis": "Bẫy thiển cận (Hyperbolic Discounting): Bộ não người luôn muốn dopamine tức thì, định giá quá cao cái lợi hôm nay và xem nhẹ tương lai 10 năm."
    },
    # --- 9 CÂU HỎI VẬN HÀNH & KÍCH HOẠT (OPERATIONAL PROCESS) ---
    {
        "id": "TH-MODE-OP-01",
        "concept": "First Principles (Tư duy Nguyên bản)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Quy trình 3 bước chuẩn mực của Elon Musk để áp dụng Tư duy Nguyên bản vào bài toán khó là gì?",
        "options": [
            "A. 1. Nhận diện & chất vấn các giả định ngầm ➔ 2. Bóc tách bài toán về các chân lý vật lý/khoa học cơ bản nhất ➔ 3. Tái thiết kế giải pháp mới từ số 0.",
            "B. 1. Khảo sát các đối thủ đầu ngành ➔ 2. Sao chép 80% tính năng cốt lõi ➔ 3. Hạ giá bán 10% để cạnh tranh.",
            "C. 1. Thuê công ty tư vấn chiến lược ➔ 2. Biểu quyết theo ý kiến đa số ➔ 3. Triển khai theo quy trình ISO.",
            "D. 1. Dự toán ngân sách tối đa ➔ 2. Mua thiết bị có sẵn trên thị trường ➔ 3. Tuyển dụng nhân sự quy mô lớn."
        ],
        "correct_index": 0,
        "explanation": "Elon Musk áp dụng 3 bước: Ép mọi chuyên gia phải trả lời câu hỏi 'Tại sao phải như vậy theo định luật vật lý?', sau đó tính toán chi phí nguyên tử và tái lập quy trình.",
        "trap_analysis": "Bẫy chấp nhận định kiến: Coi quy trình của người khác là giới hạn bất biến của vũ trụ."
    },
    {
        "id": "TH-MODE-OP-02",
        "concept": "Tư duy Xác suất & Cập nhật Bayes (Probabilistic & Bayesian)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Khi tiếp nhận một thông tin hoặc bằng chứng mới (Evidence), quy trình cập nhật niềm tin chuẩn xác theo Tư duy Bayes là gì?",
        "options": [
            "A. Khởi đầu từ Tỷ lệ nền khách quan (Base Rate / Prior) ➔ Đo lường độ tin cậy của dữ kiện mới (Likelihood) ➔ Tính toán xác suất mới (Posterior).",
            "B. Lập tức thay đổi 100% quan điểm ngay khi có một người nổi tiếng hoặc bài báo lớn đưa tin.",
            "C. Bỏ qua hoàn toàn dữ kiện mới nếu nó trái ngược với niềm tin ban đầu của bản thân.",
            "D. Lấy trung bình cộng giữa niềm tin cũ và cảm xúc nhất thời khi đọc tin tức."
        ],
        "correct_index": 0,
        "explanation": "Tư duy Bayes đòi hỏi bạn phải có điểm tựa Tỷ lệ nền (Base Rate). Một bằng chứng mạnh mới đủ sức làm dịch chuyển đáng kể xác suất niềm tin.",
        "trap_analysis": "Bẫy phóng đại bằng chứng hiếm: Bị kích động bởi một tin tức giật gân mà quên mất xác suất nền của sự việc vốn rất nhỏ."
    },
    {
        "id": "TH-MODE-OP-03",
        "concept": "Tư duy Đảo ngược (Inversion — Charlie Munger)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Kỹ thuật Khám nghiệm trước thất bại (Premortem) trong Tư duy Đảo ngược được tiến hành như thế nào?",
        "options": [
            "A. Đặt giả định dự án đã thất bại thảm hại sau 1 năm nữa, yêu cầu cả đội ngũ lùi lại tìm mọi nguyên nhân tiềm tàng gây ra cái chết đó để triệt tiêu ngay hôm nay.",
            "B. Chờ đến khi dự án thất bại thật rồi mới họp toàn công ty để tìm người chịu trách nhiệm kỷ luật.",
            "C. Cấm toàn bộ nhân viên nói về rủi ro hay những điều tiêu cực trong các cuộc họp kế hoạch.",
            "D. Lùi ngày triển khai dự án vô thời hạn cho đến khi thị trường không còn bất kỳ rủi ro nào."
        ],
        "correct_index": 0,
        "explanation": "Premortem (Gary Klein & Charlie Munger) hợp pháp hóa việc phê bình và tìm lỗ hổng: biến nỗi sợ thành bảng kiểm phòng vệ trước khi viên đạn đầu tiên được bắn ra.",
        "trap_analysis": "Bẫy tư duy lạc quan mù quáng: Xem việc phòng ngừa rủi ro là bàn lùi hoặc thiếu quyết tâm."
    },
    {
        "id": "TH-MODE-OP-04",
        "concept": "Tư duy Bậc hai (Second-Order Thinking — Howard Marks)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Câu hỏi kích hoạt (Trigger Question) phản xạ tư duy bậc hai của nhà đầu tư huyền thoại Howard Marks là gì?",
        "options": [
            "A. 'Và sau đó điều gì sẽ xảy ra?' (And then what?) — Nhằm dự phóng phản ứng của các đối thủ và hệ quả lan truyền trong tương lai.",
            "B. 'Làm thế nào để kiếm lợi nhuận tối đa trong phiên giao dịch ngày hôm nay?'",
            "C. 'Ai là người chịu trách nhiệm pháp lý nếu kế hoạch này đổ vỡ?'",
            "D. 'Làm sao để làm hài lòng tất cả các bên trong 1 tháng tới?'"
        ],
        "correct_index": 0,
        "explanation": "Tư duy bậc hai buộc bạn phải tự hỏi: 'Nếu mọi người đều đổ xô làm việc này thì thị trường sẽ phản ứng thế nào? Lợi thế có còn tồn tại không?'.",
        "trap_analysis": "Bẫy hệ quả bậc 1: Nhìn thấy món hời trước mắt mà không thấy chiếc bẫy chuột treo phía trên."
    },
    {
        "id": "TH-MODE-OP-05",
        "concept": "Tư duy Tùy chọn & Bất đối xứng (Optionality & Barbell — Nassim Taleb)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Để bảo vệ sự nghiệp hoặc danh mục đầu tư theo Chiến lược Thanh tạ (Barbell Allocation), bạn nên phân bổ nguồn lực như thế nào?",
        "options": [
            "A. Giữ 85–90% cực kỳ an toàn (chống rủi ro hủy diệt) + 10–15% thử nghiệm mạo hiểm có tiềm năng tăng trưởng vô hạn bất đối xứng; né tránh vùng trung bình mập mờ.",
            "B. Chia đều 50% vào tài sản rủi ro cao và 50% vào tài sản rủi ro trung bình.",
            "C. Vay nợ đòn bẩy tối đa để đầu tư vào một cơ hội duy nhất mà bạn tin tưởng 99%.",
            "D. Giữ 100% tiền mặt trong két sắt và từ chối mọi cơ hội mạo hiểm trong suốt cuộc đời."
        ],
        "correct_index": 0,
        "explanation": "Chiến lược Barbell giúp hệ thống đạt trạng thái Antifragile: Cực đoan ở hai đầu (Siêu an toàn & Siêu tùy chọn) và loại bỏ hoàn toàn vùng giữa nguy hiểm.",
        "trap_analysis": "Bẫy lầm tưởng vùng an toàn: Nghĩ rằng chọn mức rủi ro trung bình là khôn ngoan, trong khi đó là vùng dễ chết nhất khi khủng hoảng xảy ra."
    },
    {
        "id": "TH-MODE-OP-06",
        "concept": "Mạng lưới Đa ngành Latticework (Charlie Munger)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Quy trình kích hoạt hiệu ứng cộng hưởng Lollapalooza Synthesis đòi hỏi người ra quyết định phải làm gì?",
        "options": [
            "A. Đặt vấn đề vào ma trận giao thoa của ít nhất 3 lăng kính khoa học cơ bản độc lập (như Vật lý, Sinh học, Tâm lý) để tìm điểm hội tụ lực.",
            "B. Chỉ đọc sách của một chuyên gia duy nhất và làm theo đúng từng bước của chuyên gia đó.",
            "C. Tập hợp ý kiến của các nhân viên và lấy điểm trung bình cộng để hòa giải xung đột.",
            "D. Áp dụng máy móc mô hình kinh tế học vào tất cả các mối quan hệ tình cảm và gia đình."
        ],
        "correct_index": 0,
        "explanation": "Hiệu ứng Lollapalooza xảy ra khi 3-4 quy luật tự nhiên cùng tác động theo một hướng, tạo ra lực đẩy cực đại vượt xa tổng của các yếu tố riêng lẻ.",
        "trap_analysis": "Bẫy suy nghĩ đơn ngành (Silo Thinking): Giải thích một hiện tượng xã hội phức tạp chỉ bằng lăng kính tài chính hoặc kỹ thuật thuần túy."
    },
    {
        "id": "TH-MODE-OP-07",
        "concept": "Thực nghiệm Nhanh (Iterative Lean Thinking)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Trong vòng lặp Thực nghiệm nhanh (Build - Measure - Learn), thứ cần được tạo ra (Build) đầu tiên là gì?",
        "options": [
            "A. Một Thử nghiệm vi mô (MVP) nhỏ nhất, rẻ nhất để kiểm chứng giả định nguy hiểm nhất (Leap-of-Faith Assumption).",
            "B. Một sản phẩm hoàn thiện 100% với giao diện sang trọng để bán cho khách hàng lớn.",
            "C. Một chiến dịch marketing rầm rộ trên toàn quốc trước khi phát triển sản phẩm.",
            "D. Một bản kế hoạch tài chính dày 200 trang dự báo chính xác doanh thu 5 năm tới."
        ],
        "correct_index": 0,
        "explanation": "MVP không phải là sản phẩm lỗi; MVP là công cụ học hỏi nhanh nhất với ít tài nguyên nhất để trả lời câu hỏi: 'Khách hàng có thực sự cần thứ này không?'.",
        "trap_analysis": "Bẫy hoàn hảo hóa sản phẩm trong phòng kín: Bỏ hàng tỷ đồng làm sản phẩm mà không thèm kiểm chứng nhu cầu thị trường."
    },
    {
        "id": "TH-MODE-OP-08",
        "concept": "Lý thuyết Trò chơi & Ma trận Động lực (Game Theory & Incentives)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Quy tắc 'Một người cắt bánh, người kia chọn trước' (Cut-and-Choose) trong Thiết kế cơ chế minh họa cho nguyên tắc nào?",
        "options": [
            "A. Động lực tự điều chỉnh: Người tạo ra luật phải chịu trực tiếp hệ quả của luật đó (Skin in the Game), buộc họ phải hành xử công bằng tuyệt đối.",
            "B. Kẻ cầm dao luôn có quyền chiếm phần bánh lớn hơn.",
            "C. Cần phải có một trọng tài đứng giữa cân đo từng miligram bánh để chia đều.",
            "D. Không nên chia bánh mà nên cất vào tủ lạnh để tránh tranh chấp."
        ],
        "correct_index": 0,
        "explanation": "Cơ chế thông minh là cơ chế không cần công an hay thanh tra giám sát; chính cấu trúc luật chơi khiến mọi tác nhân tự động hành động vì lợi ích chung.",
        "trap_analysis": "Bẫy trông đợi lòng trung thực: Xây dựng quy chế dựa trên giả định mọi người đều là thiên thần mà không có ràng buộc quyền lợi."
    },
    {
        "id": "TH-MODE-OP-09",
        "concept": "Đa quy mô Thời gian (Multi-Scale Time Horizons — Jeff Bezos)",
        "angle": "operation",
        "angle_label": "⚡ Quy trình & Kích hoạt vận hành",
        "question": "Kỹ thuật 10-10-10 của Suzy Welch dùng để rèn luyện Tư duy Đa quy mô thời gian như thế nào?",
        "options": [
            "A. Đặt câu hỏi: Quyết định này sẽ tác động đến tôi như thế nào sau 10 phút, sau 10 tháng, và sau 10 năm?",
            "B. Mỗi ngày dành đúng 10 phút để lên kế hoạch cho 10 tháng tiếp theo.",
            "C. Chia mục tiêu cuộc đời thành 10 phần và hoàn thành trong 10 năm.",
            "D. Thay đổi công việc sau mỗi 10 tháng để trải nghiệm nhiều môi trường khác nhau."
        ],
        "correct_index": 0,
        "explanation": "Kỹ thuật 10-10-10 giúp tách biệt cảm xúc ngắn hạn (10 phút) khỏi hệ quả bền vững lâu dài (10 năm), giúp bạn không hy sinh tương lai vì sự dễ chịu hôm nay.",
        "trap_analysis": "Bẫy thiển cận: Bị chi phối bởi sự bốc đồng trong 10 phút đầu mà hủy hoại thành quả 10 năm gầy dựng."
    },
    # --- 9 CÂU HỎI BẪY TƯ DUY ĐỐI NGHỊCH (INVERSION TRAPS & ANTI-PATTERNS) ---
    {
        "id": "TH-MODE-TR-01",
        "concept": "First Principles (Tư duy Nguyên bản)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Cạm bẫy 'Tối ưu hóa cục bộ' (Local Optimization Trap) vi phạm Tư duy Nguyên bản như thế nào?",
        "options": [
            "A. Cố gắng làm tốt hơn một quy trình/bước công việc mà đáng lẽ ra nó hoàn toàn không nên tồn tại ngay từ đầu.",
            "B. Cắt giảm chi phí nguyên vật liệu đầu vào quá mức khiến chất lượng giảm sút.",
            "C. Đổi mới công nghệ quá nhanh khiến nhân viên không kịp thích ứng.",
            "D. Không tham khảo ý kiến của khách hàng trung thành trước khi nâng cấp sản phẩm."
        ],
        "correct_index": 0,
        "explanation": "Elon Musk chỉ ra sai lầm phổ biến nhất của kỹ sư là: Tối ưu hóa một bộ phận mà lẽ ra phải xóa bỏ hoàn toàn bộ phận đó.",
        "trap_analysis": "Bẫy yêu thích giải pháp cũ: Cố gắng đánh bóng chiếc xe ngựa thay vì phát minh ra ô tô."
    },
    {
        "id": "TH-MODE-TR-02",
        "concept": "Tư duy Xác suất & Cập nhật Bayes (Probabilistic & Bayesian)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Bẫy Thờ ơ tỷ lệ nền (Base Rate Neglect) khiến người ra quyết định mắc sai lầm gì?",
        "options": [
            "A. Quá tin vào một câu chuyện khởi nghiệp thành công cá biệt hào nhoáng mà phớt lờ thực tế 90% các công ty khởi nghiệp trong ngành đều thất bại.",
            "B. Không chịu vay vốn ngân hàng khi lãi suất đang ở mức thấp kỷ lục.",
            "C. Phân tích quá nhiều số liệu thống kê trong quá khứ dẫn đến chậm trễ hành động.",
            "D. Luôn chọn các cổ phiếu có giá trị vốn hóa lớn nhất thị trường."
        ],
        "correct_index": 0,
        "explanation": "Tỷ lệ nền (Base Rate) là lực hút trọng trường của xác suất. Nếu bạn tham gia một cuộc chơi có tỷ lệ thất bại nền là 95%, bạn cần bằng chứng phi thường để tin mình là ngoại lệ.",
        "trap_analysis": "Bẫy ảo tưởng bản thân đặc biệt: Tin rằng nhiệt huyết cá nhân có thể đánh bại quy luật thống kê khách quan."
    },
    {
        "id": "TH-MODE-TR-03",
        "concept": "Tư duy Đảo ngược (Inversion — Charlie Munger)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Bẫy Ngụy biện người sống sót (Survivorship Bias) làm sai lệch nhận thức như thế nào nếu thiếu Tư duy Đảo ngược?",
        "options": [
            "A. Chỉ nghiên cứu những kẻ chiến thắng và ngộ nhận đó là công thức thành công, trong khi bỏ qua 'nghĩa địa' của những người đã làm y hệt nhưng đã thất bại.",
            "B. Luôn chuẩn bị phương án dự phòng quá kỹ lưỡng làm mất đi tính quyết đoán.",
            "C. Không chịu lắng nghe lời khuyên của những người đã vượt qua nghịch cảnh.",
            "D. Đầu tư vào các doanh nghiệp đã có bề dày lịch sử hoạt động trên 50 năm."
        ],
        "correct_index": 0,
        "explanation": "Nghiên cứu nghĩa địa thất bại (Inversion) luôn mang lại nhiều bài học giá trị và chân thật hơn là đọc những cuốn hồi ký hào nhoáng của người sống sót.",
        "trap_analysis": "Bẫy hào quang chiến thắng: Học thói quen bỏ học của Steve Jobs hay Bill Gates mà quên mất hàng triệu người bỏ học khác đã lâm vào cảnh bế tắc."
    },
    {
        "id": "TH-MODE-TR-04",
        "concept": "Tư duy Bậc hai (Second-Order Thinking — Howard Marks)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Hiện tượng 'Hiệu ứng Rắn hổ mang' (Cobra Effect) là ví dụ kinh điển của việc thiếu tư duy bậc hai, nó mô tả điều gì?",
        "options": [
            "A. Giải pháp bậc một tạo ra động lực sai lầm khiến vấn đề sau đó còn trở nên tồi tệ hơn nhiều so với trước khi can thiệp (chính quyền trả tiền diệt rắn dẫn đến việc người dân thi nhau nuôi rắn).",
            "B. Rắn hổ mang thích nghi với các loại thuốc độc mới và sinh sôi nảy nở nhanh hơn.",
            "C. Giá rắn hổ mang trên thị trường tăng cao khiến chính quyền bị thâm hụt ngân sách.",
            "D. Người dân không chịu giao nộp rắn vì sợ bị chính quyền xử phạt."
        ],
        "correct_index": 0,
        "explanation": "Tư duy bậc một ngây thơ nghĩ rằng treo thưởng diệt rắn thì rắn sẽ hết. Tư duy bậc hai thấy ngay phản ứng của con người: Họ sẽ nuôi rắn để lấy tiền thưởng!",
        "trap_analysis": "Bẫy chính sách ngây thơ: Can thiệp vào hệ thống phức hợp bằng giải pháp tuyến tính thô bạo."
    },
    {
        "id": "TH-MODE-TR-05",
        "concept": "Tư duy Tùy chọn & Bất đối xứng (Optionality & Barbell — Nassim Taleb)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Cạm bẫy 'Vùng giữa chết chóc' (The Murky Middle) trong đầu tư và sự nghiệp là gì?",
        "options": [
            "A. Chọn các vị thế có rủi ro vừa phải nhưng trần lợi nhuận bị giới hạn — vừa đủ bấp bênh để mất sạch tài sản khi có khủng hoảng, nhưng lại không có tiềm năng tăng trưởng đột phá.",
            "B. Đầu tư toàn bộ tiền vào vàng miếng và bất động sản thổ cư ven đô.",
            "C. Tham gia vào các công ty khởi nghiệp mạo hiểm giai đoạn đầu với số vốn nhỏ.",
            "D. Gửi tiết kiệm ngân hàng nhà nước để nhận lãi suất ổn định hàng năm."
        ],
        "correct_index": 0,
        "explanation": "Vùng giữa là nơi tồi tệ nhất của phổ rủi ro. Bạn nhận lấy rủi ro tiềm ẩn của một cuộc chơi lớn nhưng lại chỉ nhận về phần thưởng còm cõi của một cuộc chơi nhỏ.",
        "trap_analysis": "Bẫy trung dung sai lầm: Đánh đồng sự thỏa hiệp ở giữa với sự cân bằng thông thái."
    },
    {
        "id": "TH-MODE-TR-06",
        "concept": "Mạng lưới Đa ngành Latticework (Charlie Munger)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Hội chứng 'Người cầm búa' (Man with a Hammer Syndrome) phá hủy chất lượng quyết định như thế nào?",
        "options": [
            "A. Khi bạn chỉ có duy nhất một cây búa trong tay (một chuyên môn hạn hẹp), bạn sẽ nhìn mọi vấn đề trong cuộc đời đều giống như một chiếc đinh và bóp méo thực tế để dùng búa đập.",
            "B. Bạn từ chối nâng cấp dụng cụ làm việc mới vì tiếc tiền mua sắm trang thiết bị.",
            "C. Bạn làm việc quá chăm chỉ bằng sức mạnh cơ bắp thay vì dùng trí tuệ.",
            "D. Bạn dành quá nhiều thời gian để sửa chữa các lỗi nhỏ không quan trọng."
        ],
        "correct_index": 0,
        "explanation": "Bác sĩ phẫu thuật thì muốn mổ, luật sư thì muốn kiện, lập trình viên thì muốn viết app. Mạng lưới Munger giúp bạn nhìn sự việc đúng như bản chất của nó, không qua lăng kính nghề nghiệp.",
        "trap_analysis": "Bẫy ngạo mạn chuyên gia: Tin rằng thành công trong một lĩnh vực hẹp cho phép mình phán xét mọi vấn đề khác của thế giới."
    },
    {
        "id": "TH-MODE-TR-07",
        "concept": "Thực nghiệm Nhanh (Iterative Lean Thinking)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Cạm bẫy 'Chi phí chìm' (Sunk Cost Fallacy) bóp nghẹt Tư duy Thực nghiệm Nhanh như thế nào?",
        "options": [
            "A. Tiếp tục đổ thêm tiền bạc, công sức và thời gian vào một dự án thất bại chỉ vì tiếc nuối những nguồn lực đã trót đầu tư trong quá khứ mà không thể lấy lại.",
            "B. Bán tháo toàn bộ máy móc nhà xưởng khi dự án vừa mới bắt đầu có lãi.",
            "C. Cắt giảm chi phí nghiên cứu và phát triển (R&D) trong giai đoạn khó khăn.",
            "D. Không tính toán chi phí vận hành biến đổi khi mở rộng quy mô kinh doanh."
        ],
        "correct_index": 0,
        "explanation": "Trong tư duy Lean, tiền đã mất là đã mất. Quyết định của ngày hôm nay chỉ được dựa trên triển vọng giá trị trong tương lai, hoàn toàn không dựa trên chi phí quá khứ.",
        "trap_analysis": "Bẫy sĩ diện cá nhân: Sợ thừa nhận mình đã sai nên tiếp tục ném tiền tốt vào chỗ tiền xấu."
    },
    {
        "id": "TH-MODE-TR-08",
        "concept": "Lý thuyết Trò chơi & Ma trận Động lực (Game Theory & Incentives)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Cạm bẫy 'Thưởng cho việc A nhưng kỳ vọng việc B' (Folly of Rewarding A While Hoping for B) thể hiện lỗi thiết kế nào?",
        "options": [
            "A. Doanh nghiệp thưởng cho nhân viên dựa trên khối lượng công việc ngắn hạn nhưng lại hy vọng họ cống hiến cho chất lượng và sự phát triển dài hạn.",
            "B. Doanh nghiệp trả lương quá cao so với mặt bằng chung của thị trường lao động.",
            "C. Doanh nghiệp không công khai bảng lương thưởng cho toàn thể nhân viên.",
            "D. Doanh nghiệp thay đổi chỉ số đánh giá hiệu quả công việc (KPI) hàng tuần."
        ],
        "correct_index": 0,
        "explanation": "Charlie Munger từng nói: 'Nếu bạn bảo tôi động lực ở đâu, tôi sẽ chỉ cho bạn kết quả ở đó'. Con người sẽ luôn tối ưu hóa chỉ số mà họ được trả tiền để làm.",
        "trap_analysis": "Bẫy kỳ vọng viển vông: Dùng khẩu hiệu đạo đức để thay thế cho một cấu trúc cơ chế khen thưởng méo mó."
    },
    {
        "id": "TH-MODE-TR-09",
        "concept": "Đa quy mô Thời gian (Multi-Scale Time Horizons — Jeff Bezos)",
        "angle": "trap",
        "angle_label": "⚠️ Bẫy tư duy đối nghịch",
        "question": "Hiện tượng 'Chiết khấu quá mức tương lai' (Hyperbolic Discounting) khiến con người đưa ra những quyết định tai hại nào?",
        "options": [
            "A. Đánh giá quá cao niềm vui hoặc sự thỏa mãn nhỏ trước mắt (Dopamine tức thì) và xem nhẹ cái giá khủng khiếp phải trả trong tương lai 5-10 năm tới.",
            "B. Lên kế hoạch quá xa khiến bản thân rơi vào trạng thái lo âu và căng thẳng kéo dài.",
            "C. Tiết kiệm quá nhiều tiền cho tuổi già mà không chịu chi tiêu cho hiện tại.",
            "D. Đầu tư vào các dự án hạ tầng lớn có thời gian thu hồi vốn trên 20 năm."
        ],
        "correct_index": 0,
        "explanation": "Bộ não tiến hóa của loài vượn người được lập trình để tìm kiếm thức ăn ngay lập tức. Giới tinh hoa chiến thắng nhờ khả năng trì hoãn sự thỏa mãn (Delayed Gratification).",
        "trap_analysis": "Bẫy dopamine ngắn hạn: Đánh đổi sức khỏe, danh tiếng và sự giàu có dài hạn lấy vài giây thỏa mãn tức thời."
    }
]


THEORY_MODELS_QUIZ = [
    {
        "id": "TH-MOD-01",
        "model_id": "PHYS-01",
        "model_name": "Đòn bẩy (Leverage)",
        "pillar": "Vật lý học",
        "tier": 1,
        "question": "Về mặt lý thuyết bản chất, 4 loại đòn bẩy tối thượng của nền kinh tế hiện đại (Naval Ravikant) bao gồm những gì?",
        "options": [
            "A. Lao động (Labor), Vốn (Capital), Mã nguồn (Code) và Nội dung (Media) — trong đó Code và Media có chi phí cận biên bằng 0.",
            "B. Tiền vay ngân hàng, Vay nóng người thân, Bán nhà và Thế chấp tài sản.",
            "C. Nói chuyện hay, Quan hệ ngoại giao tốt, Đi nhậu giỏi và Chăm chỉ làm thêm giờ.",
            "D. Công nghệ thông tin, Bất động sản, Vàng miếng và Tiền điện tử."
        ],
        "correct_index": 0,
        "explanation": "Đòn bẩy không cần sự cho phép (Permissionless leverage) là Code và Media: bạn làm việc một lần, nhưng sản phẩm có thể nhân bản phục vụ hàng triệu người trong lúc bạn ngủ.",
        "trap_analysis": "Bẫy đòn bẩy tài chính thiếu biên độ an toàn: phóng đại lợi nhuận thì cũng phóng đại rủi ro đến mức cháy tài khoản."
    },
    {
        "id": "TH-MOD-02",
        "model_id": "PHYS-03",
        "model_name": "Entropy & Định luật 2 Nhiệt động học",
        "pillar": "Vật lý học",
        "tier": 1,
        "question": "Định luật 2 Nhiệt động học khẳng định điều gì về trạng thái mặc định của mọi hệ thống khép kín?",
        "options": [
            "A. Trong một hệ kín, mức độ hỗn loạn (Entropy) luôn có xu hướng tự nhiên tăng dần theo thời gian nếu không được nạp thêm năng lượng từ bên ngoài.",
            "B. Hệ thống kín sẽ tự động trở nên ngăn nắp và tối ưu hơn theo thời gian nhờ quy luật chọn lọc tự nhiên.",
            "C. Năng lượng trong hệ kín tự động nhân đôi sau mỗi chu kỳ nhiệt động lực học.",
            "D. Mọi vật thể trong hệ kín đều giữ nguyên trạng thái chuyển động vĩnh cửu không ma sát."
        ],
        "correct_index": 0,
        "explanation": "Sự thoái hóa, bừa bộn, lười biếng và rạn nứt là mặc định tự nhiên của vũ trụ. Muốn giữ trật tự và hiệu suất cao, bạn bắt buộc phải chủ động bơm năng lượng kỷ luật mỗi ngày.",
        "trap_analysis": "Ảo tưởng ổn định vĩnh cửu: Tin rằng doanh nghiệp hay hôn nhân một khi đã tốt thì sẽ tự duy trì mà không cần bảo trì, chăm sóc."
    },
    {
        "id": "TH-MOD-03",
        "model_id": "BIOL-01",
        "model_name": "Tiến hóa & Chọn lọc Tự nhiên",
        "pillar": "Sinh học",
        "tier": 1,
        "question": "Theo thuyết tiến hóa hiện đại của Darwin, điều kiện quyết định sự sống còn của một thực thể trong môi trường biến động là gì?",
        "options": [
            "A. Khả năng thích nghi nhanh nhất với sự thay đổi của môi trường (Fitness), không phải kẻ to lớn nhất hay thông minh nhất.",
            "B. Sức mạnh cơ bắp tuyệt đối và khả năng tiêu diệt toàn bộ các cá thể xung quanh.",
            "C. Chỉ số thông minh IQ bẩm sinh cao nhất trong bầy đàn.",
            "D. Sở hữu lượng dự trữ mỡ và năng lượng nhiều nhất trong cơ thể."
        ],
        "correct_index": 0,
        "explanation": "Fitness (sự tương thích) đo lường mức độ khớp giữa thực thể và môi trường. Kẻ khổng lồ nhưng xơ cứng (như khủng long) sẽ tuyệt chủng khi môi trường biến đổi.",
        "trap_analysis": "Bẫy tối ưu hóa cục bộ quá mức: Trở nên quá hoàn hảo cho môi trường cũ đến mức mất khả năng xoay trục khi môi trường mới xuất hiện."
    },
    {
        "id": "TH-MOD-04",
        "model_id": "PSYC-01",
        "model_name": "Thiên kiến Xác nhận (Confirmation Bias)",
        "pillar": "Tâm lý học",
        "tier": 1,
        "question": "Cơ chế tâm lý sâu xa nào khiến con người mắc Thiên kiến Xác nhận (Confirmation Bias)?",
        "options": [
            "A. Bộ não muốn bảo vệ cái tôi (Ego) và tiết kiệm năng lượng nhận thức bằng cách chỉ lọc lấy thông tin củng cố niềm tin có sẵn và gạt bỏ bằng chứng phản bác.",
            "B. Do thị lực mắt người bị hạn chế không nhìn rõ toàn bộ các chữ cái trên báo chí.",
            "C. Do con người bị ảnh hưởng bởi từ trường của Trái Đất vào những ngày trăng tròn.",
            "D. Vì các công ty truyền thông cố tình không xuất bản các thông tin trái chiều."
        ],
        "correct_index": 0,
        "explanation": "Não người ghét cảm giác 'mình đã sai' (Cognitive Dissonance). Giới tinh hoa khắc phục bằng cách chủ động săn lùng các luận điểm phản bác mạnh nhất đối với niềm tin của mình.",
        "trap_analysis": "Biến niềm tin thành danh dự: Càng tranh cãi càng lún sâu vào sai lầm vì không phân biệt được bản thân mình với ý kiến của mình."
    },
    {
        "id": "TH-MOD-05",
        "model_id": "MATH-04",
        "model_name": "Giá trị Kỳ vọng & Tiêu chuẩn Kelly (Kelly Criterion)",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "question": "Mục tiêu toán học tối thượng của Công thức Tiêu chuẩn Kelly (f* = (bp - q) / b) là gì?",
        "options": [
            "A. Tối đa hóa tốc độ tăng trưởng vốn hình học dài hạn đồng thời triệt tiêu hoàn toàn xác suất bị phá sản (Ruin Risk).",
            "B. Giúp người chơi thắng được 100% trong mọi ván cược hoặc thương vụ đầu tư.",
            "C. Tính toán chính xác thời điểm đỉnh và đáy của thị trường chứng khoán.",
            "D. Chia đều tiền cược vào tất cả các cửa có sẵn trên bàn cờ."
        ],
        "correct_index": 0,
        "explanation": "Kelly Criterion chỉ ra rằng: Có lợi thế (Edge) chưa đủ, quản trị quy mô vị thế (Position Sizing) mới là thứ quyết định bạn trở thành tỷ phú hay kẻ phá sản.",
        "trap_analysis": "Cược quá tay (Over-betting): Dù xác suất thắng là 90%, nếu bạn all-in 100% tài sản, chuỗi thua lỗ bất ngờ sẽ đưa tài sản của bạn về 0 vĩnh viễn."
    }
]

THEORY_PRINCIPLES_QUIZ = [
    {
        "id": "TH-PRIN-01",
        "principle_name": "Nguyên lý Chuyển dịch Cân bằng Le Chatelier",
        "domain": "Hóa học & Khoa học Vật liệu",
        "question": "Định nghĩa lý thuyết hình thức của Nguyên lý Le Chatelier là gì?",
        "options": [
            "A. Khi một hệ thống đang ở trạng thái cân bằng chịu một tác động bên ngoài làm thay đổi nhiệt độ, áp suất hoặc nồng độ, hệ thống sẽ tự dịch chuyển theo hướng chống lại tác động đó.",
            "B. Mọi phản ứng hóa học đều xảy ra với tốc độ không đổi bất kể nhiệt độ hay áp suất.",
            "C. Tổng khối lượng các chất tham gia phản ứng luôn lớn hơn tổng khối lượng các sản phẩm tạo thành.",
            "D. Năng lượng tỏa ra trong một phản ứng luôn bằng năng lượng hấp thụ của môi trường xung quanh."
        ],
        "correct_index": 0,
        "explanation": "Hệ thống tự nhiên luôn tìm kiếm trạng thái cân bằng nội môi. Mọi nỗ lực cưỡng bức thay đổi quá đột ngột sẽ kích hoạt phản lực đề kháng tự nhiên của hệ thống.",
        "trap_analysis": "Điều kiện biên: Hệ thống phải là hệ kín và đang ở trạng thái cân bằng động thuận nghịch."
    },
    {
        "id": "TH-PRIN-02",
        "principle_name": "Nguyên lý Chất Xúc tác (Catalysis)",
        "domain": "Hóa học & Khoa học Vật liệu",
        "question": "Cơ chế khoa học mà qua đó Chất xúc tác làm tăng tốc độ phản ứng là gì?",
        "options": [
            "A. Tạo ra một lộ trình phản ứng mới có năng lượng hoạt hóa (Activation Energy - E_a) thấp hơn mà không bị tiêu hao sau phản ứng.",
            "B. Tăng nhiệt độ của toàn bộ hệ thống lên gấp 10 lần trong tích tắc.",
            "C. Biến phản ứng thu nhiệt thành phản ứng tỏa nhiệt vĩnh cửu.",
            "D. Thay đổi vị trí cân bằng nhiệt động học cuối cùng của các chất tham gia."
        ],
        "correct_index": 0,
        "explanation": "Chất xúc tác không làm thay đổi điểm cân bằng nhiệt động học cuối cùng, nó chỉ hạ thấp bức tường cản trở ban đầu giúp phản ứng đạt đích nhanh hơn.",
        "trap_analysis": "Phép thử bác bỏ (Falsification): Nếu một chất làm thay đổi hằng số cân bằng K_eq của phản ứng thì chất đó là chất tham gia phản ứng, không phải chất xúc tác."
    },
    {
        "id": "TH-PRIN-03",
        "principle_name": "Nguyên lý Bất định Heisenberg (Uncertainty Principle)",
        "domain": "Vật lý học",
        "question": "Hệ thức Bất định Heisenberg (Δx × Δp ≥ h / 4π) khẳng định giới hạn cơ bản nào của tự nhiên?",
        "options": [
            "A. Không thể xác định đồng thời cả vị trí và động lượng của một hạt hạ nguyên tử với độ chính xác tuyệt đối; hành động đo lường làm thay đổi trạng thái của hạt.",
            "B. Vận tốc của ánh sáng trong chân không là một đại lượng hoàn toàn không thể đo đạc được.",
            "C. Thời gian trôi đi với tốc độ khác nhau tùy thuộc vào cảm xúc vui hay buồn của người quan sát.",
            "D. Mọi hạt vật chất đều có thể biến thành năng lượng nguyên tử ở nhiệt độ phòng."
        ],
        "correct_index": 0,
        "explanation": "Bất định Heisenberg là đặc tính bản chất của cơ học lượng tử, không phải do dụng cụ đo bị lỗi. Trong xã hội học, nó tương đương với Định luật Goodhart (khi một thước đo trở thành mục tiêu quản trị, nó lập tức mất giá trị đo).",
        "trap_analysis": "Hiểu sai: Nghĩ rằng đây chỉ là sự bất lực tạm thời của công nghệ đo lường hiện tại."
    }
]


def get_theory_questions_for_modes(angle: str = "all") -> List[Dict[str, Any]]:
    """
    Trả về bộ trắc nghiệm lý thuyết toàn diện cho 9 Chế độ Tư duy (27 câu hỏi chuyên sâu):
    - angle in ['all', 'concept', 'operation', 'trap']
    - 3 góc độ: Bản chất & Định nghĩa (9 câu), Quy trình & Vận hành (9 câu), Bẫy tư duy đối nghịch (9 câu).
    """
    if angle == "concept":
        return [q for q in THEORY_MODES_QUIZ if q.get("angle") == "concept"]
    elif angle == "operation":
        return [q for q in THEORY_MODES_QUIZ if q.get("angle") == "operation"]
    elif angle == "trap":
        return [q for q in THEORY_MODES_QUIZ if q.get("angle") == "trap"]
    return THEORY_MODES_QUIZ


def get_theory_questions_for_models(
    pillar: Optional[str] = None,
    tier: Optional[int] = None,
    angle: str = "all",
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Sinh và tổng hợp danh sách câu hỏi trắc nghiệm lý thuyết đa chiều cho 88 Mô hình Hạt nhân:
    - angle in ['all', 'first_principle', 'leverage', 'inversion', 'matrix']
    - 4 góc độ khảo sát: Chân lý gốc, Đòn bẩy tối thượng, Bẫy đảo ngược, và Ma trận nhận diện tương hỗ.
    - Đầy đủ 88 mô hình x 4 góc độ = tối đa 352 câu hỏi lý thuyết đa chiều!
    """
    all_models = get_all_models()
    filtered = filter_models(all_models, pillar=pillar, tier=tier)
    
    results = []
    base_seed = seed or 42
    
    for m in filtered:
        other_models = [om for om in all_models if om.get("id") != m.get("id")]
        if len(other_models) < 3:
            continue
            
        m_id = m.get("id", "0")
        seed_val = base_seed + sum(ord(c) for c in m_id)
        
        # 1. GÓC ĐỘ 1: CHÂN LÝ GỐC (FIRST PRINCIPLE)
        if angle in ("all", "first_principle"):
            rng_fp = random.Random(seed_val + 101)
            distractors = rng_fp.sample(other_models, 3)
            raw_options = [
                (m.get("first_principle"), True),
                (distractors[0].get("first_principle"), False),
                (distractors[1].get("first_principle"), False),
                (distractors[2].get("first_principle"), False),
            ]
            rng_fp.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-M-{m_id}-FP",
                "model_id": m_id,
                "model_name": f"{m.get('name_vi')} ({m.get('name_en')})",
                "pillar": m.get("pillar"),
                "tier": m.get("tier"),
                "angle": "first_principle",
                "angle_label": "🔬 Chân lý gốc (First Principle)",
                "question": f"Về mặt lý thuyết bản chất, Chân lý gốc (First Principle) của mô hình '{m.get('name_vi')}' là gì?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Chân lý gốc của {m.get('name_vi')}: {m.get('first_principle')}. Câu hỏi kích hoạt: {m.get('trigger_question')}",
                "trap_analysis": f"Bẫy đảo ngược (Inversion Trap) cần né tránh: {m.get('inversion_trap')}"
            })
            
        # 2. GÓC ĐỘ 2: ĐÒN BẨY TỐI THƯỢNG (ELITE LEVERAGE)
        if angle in ("all", "leverage"):
            rng_lev = random.Random(seed_val + 202)
            distractors = rng_lev.sample(other_models, 3)
            raw_options = [
                (m.get("elite_leverage"), True),
                (distractors[0].get("elite_leverage"), False),
                (distractors[1].get("elite_leverage"), False),
                (distractors[2].get("elite_leverage"), False),
            ]
            rng_lev.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-M-{m_id}-LEV",
                "model_id": m_id,
                "model_name": f"{m.get('name_vi')} ({m.get('name_en')})",
                "pillar": m.get("pillar"),
                "tier": m.get("tier"),
                "angle": "leverage",
                "angle_label": "⚡ Đòn bẩy tối thượng (Elite Leverage)",
                "question": f"Đòn bẩy tối thượng (Elite Leverage) của mô hình '{m.get('name_vi')}' giúp tối đa hóa kết quả với ít nguồn lực nhất như thế nào?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Đòn bẩy tối thượng của {m.get('name_vi')}: {m.get('elite_leverage')}. Cộng hưởng Lollapalooza: {', '.join(m.get('lollapalooza_pairs', []))}",
                "trap_analysis": f"Nếu lạm dụng đòn bẩy mà bỏ qua biên độ an toàn, bẫy nguy hiểm là: {m.get('inversion_trap')}"
            })
            
        # 3. GÓC ĐỘ 3: BẪY ĐẢO NGƯỢC (INVERSION TRAP)
        if angle in ("all", "inversion"):
            rng_inv = random.Random(seed_val + 303)
            distractors = rng_inv.sample(other_models, 3)
            raw_options = [
                (m.get("inversion_trap"), True),
                (distractors[0].get("inversion_trap"), False),
                (distractors[1].get("inversion_trap"), False),
                (distractors[2].get("inversion_trap"), False),
            ]
            rng_inv.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-M-{m_id}-INV",
                "model_id": m_id,
                "model_name": f"{m.get('name_vi')} ({m.get('name_en')})",
                "pillar": m.get("pillar"),
                "tier": m.get("tier"),
                "angle": "inversion",
                "angle_label": "⚠️ Bẫy đảo ngược (Inversion Trap)",
                "question": f"Bẫy đảo ngược (Inversion Trap) và cạm bẫy tư duy nguy hiểm nhất liên quan đến mô hình '{m.get('name_vi')}' là gì?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Bẫy đảo ngược của {m.get('name_vi')}: {m.get('inversion_trap')}. Chân lý gốc phòng thủ: {m.get('first_principle')}",
                "trap_analysis": f"Cách né tránh: Luôn đặt câu hỏi kích hoạt: \"{m.get('trigger_question')}\""
            })
            
        # 4. GÓC ĐỘ 4: MA TRẬN PHÂN BIỆT TƯƠNG HỖ (DISCRIMINATIVE MATRIX)
        if angle in ("all", "matrix"):
            rng_mat = random.Random(seed_val + 404)
            distractors = rng_mat.sample(other_models, 3)
            raw_options = [
                (f"{m.get('name_vi')} ({m.get('name_en')})", True),
                (f"{distractors[0].get('name_vi')} ({distractors[0].get('name_en')})", False),
                (f"{distractors[1].get('name_vi')} ({distractors[1].get('name_en')})", False),
                (f"{distractors[2].get('name_vi')} ({distractors[2].get('name_en')})", False),
            ]
            rng_mat.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-M-{m_id}-MAT",
                "model_id": m_id,
                "model_name": f"{m.get('name_vi')} ({m.get('name_en')})",
                "pillar": m.get("pillar"),
                "tier": m.get("tier"),
                "angle": "matrix",
                "angle_label": "🔀 Ma trận Phân biệt Tương hỗ (Discriminative Matrix)",
                "question": f"Đoạn chân lý gốc: \"{m.get('first_principle')}\" thuộc về Mô hình Hạt nhân nào sau đây?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Chính xác! Đó là mô hình {m.get('name_vi')}. Đòn bẩy tối thượng: {m.get('elite_leverage')}",
                "trap_analysis": f"Cần phân biệt với {distractors[0].get('name_vi')} và các mô hình cùng trụ cột {m.get('pillar')}."
            })
            
    return results


def get_theory_questions_for_principles(
    domain: Optional[str] = None,
    angle: str = "all",
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Sinh và tổng hợp danh sách câu hỏi trắc nghiệm lý thuyết đa chiều cho 100 Nguyên lý Khởi thủy:
    - angle in ['all', 'definition', 'boundary', 'falsification', 'matrix']
    - 4 góc độ khảo sát: Định nghĩa & Trực giác, Điều kiện biên, Phép thử bác bỏ (Karl Popper), và Ma trận phân biệt nguyên lý.
    - Đầy đủ 100 nguyên lý x 4 góc độ = tối đa 350-400 câu hỏi lý thuyết khoa học!
    """
    kb = load_knowledge_base()
    all_p = kb.get("principles", [])
    filtered_p = all_p
    if domain and domain != "Tất cả":
        filtered_p = [p for p in all_p if p.get("domain") == domain]
        
    results = []
    base_seed = seed or 42
    
    for p in filtered_p:
        p_name = p.get("principle_name")
        other_p = [op for op in all_p if op.get("principle_name") != p_name]
        if len(other_p) < 3:
            continue
            
        seed_val = base_seed + sum(ord(c) for c in p_name)
        
        # 1. GÓC ĐỘ 1: ĐỊNH NGHĨA HÌNH THỨC & TRỰC GIÁC
        if angle in ("all", "definition"):
            rng_def = random.Random(seed_val + 101)
            distractors = rng_def.sample(other_p, 3)
            raw_options = [
                (p.get("intuitive_summary") or p.get("description"), True),
                (distractors[0].get("intuitive_summary") or distractors[0].get("description"), False),
                (distractors[1].get("intuitive_summary") or distractors[1].get("description"), False),
                (distractors[2].get("intuitive_summary") or distractors[2].get("description"), False),
            ]
            rng_def.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-P-{seed_val}-DEF",
                "principle_name": p_name,
                "domain": p.get("domain", "Khoa học"),
                "angle": "definition",
                "angle_label": "🔬 Định nghĩa hình thức & Trực giác",
                "question": f"Về mặt bản chất khoa học, nguyên lý '{p_name}' ({p.get('domain')}) khẳng định điều gì?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Định nghĩa hình thức: {p.get('formal_definition')}. Tóm tắt trực giác: {p.get('intuitive_summary')}",
                "trap_analysis": f"Điều kiện biên: {p.get('boundary_conditions', '—')} | Khả bác: {p.get('falsification_test', '—')}"
            })

        # 2. GÓC ĐỘ 2: ĐIỀU KIỆN BIÊN NGHIỆM ĐÚNG (BOUNDARY CONDITIONS)
        if angle in ("all", "boundary") and p.get("boundary_conditions"):
            valid_distractors = [op for op in other_p if op.get("boundary_conditions")]
            if len(valid_distractors) >= 3:
                rng_bd = random.Random(seed_val + 202)
                distractors = rng_bd.sample(valid_distractors, 3)
                raw_options = [
                    (p.get("boundary_conditions"), True),
                    (distractors[0].get("boundary_conditions"), False),
                    (distractors[1].get("boundary_conditions"), False),
                    (distractors[2].get("boundary_conditions"), False),
                ]
                rng_bd.shuffle(raw_options)
                corr_idx = 0
                opts = []
                for idx, (txt, is_corr) in enumerate(raw_options):
                    opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                    if is_corr:
                        corr_idx = idx
                results.append({
                    "id": f"TH-P-{seed_val}-BD",
                    "principle_name": p_name,
                    "domain": p.get("domain", "Khoa học"),
                    "angle": "boundary",
                    "angle_label": "⚖️ Điều kiện biên nghiệm đúng (Boundary Conditions)",
                    "question": f"Điều kiện biên (Boundary Condition) để nguyên lý khoa học '{p_name}' nghiệm đúng trong thực tế là gì?",
                    "options": opts,
                    "correct_index": corr_idx,
                    "explanation": f"Điều kiện biên chuẩn xác: {p.get('boundary_conditions')}. Vượt ra ngoài ranh giới này, định luật sẽ sụp đổ.",
                    "trap_analysis": f"Định nghĩa gốc: {p.get('formal_definition')}"
                })

        # 3. GÓC ĐỘ 3: PHÉP THỬ BÁC BỎ (FALSIFICATION TEST)
        if angle in ("all", "falsification") and p.get("falsification_test"):
            valid_distractors = [op for op in other_p if op.get("falsification_test")]
            if len(valid_distractors) >= 3:
                rng_fs = random.Random(seed_val + 303)
                distractors = rng_fs.sample(valid_distractors, 3)
                raw_options = [
                    (p.get("falsification_test"), True),
                    (distractors[0].get("falsification_test"), False),
                    (distractors[1].get("falsification_test"), False),
                    (distractors[2].get("falsification_test"), False),
                ]
                rng_fs.shuffle(raw_options)
                corr_idx = 0
                opts = []
                for idx, (txt, is_corr) in enumerate(raw_options):
                    opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                    if is_corr:
                        corr_idx = idx
                results.append({
                    "id": f"TH-P-{seed_val}-FS",
                    "principle_name": p_name,
                    "domain": p.get("domain", "Khoa học"),
                    "angle": "falsification",
                    "angle_label": "💥 Phép thử bác bỏ (Karl Popper's Falsification Test)",
                    "question": f"Theo tiêu chí khả bác của Karl Popper, bằng chứng hoặc hiện tượng nào chứng minh nguyên lý '{p_name}' bị vi phạm/sai lệch nếu xuất hiện?",
                    "options": opts,
                    "correct_index": corr_idx,
                    "explanation": f"Tiêu chí bác bỏ (Falsification): {p.get('falsification_test')}. Đây là nền tảng phân biệt khoa học thực thụ với giả khoa học.",
                    "trap_analysis": f"Điều kiện biên: {p.get('boundary_conditions', '—')}"
                })

        # 4. GÓC ĐỘ 4: MA TRẬN PHÂN BIỆT NGUYÊN LÝ (DISCRIMINATIVE MATRIX)
        if angle in ("all", "matrix"):
            rng_mat = random.Random(seed_val + 404)
            distractors = rng_mat.sample(other_p, 3)
            raw_options = [
                (f"{p_name} ({p.get('domain')})", True),
                (f"{distractors[0].get('principle_name')} ({distractors[0].get('domain')})", False),
                (f"{distractors[1].get('principle_name')} ({distractors[1].get('domain')})", False),
                (f"{distractors[2].get('principle_name')} ({distractors[2].get('domain')})", False),
            ]
            rng_mat.shuffle(raw_options)
            corr_idx = 0
            opts = []
            for idx, (txt, is_corr) in enumerate(raw_options):
                opts.append(f"{['A','B','C','D'][idx]}. {txt}")
                if is_corr:
                    corr_idx = idx
            results.append({
                "id": f"TH-P-{seed_val}-MAT",
                "principle_name": p_name,
                "domain": p.get("domain", "Khoa học"),
                "angle": "matrix",
                "angle_label": "🔀 Ma trận Phân biệt Nguyên lý (Discriminative Matrix)",
                "question": f"Đoạn định nghĩa khoa học: \"{p.get('formal_definition')}\" thuộc về nguyên lý khởi thủy nào?",
                "options": opts,
                "correct_index": corr_idx,
                "explanation": f"Chính xác! Đó là {p_name}. Tóm tắt trực giác: {p.get('intuitive_summary')}",
                "trap_analysis": f"Cần phân biệt với {distractors[0].get('principle_name')} và các nguyên lý cùng phân ngành {p.get('domain')}."
            })
            
    return results


# =============================================================================
# 1. NGÂN HÀNG TRẮC NGHIỆM TÌNH HUỐNG 9 CHẾ ĐỘ TƯ DUY ELITE (CURATED)
# =============================================================================
MODES_QUIZ = [
    {
        "id": "MODE-01",
        "concept": "First Principles (Tư duy Nguyên bản)",
        "scenario": (
            "Khi SpaceX chế tạo tên lửa, các chuyên gia hàng không vũ trụ khẳng định: 'Chi phí mua tên lửa tối thiểu là 65 triệu USD "
            "vì lịch sử ngành hàng không chưa ai làm rẻ hơn được'. Elon Musk không chấp nhận điều này. Ông tra cứu bảng tuần hoàn hoá học, "
            "tính toán chi phí nguyên liệu thô (nhôm, titan, đồng, sợi carbon) chỉ chiếm 2% giá tên lửa, rồi tự hỏi: 'Làm thế nào để kết hợp "
            "các nguyên liệu này thành tên lửa với chi phí rẻ nhất?'"
        ),
        "question": "Elon Musk đã áp dụng phương pháp tư duy nào để đập tan niềm tin của toàn ngành hàng không?",
        "options": [
            "A. First Principles: Bóc tách về chân lý vật lý cơ bản nhất và suy luận ngược lên thay vì bắt chước (analogy)",
            "B. Tư duy Đảo ngược: Tìm cách làm cho tên lửa nổ tung để rút kinh nghiệm",
            "C. Lưỡi dao Occam: Chọn giải pháp đơn giản nhất là mua lại tên lửa cũ của Nga",
            "D. Tư duy Bậc hai: Dự đoán phản ứng của đối thủ Boeing trong 10 năm tới"
        ],
        "correct_index": 0,
        "explanation": (
            "First Principles đòi hỏi bạn không suy luận theo lối mòn bắt chước (Reasoning by Analogy). "
            "Hãy đập vụn bài toán xuống tận các định luật vật lý và nguyên liệu thô bất biến, rồi tái thiết kế từ số 0."
        ),
        "trap_analysis": (
            "Bẫy bắt chước (Analogy Trap) khiến 99% mọi người chấp nhận mức giá 65 triệu USD vì 'xưa nay người ta vẫn làm thế'. "
            "Chỉ có First Principles mới tạo ra đột phá chi phí giảm 10 lần."
        )
    },
    {
        "id": "MODE-02",
        "concept": "Tư duy Xác suất & Cập nhật Bayes (Probabilistic & Bayesian)",
        "scenario": (
            "Một nhà đầu tư theo dõi cổ phiếu công ty X. Ban đầu ông tin xác suất công ty tăng trưởng tốt là 70%. "
            "Tuy nhiên, báo cáo tài chính quý mới nhất cho thấy dòng tiền kinh doanh âm nặng dù doanh thu tăng ảo, "
            "và 2 giám đốc tài chính liên tiếp nộp đơn từ chức. Thay vì cố chấp giữ quan điểm cũ, nhà đầu tư lập tức hạ xác suất "
            "thành công của công ty xuống 25% và bán giảm tỷ trọng bảo vệ vốn."
        ),
        "question": "Hành vi của nhà đầu tư này thể hiện chế độ tư duy nào?",
        "options": [
            "A. Thiên kiến xác nhận: Cố tìm tin tốt để chứng minh mình mua đúng",
            "B. Cập nhật Bayes: Nhìn thế giới theo phổ xác suất và liên tục điều chỉnh niềm tin khi có dữ kiện thực nghiệm mới",
            "C. Chi phí cơ hội: So sánh cổ phiếu X với tiền gửi ngân hàng",
            "D. Tư duy Tùy chọn: Chấp nhận mất hết số tiền đã mua để đổi lấy cơ hội ăn 100 lần"
        ],
        "correct_index": 1,
        "explanation": (
            "Định lý Bayes dạy rằng: Niềm tin ban đầu (Prior) phải luôn được nhân với bằng chứng mới (Likelihood) "
            "để tạo ra xác suất thực tế mới (Posterior). Người tinh hoa không coi niềm tin là danh dự mà coi nó là xác suất cần cập nhật."
        ),
        "trap_analysis": (
            "Bẫy tâm lý phổ biến là Cố chấp & Nhất quán (Commitment Bias) — cố giữ niềm tin cũ dù thực tế đã đổi khác."
        )
    },
    {
        "id": "MODE-03",
        "concept": "Tư duy Đảo ngược (Inversion — Charlie Munger)",
        "scenario": (
            "Trước khi khởi động dự án phát triển phần mềm mới kéo dài 6 tháng, Giám đốc dự án tập hợp toàn bộ đội ngũ lại và nói: "
            "'Hãy tưởng tượng hôm nay là 6 tháng sau, và dự án này thất bại thảm hại, công ty bị kiện, toàn bộ dữ liệu bị mất. "
            "Bây giờ, từng người hãy viết ra chính xác những lý do gì đã dẫn tới thảm họa đó?'"
        ),
        "question": "Kỹ thuật quản trị rủi ro đỉnh cao này thuộc chế độ tư duy nào?",
        "options": [
            "A. Lạc quan tếu (Wishful Thinking)",
            "B. Tư duy Đảo ngược (Inversion / Premortem): Muốn thành công, trước hết phải tìm mọi cách thất bại chắc chắn rồi né tránh",
            "C. Đòn bẩy tài chính: Vay thêm vốn để bù lỗ nếu dự án hỏng",
            "D. Tư duy Hệ thống: Vẽ sơ đồ vòng lặp phản hồi âm"
        ],
        "correct_index": 1,
        "explanation": (
            "Charlie Munger có câu nói nổi tiếng: 'Invert, always invert' (Luôn luôn đảo ngược). "
            "Thường việc tìm cách tránh ngu ngốc dễ dàng và mang lại hiệu quả cao hơn nhiều so với việc cố gắng trở nên xuất chúng."
        ),
        "trap_analysis": (
            "Bẫy chỉ nhìn về phía trước (Forward-only Thinking) khiến người ta chỉ vẽ ra viễn cảnh màu hồng mà bỏ quên các lỗ thủng chết người."
        )
    },
    {
        "id": "MODE-04",
        "concept": "Tư duy Bậc hai (Second-Order Thinking — Howard Marks)",
        "scenario": (
            "Chính phủ áp dụng chính sách áp trần giá thuê nhà nhằm giúp người nghèo có nhà ở giá rẻ (Hệ quả bậc 1: Nhà thuê rẻ hơn). "
            "Tuy nhiên sau 2 năm, các chủ nhà ngừng xây mới và không bảo trì nhà cũ vì không có lãi. Nguồn cung nhà trọ sụt giảm nghiêm trọng, "
            "khiến hàng chục ngàn người nghèo hoàn toàn không tìm được chỗ thuê và phải ra đường (Hệ quả bậc 2)."
        ),
        "question": "Sai lầm của chính sách trên xuất phát từ việc thiếu chế độ tư duy nào?",
        "options": [
            "A. Tư duy Bậc hai (Second-Order Thinking): Không tự hỏi câu hỏi sống còn 'Và sau đó điều gì sẽ xảy ra tiếp theo?'",
            "B. Tư duy Bậc một: Chỉ nhìn vào tác động tích cực hiển hiện trước mắt",
            "C. Lưỡi dao Occam",
            "D. Quy luật Cung Cầu thuần túy"
        ],
        "correct_index": 0,
        "explanation": (
            "Tư duy bậc 1 đơn giản và thiển cận: 'Nếu làm A, B sẽ xảy ra (tốt)'. "
            "Tư duy bậc 2 sâu sắc và phức tạp hơn: 'Khi B xảy ra, các tác nhân sẽ phản ứng thế nào? Hệ quả của hệ quả đó trong 1–3 năm tới là gì?'"
        ),
        "trap_analysis": (
            "Hầu hết các thảm họa kinh tế và chính sách xã hội bắt nguồn từ tư duy bậc một: làm một điều có vẻ tốt tức thời nhưng hủy hoại hệ thống về lâu dài."
        )
    },
    {
        "id": "MODE-05",
        "concept": "Tư duy Tùy chọn & Bất đối xứng (Optionality & Barbell — Nassim Taleb)",
        "scenario": (
            "Một chuyên gia phần mềm ban ngày làm công việc lập trình hưởng lương ổn định, an toàn tuyệt đối và không có rủi ro phá sản. "
            "Buổi tối và cuối tuần, anh ta dành 2 giờ viết một thư viện mã nguồn mở và phát hành khóa học SaaS trực tuyến. "
            "Nếu khóa học thất bại, anh ta chỉ mất chút thời gian rảnh; nếu thành công lớn, phần mềm có thể phục vụ 100.000 khách hàng với chi phí cận biên bằng 0."
        ),
        "question": "Chiến lược phân bổ nguồn lực này là hiện thân hoàn hảo của chế độ tư duy nào?",
        "options": [
            "A. All-in đánh bạc toàn bộ tài sản vào một cơ hội duy nhất",
            "B. Chiến lược Barbell (Đòn tạ): Cực kỳ thận trọng ở 90% nguồn lực và cực kỳ mạo hiểm ở 10% cơ hội có lợi nhuận bất đối xứng dương",
            "C. Tư duy Đa quy mô thời gian thuần túy",
            "D. Bẫy Chi phí Chìm"
        ],
        "correct_index": 1,
        "explanation": (
            "Chiến lược Barbell của Nassim Taleb giúp bạn Chống Mong Manh (Antifragile): "
            "Giới hạn tối đa tổn thất khi rủi ro xảy ra, nhưng mở toang cánh cửa đón nhận lợi nhuận khổng lồ bất đối xứng (Asymmetric Upside)."
        ),
        "trap_analysis": (
            "Rất nhiều người rơi vào bẫy 'Rủi ro trung bình': Chọn một công việc vừa đủ bấp bênh, nhưng tiềm năng tăng trưởng lại bị chặn trần."
        )
    },
    {
        "id": "MODE-06",
        "concept": "Latticework Đa ngành (Munger Latticework)",
        "scenario": (
            "Khi xem xét nguyên nhân một sản phẩm mạng xã hội mới bùng nổ, một chuyên gia không chỉ dùng kinh tế học (tiếp thị, giá cả), "
            "mà kết hợp: Vật lý (Khối lượng tới hạn để tạo phản ứng dây chuyền), Sinh học (Tiến hóa thích nghi với thị hiếu người dùng), "
            "và Tâm lý học (Bằng chứng xã hội & Thiên kiến FOMO)."
        ),
        "question": "Chuyên gia này đang vận dụng phương pháp gì?",
        "options": [
            "A. Hội chứng người cầm búa (Man with a Hammer)",
            "B. Mạng lưới mô hình đa ngành (Latticework): Kết hợp lăng kính của nhiều môn khoa học cơ bản để tạo hiệu ứng cộng hưởng Lollapalooza",
            "C. Chuyên môn hóa hẹp (Silo Thinking)",
            "D. Lưỡi dao Occam"
        ],
        "correct_index": 1,
        "explanation": (
            "Thế giới thực không phân chia theo khoa học tự nhiên hay khoa học xã hội. Mọi vấn đề lớn đều là hệ thống phức hợp. "
            "Latticework giúp bạn treo mọi kinh nghiệm lên các mô hình cốt lõi liên ngành."
        ),
        "trap_analysis": (
            "Người cầm búa chỉ nhìn thấy đinh; chuyên gia một ngành duy nhất luôn bóp méo thực tế để vừa vặn với chuyên môn hạn hẹp của mình."
        )
    },
    {
        "id": "MODE-07",
        "concept": "Vòng lặp Thực nghiệm Nhanh (Iterative Loops & Lean)",
        "scenario": (
            "Thay vì bỏ 1 tỷ đồng và 1 năm để xây dựng một ứng dụng giao đồ ăn hoàn chỉnh rồi mới ra mắt thị trường, "
            "nhóm sáng lập tạo một nhóm Zalo đơn giản trong khu chung cư 500 hộ để nhận đặt món thủ công, đo lường tỷ lệ đặt lại hàng tuần, "
            "và liên tục tinh chỉnh dịch vụ sau mỗi 3 ngày."
        ),
        "question": "Phương pháp tiếp cận này thể hiện bản chất của chế độ tư duy nào?",
        "options": [
            "A. Vòng lặp Thực nghiệm Nhanh (Build - Measure - Learn): Thay giả định trừu tượng bằng thử nghiệm vi mô chi phí thấp để tiếp xúc sự thật sớm nhất",
            "B. Tư duy Bậc hai",
            "C. Đòn bẩy tài chính lớn",
            "D. Vòng tròn Năng lực cố định"
        ],
        "correct_index": 0,
        "explanation": (
            "Trong môi trường bất định, không kế hoạch trên giấy nào sống sót sau lần tiếp xúc đầu tiên với khách hàng. "
            "Tốc độ học hỏi qua các vòng lặp thực nghiệm vi mô quyết định sự sống còn."
        ),
        "trap_analysis": (
            "Bẫy Phân tích tê liệt (Analysis Paralysis): Ngồi trong phòng lạnh lập kế hoạch 5 năm mà không chịu đưa sản phẩm ra va đập thực tế."
        )
    },
    {
        "id": "MODE-08",
        "concept": "Lý thuyết Trò chơi & Động lực (Game Theory & Incentives)",
        "scenario": (
            "Một công ty muốn giảm tỷ lệ tài xế giao hàng trễ giờ. Nếu chỉ tuyên truyền đạo đức và kêu gọi trách nhiệm, kết quả không thay đổi. "
            "Nhưng khi công ty đổi cơ chế thưởng: Tài xế giao đúng giờ được cộng 15% tiền thưởng chuyến, nhưng nếu vi phạm quá 3 lần/tháng "
            "sẽ bị tạm ngưng nhận cuốc vào giờ cao điểm, tỷ lệ đúng giờ lập tức tăng lên 98%."
        ),
        "question": "Nguyên lý cốt lõi nào đã thay đổi cục diện?",
        "options": [
            "A. Quyền lực cưỡng chế",
            "B. Thiết kế động lực (Incentive Design): 'Hãy cho tôi thấy cơ chế đãi ngộ, tôi sẽ chỉ cho bạn thấy hành vi của con người' (Charlie Munger)",
            "C. Lưỡi dao Occam",
            "D. Thiên kiến sống sót"
        ],
        "correct_index": 1,
        "explanation": (
            "Con người phản ứng với các động lực (Incentives), không phải khẩu hiệu. "
            "Khi động lực được thiết kế căn chỉnh chuẩn xác (Aligned Incentives), hành vi tự giác xuất hiện mà không cần giám sát nặng nề."
        ),
        "trap_analysis": (
            "Ngây thơ tin rằng mọi người sẽ hành động vì lợi ích chung khi mà cơ chế tài chính ngầm đang khuyến khích họ làm điều ngược lại."
        )
    },
    {
        "id": "MODE-09",
        "concept": "Đa quy mô Thời gian (Multi-Scale Time Horizons — Jeff Bezos)",
        "scenario": (
            "Jeff Bezos nói với cổ đông Amazon: 'Nếu mọi việc bạn làm đòi hỏi phải có kết quả trong 3 năm, bạn sẽ phải cạnh tranh với hàng ngàn người. "
            "Nhưng nếu bạn sẵn sàng đầu tư vào một tầm nhìn 7–10 năm, bạn chỉ phải cạnh tranh với một số rất ít người, vì hầu như không ai kiên nhẫn đến thế'."
        ),
        "question": "Chế độ tư duy nào là bí quyết giúp xây dựng các tổ chức và con người vĩ đại trường tồn?",
        "options": [
            "A. Tối ưu hóa lợi nhuận quý này bằng mọi giá",
            "B. Tư duy Đa quy mô Thời gian: Hành động quyết liệt hôm nay nhưng neo giữ tầm nhìn vào những nguyên lý không thay đổi trong 10 năm tới",
            "C. Bắt chước đối thủ nhanh nhất có thể",
            "D. Thiên kiến sẵn có"
        ],
        "correct_index": 1,
        "explanation": (
            "Đa quy mô thời gian giúp giải quyết mâu thuẫn giữa hành động vi mô hàng ngày và chiến lược vĩ mô dài hạn. "
            "Lãi kép và moat lớn nhất của con người luôn nằm ở quy mô thời gian 10 năm."
        ),
        "trap_analysis": (
            "Bẫy thiển cận (Hyperbolic Discounting): Não bộ con người có xu hướng định giá quá cao phần thưởng tức thì và đánh giá quá thấp giá trị khổng lồ của tương lai xa."
        )
    }
]

# =============================================================================
# 2. NGÂN HÀNG TRẮC NGHIỆM TÌNH HUỐNG 88 MÔ HÌNH HẠT NHÂN (36 BÀI TOÁN THỰC CHIẾN ĐA TRỤ CỘT)
# =============================================================================
MODELS_QUIZ = [
    # -------------------------------------------------------------------------
    # TRỤ CỘT 1: VẬT LÝ HỌC (8 CÂU: GMM VOL 1 & VOL 2 ENRICHED)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PHYS-01",
        "model_id": "PHYS-01",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Đòn bẩy (Leverage — Archimedes & Naval Ravikant)",
        "scenario": (
            "Một lập trình viên dành 3 tháng xây dựng công cụ AI tự động phân tích báo cáo tài chính và cung cấp dưới dạng SaaS. "
            "Sau khi hoàn thiện, công cụ phục vụ đồng thời 5.000 nhà đầu tư mà anh ta không tốn thêm giờ làm việc nào, "
            "doanh thu tăng trưởng lũy tiến trong khi chi phí biên gần bằng 0."
        ),
        "question": "Loại đòn bẩy tối thượng nào của kỷ nguyên số (theo phân loại của Naval Ravikant) được khai thác ở đây?",
        "options": [
            "A. Đòn bẩy nhân sự (Labor Leverage)",
            "B. Đòn bẩy không cần cấp phép thông qua Mã nguồn & Công nghệ (Code & Software Leverage)",
            "C. Đòn bẩy nợ vay tài chính (Margin)",
            "D. Quán tính tĩnh"
        ],
        "correct_index": 1,
        "explanation": "Naval Ravikant nhấn mạnh: Code và Media là hai hình thức đòn bẩy thế hệ mới có chi phí biên bằng 0, không cần ai cấp phép và tạo ra tài sản ngay cả khi bạn đang ngủ.",
        "trap_analysis": "Bẫy đòn bẩy tài chính: Lạm dụng margin vay nợ quá mức sẽ khuếch đại rủi ro đến mức cháy sạch tài khoản khi thị trường đảo chiều nếu thiếu biên độ an toàn."
    },
    {
        "id": "Q-PHYS-02",
        "model_id": "PHYS-02",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Quán tính (Inertia — Newton's 1st Law)",
        "scenario": (
            "Một tập đoàn bán lẻ truyền thống có 15.000 nhân sự và 500 cửa hàng vật lý. Dù ban giám đốc nhận thức rõ nguy cơ bị thương mại điện tử vượt mặt, "
            "nhưng bộ máy cồng kềnh, thói quen tác nghiệp nhiều năm và hệ thống quy trình tầng tầng lớp lớp khiến tổ chức không thể xoay trục kịp thời, dần đánh mất thị phần."
        ),
        "question": "Quy luật vật lý nào phản ánh sức cản thay đổi to lớn của cỗ máy tổ chức này?",
        "options": [
            "A. Quán tính tổ chức (Corporate Inertia): Thực thể có khối lượng càng lớn thì lực cản chống lại sự thay đổi trạng thái chuyển động càng mạnh mẽ",
            "B. Định luật bảo toàn năng lượng",
            "C. Hiện tượng cộng hưởng tự do",
            "D. Lực nâng Ác-si-mét"
        ],
        "correct_index": 0,
        "explanation": "Định luật 1 Newton: Vật thể có xu hướng giữ nguyên trạng thái đứng yên hoặc chuyển động thẳng đều trừ khi có ngoại lực tác động. Cỗ máy càng đồ sộ, quán tính duy trì lối mòn cũ càng áp đảo.",
        "trap_analysis": "Ảo tưởng chỉ cần ra chỉ thị văn bản là toàn bộ tổ chức sẽ lập tức bẻ lái; thực tế cần ngoại lực tập trung cực lớn và bước chuyển thí điểm tinh gọn để phá vỡ quán tính cũ."
    },
    {
        "id": "Q-PHYS-03",
        "model_id": "PHYS-03",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Entropy & Định luật 2 Nhiệt động học (Entropy & Second Law)",
        "scenario": (
            "Một cơ sở mã nguồn (codebase) sau 6 tháng phát triển nhanh mà không dành thời gian tái cấu trúc (refactor) bắt đầu xuất hiện lỗi vặt tràn lan, "
            "hiệu năng sụt giảm và các nhà phát triển mới không thể hiểu nổi logic code, dù không một lập trình viên nào cố tình viết ẩu."
        ),
        "question": "Quy luật vũ trụ cơ bản nào chi phối sự suy thoái không thể tránh khỏi này?",
        "options": [
            "A. Nguyên lý Bất định Heisenberg",
            "B. Entropy & Định luật 2 Nhiệt động học: Trong một hệ kín, mức độ hỗn loạn luôn tự động tăng dần theo thời gian nếu không có năng lượng đầu vào có chủ đích để bảo trì trật tự",
            "C. Bảo toàn động lượng",
            "D. Chuyển pha đột ngột"
        ],
        "correct_index": 1,
        "explanation": "Entropy là trạng thái mặc định của tự nhiên: Trật tự đòi hỏi năng lượng và kỷ luật duy trì liên tục; nếu bỏ mặc, mọi hệ thống (sức khỏe, quan hệ, code, tài chính) đều tự động thoái hóa về hỗn loạn.",
        "trap_analysis": "Ảo tưởng ổn định vĩnh cửu: Tin rằng hệ thống đã chạy tốt một lần thì sẽ tự duy trì trật tự mãi mãi mà không cần các van bơm năng lượng định kỳ."
    },
    {
        "id": "Q-PHYS-04",
        "model_id": "PHYS-04",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Khối lượng Tới hạn & Phản ứng Dây chuyền (Critical Mass)",
        "scenario": (
            "Một ứng dụng gọi xe công nghệ khởi nghiệp tại một thành phố mới. Suốt 4 tháng đầu khi chỉ có 200 tài xế và 1.000 khách, hành khách phải chờ xe quá lâu và tài xế nản lòng bỏ cuộc. "
            "Nhưng khi đội ngũ dồn toàn lực khuyến mại đạt ngưỡng 2.000 tài xế và 30.000 khách thường xuyên, thời gian chờ giảm xuống dưới 3 phút và ứng dụng tự động bùng nổ người dùng mới theo cấp số nhân mà không cần trợ cấp giá nữa."
        ),
        "question": "Hiện tượng vật lý nào mô tả chính xác ngưỡng chuyển biến bùng nổ tự thân này?",
        "options": [
            "A. Lực ma sát nhớt",
            "B. Khối lượng tới hạn (Critical Mass): Mật độ tài nguyên tối thiểu cần tích lũy để kích hoạt phản ứng dây chuyền tự duy trì liên tục",
            "C. Trọng lực tĩnh",
            "D. Hiện tượng giao thoa sóng"
        ],
        "correct_index": 1,
        "explanation": "Trước khi đạt khối lượng tới hạn, mọi nỗ lực đều có vẻ không hiệu quả vì phản ứng dây chuyền chưa tự nuôi được nó; vượt qua ngưỡng tới hạn, hệ thống tự cất cánh nhờ hiệu ứng vòng lặp tích cực.",
        "trap_analysis": "Bẫy dàn trải tài nguyên: Phân bổ 10% công sức cho 10 thành phố cùng lúc khiến không thị trường nào đạt khối lượng tới hạn, dẫn đến thất bại toàn diện."
    },
    {
        "id": "Q-PHYS-08",
        "model_id": "PHYS-08",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Ma sát & Độ nhớt (Friction & Viscosity)",
        "scenario": (
            "Để giúp người dân tăng tỷ lệ tiết kiệm hưu trí, một chính phủ chuyển quy định từ 'Người lao động phải chủ động điền đơn xin tham gia' (Opt-in) "
            "sang 'Mặc định tự động trích 5% lương vào quỹ hưu trí, ai không muốn thì điền đơn xin rút' (Opt-out). Tỷ lệ tham gia ngay lập tức tăng vọt từ 36% lên 86%."
        ),
        "question": "Đòn bẩy hành vi dựa trên mô hình vật lý nào đã được áp dụng tài tình ở đây?",
        "options": [
            "A. Thao túng Ma sát (Friction Architecture): Triệt tiêu ma sát vi mô (thủ tục điền đơn) đối với hành vi có lợi và đặt ma sát đối với hành vi thoái lui",
            "B. Gia tốc trọng trường",
            "C. Bức xạ nhiệt",
            "D. Cân bằng tĩnh học"
        ],
        "correct_index": 0,
        "explanation": "Ma sát là lực cản trở dòng chảy hành động. Giảm ma sát đối với thói quen tốt xuống 0 và tăng tối đa ma sát đối với cám dỗ xấu là bí quyết định hình hành vi con người hiệu quả nhất.",
        "trap_analysis": "Triệt tiêu ma sát kiểm soát rủi ro: Loại bỏ hoàn toàn các chốt kiểm duyệt tài chính hay bảo mật để chạy theo tốc độ sẽ dẫn đến rủi ro sụp đổ hệ thống."
    },
    {
        "id": "Q-PHYS-07",
        "model_id": "PHYS-07",
        "pillar": "Vật lý học",
        "tier": 2,
        "model_name": "Chuyển pha (Phase Transition)",
        "scenario": (
            "Nước được đun từ 20 độ lên 99 độ C vẫn hoàn toàn là chất lỏng. Nhưng chỉ cần tăng thêm đúng 1 độ C (từ 99 lên 100 độ C), "
            "toàn bộ cấu trúc phân tử đột ngột biến đổi từ chất lỏng sang thể khí với thể tích nở rộng gấp 1.600 lần."
        ),
        "question": "Mô hình vật lý này giúp giải thích hiện tượng nào trong xã hội và kinh doanh?",
        "options": [
            "A. Sự biến đổi chậm chạp tích lũy về lượng đến một ngưỡng giới hạn sẽ tạo ra bước nhảy vọt đột biến về chất (Tipping Point)",
            "B. Nước luôn sôi ở mọi nhiệt độ nếu có áp suất",
            "C. Sự nguội lạnh dần của cảm xúc",
            "D. Quy luật bảo toàn khối lượng"
        ],
        "correct_index": 0,
        "explanation": "Chuyển pha chứng minh rằng những thay đổi nhỏ tiệm tiến tích lũy bên dưới bề mặt có thể bất ngờ làm thay đổi toàn bộ trạng thái của hệ thống.",
        "trap_analysis": "Nhầm lẫn giữa việc 'chưa thấy kết quả' với 'không có tiến bộ gì đang diễn ra ngầm'."
    },
    {
        "id": "Q-PHYS-10",
        "model_id": "PHYS-10",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Thí Nghiệm Tư Duy (Thought Experiment — Einstein & Galileo)",
        "scenario": (
            "Năm 16 tuổi, Albert Einstein tự đặt cho mình câu hỏi: 'Chuyện gì sẽ xảy ra nếu tôi cưỡi trên một chùm ánh sáng và cầm một chiếc gương soi mặt mình?'. "
            "Chỉ bằng việc chạy mô phỏng kịch bản cực hạn này trong tâm trí bằng suy luận logic chặt chẽ, ông đã phát minh ra Thuyết Tương đối làm đảo lộn toàn bộ vật lý cổ điển."
        ),
        "question": "Công cụ nhận thức quyền năng nào cho phép con người kiểm tra các giả thuyết cực hạn khi chưa thể thử nghiệm ngoài đời thực?",
        "options": [
            "A. Thí nghiệm tư duy (Thought Experiment): Mô phỏng các kịch bản cực hạn trong đầu bằng logic nghiêm ngặt để kiểm tra độ bền vững và phát hiện lỗ hổng của kế hoạch",
            "B. Mơ mộng hão huyền không có cơ sở",
            "C. Đo đạc thực địa bằng mắt thường",
            "D. Thu thập ý kiến thăm dò số đông"
        ],
        "correct_index": 0,
        "explanation": "Thí nghiệm tư duy (Gedankenexperiment) cho phép bạn phá vỡ rào cản chi phí và công nghệ, khám phá ra chân lý hoặc điểm chết của dự án trước khi tiêu tốn một đồng vốn nào.",
        "trap_analysis": "Dựng kịch bản trong đầu nhưng ngầm thiên vị để hợp thức hóa ý kiến cá nhân, thay vì suy diễn khách quan không khoan nhượng."
    },
    {
        "id": "Q-PHYS-11",
        "model_id": "PHYS-11",
        "pillar": "Vật lý học",
        "tier": 1,
        "model_name": "Tư Duy Nguyên Bản (First Principles Thinking — Aristotle & Elon Musk)",
        "scenario": (
            "Khi Elon Musk bắt đầu dự án chế tạo tên lửa vũ trụ SpaceX, các chuyên gia hàng không vũ trụ khẳng định giá thành tên lửa tối thiểu phải là 65 triệu USD/quả. "
            "Thay vì chấp nhận, Musk phân rã tên lửa về chi phí vật liệu thô trên sàn giao dịch kim loại (nhôm, titan, đồng, sợi carbon) và nhận ra chi phí vật liệu thực tế chỉ chiếm 2% giá chào bán, "
            "98% còn lại là chi phí trung gian và quy trình gia công lỗi thời."
        ),
        "question": "Phương pháp tư duy bóc tách tận cùng chân lý khách quan này có tên là gì?",
        "options": [
            "A. Suy luận bắt chước theo kinh nghiệm đám đông (Reasoning by Analogy)",
            "B. Tư duy Nguyên bản (First Principles Thinking): Phân rã bài toán về những chân lý vật lý và sự thật cơ bản nhất không thể suy diễn thêm, từ đó tái thiết kế giải pháp đột phá từ số 0",
            "C. Thỏa hiệp chi phí trung gian",
            "D. Tối ưu hóa tiệm tiến cục bộ"
        ],
        "correct_index": 1,
        "explanation": "Tư duy nguyên bản giúp bạn nhìn thấu bản chất vật lý của vấn đề, giải phóng bản thân khỏi các định kiến và giới hạn nhân tạo do con người tự đặt ra.",
        "trap_analysis": "Bẫy bắt chước (Analogy Trap): Coi cách người khác đang làm là giới hạn tối thượng của vũ trụ."
    },

    # -------------------------------------------------------------------------
    # TRỤ CỘT 2: SINH HỌC (7 CÂU: GMM VOL 2 ENRICHED)
    # -------------------------------------------------------------------------
    {
        "id": "Q-BIO-01",
        "model_id": "BIO-01",
        "pillar": "Sinh học",
        "tier": 1,
        "model_name": "Tiến hóa & Chọn lọc Tự nhiên (Natural Selection & Evolution — Charles Darwin)",
        "scenario": (
            "Trong cuộc khủng hoảng chuỗi cung ứng toàn cầu và biến động lãi suất dồn dập, các doanh nghiệp duy trì mô hình sản xuất cứng nhắc theo kế hoạch 5 năm cũ bị tồn kho khổng lồ và vỡ nợ; "
            "trong khi các công ty áp dụng mô hình sản xuất tinh gọn linh hoạt, liên tục tung thử nghiệm lô nhỏ và xoay trục theo thị trường lại gia tăng thị phần."
        ),
        "question": "Chân lý cốt lõi nào của học thuyết chọn lọc tự nhiên Darwin giải thích sự phân hóa sinh tồn này?",
        "options": [
            "A. Kẻ có quy mô vốn to nhất luôn luôn áp đảo kẻ nhỏ",
            "B. Không phải loài mạnh nhất hay thông minh nhất sống sót, mà là loài có khả năng thích nghi nhanh nhất với sự thay đổi của môi trường",
            "C. Chọn lọc tự nhiên chỉ diễn ra khi có thảm họa tuyệt chủng",
            "D. Sự cạnh tranh triệt tiêu hoàn toàn mọi liên minh"
        ],
        "correct_index": 1,
        "explanation": "Chọn lọc tự nhiên là bộ lọc tàn nhẫn đào thải những cấu trúc xơ cứng không ăn khớp với môi trường mới. Khả năng thích ứng qua thử nghiệm nhanh là vũ khí sinh tồn tối cao.",
        "trap_analysis": "Bẫy bảo thủ tự mãn: Tin rằng con hào kinh tế quá khứ sẽ bảo vệ doanh nghiệp mãi mãi khi khí hậu thị trường đã thay đổi hoàn toàn."
    },
    {
        "id": "Q-BIO-02",
        "model_id": "BIO-02",
        "pillar": "Sinh học",
        "tier": 1,
        "model_name": "Hốc Sinh Thái & Chuyên Biệt Hóa (Ecological Niches & Specialization — Gause's Law)",
        "scenario": (
            "Một công ty công nghệ giáo dục quy mô nhỏ không thể cạnh tranh trực diện với các tập đoàn EdTech đa năng có ngân sách marketing hàng trăm triệu USD. "
            "Thay vào đó, họ chỉ tập trung sản xuất giải pháp luyện thi chứng chỉ tài chính CFA chuyên sâu bằng tiếng Việt và chiếm trọn 80% thị phần ngách này với biên lợi nhuận ròng lên tới 45%."
        ),
        "question": "Nguyên lý sinh học nào phản ánh chiến lược định vị thông minh của công ty này?",
        "options": [
            "A. Hốc sinh thái & Nguyên lý Gause: Hai thực thể cạnh tranh trực diện cùng một nguồn thức ăn hạn chế không thể cùng tồn tại; kẻ yếu hơn phải tìm hoặc tạo ra một hốc riêng biệt để phát triển độc quyền",
            "B. Tự sao chép vô tính",
            "C. Di cư ngẫu nhiên không mục đích",
            "D. Ký sinh bắt buộc"
        ],
        "correct_index": 0,
        "explanation": "Nguyên lý loại trừ cạnh tranh của Gause khẳng định: Cạnh tranh trực diện với kẻ khổng lồ trên cùng một sân chơi là tự sát. Chiếm lĩnh một hốc hẹp và trở thành số 1 tuyệt đối trong hốc đó là con đường sinh tồn bền vững nhất.",
        "trap_analysis": "Ảo tưởng đại trà: Cố gắng làm hài lòng tất cả mọi phân khúc khách hàng, khiến năng lực bị phân tán mỏng manh và dễ dàng bị đánh bại ở mọi mặt trận."
    },
    {
        "id": "Q-BIO-03",
        "model_id": "BIO-03",
        "pillar": "Sinh học",
        "tier": 1,
        "model_name": "Cân bằng Nội môi (Homeostasis & Negative Feedback Regulation)",
        "scenario": (
            "Một nhà đầu tư cá nhân đặt quy tắc kỷ luật nghiêm ngặt: Tỷ trọng cổ phiếu trong tổng tài sản luôn được duy trì ở mức 70% và tiền mặt 30%. "
            "Khi thị trường tăng nóng đẩy tỷ trọng cổ phiếu lên 85%, hệ thống tự động bán bớt 15% chuyển về tiền mặt; khi thị trường sụt giảm làm tỷ trọng cổ phiếu rơi về 55%, anh ta dùng tiền dự phòng mua gom cổ phiếu cơ bản, tự động mua đáy bán đỉnh không hề bị cảm xúc chi phối."
        ),
        "question": "Cơ chế sinh học kỳ diệu nào của cơ thể sống đã được áp dụng vào quản trị danh mục đầu tư ở đây?",
        "options": [
            "A. Đột biến gen ngẫu nhiên",
            "B. Cân bằng nội môi (Homeostasis): Cơ chế tự động điều chỉnh thông qua các vòng phản hồi âm để duy trì các chỉ số sinh tồn ở trạng thái ổn định động bất chấp bão tố bên ngoài",
            "C. Chọn lọc giới tính",
            "D. Tháp dinh dưỡng một chiều"
        ],
        "correct_index": 1,
        "explanation": "Cân bằng nội môi giúp cơ thể giữ thân nhiệt 37°C dù nhiệt độ ngoài trời là 0°C hay 40°C. Xây dựng các van phản hồi tự động cân bằng trong tài chính giúp nhà đầu tư miễn nhiễm trước tâm lý bầy đàn tham lam và sợ hãi.",
        "trap_analysis": "Cân bằng cứng nhắc: Cố giữ nguyên trạng thái cũ đến mức ngăn cản mọi sự thay đổi và học hỏi cần thiết cho quá trình phát triển đột phá."
    },
    {
        "id": "Q-BIO-04",
        "model_id": "BIO-04",
        "pillar": "Sinh học",
        "tier": 1,
        "model_name": "Hiệu ứng Nữ hoàng Đỏ (The Red Queen Effect — Van Valen & Lewis Carroll)",
        "scenario": (
            "Một lập trình viên kỳ cựu có 10 năm kinh nghiệm xuất sắc với các ngôn ngữ truyền thống. Trong 2 năm qua, anh ta từ chối tiếp cận các công cụ hỗ trợ AI coding vì cho rằng 'không thực chất'. "
            "Kết quả là năng suất tạo sản phẩm của anh ta bị các kỹ sư trẻ mới ra trường thành thạo AI vượt qua gấp 3 lần, khiến vị thế chuyên gia của anh bị lung lay nghiêm trọng."
        ),
        "question": "Quy luật đồng tiến hóa sinh học nào mô tả tình cảnh trớ trêu của kỹ sư này?",
        "options": [
            "A. Hiệu ứng Nữ hoàng Đỏ (The Red Queen Effect): 'Bạn phải chạy hết tốc lực chỉ để giữ nguyên vị trí hiện tại' — trong một môi trường vận động tương đối, đứng yên đồng nghĩa với việc đang tụt hậu nhanh chóng",
            "B. Đồng sinh cùng loài",
            "C. Tiến hóa phân kỳ",
            "D. Cân bằng chấm dứt"
        ],
        "correct_index": 0,
        "explanation": "Trong tự nhiên, con mồi chạy nhanh hơn thì thú săn mồi cũng tiến hóa để chạy nhanh hơn. Nâng cấp năng lực liên tục không phải để trở nên siêu phàm, mà là điều kiện tối thiểu để duy trì vị thế sinh tồn trong thị trường.",
        "trap_analysis": "Bị cuốn vào cuộc đua vũ trang tiêu hao vô nghĩa với đối thủ (chạy đua giảm giá hoặc làm việc kiệt sức) mà không hề xây dựng được con hào tri thức bền vững."
    },
    {
        "id": "Q-BIO-05",
        "model_id": "BIO-05",
        "pillar": "Sinh học",
        "tier": 1,
        "model_name": "Đồng sinh & Cộng sinh (Mutualism & Symbiosis — Cooperation in Nature)",
        "scenario": (
            "Mối quan hệ giữa loài nấm Mycorrhiza và rễ cây rừng: Nấm len lỏi vào đất hấp thu khoáng chất và nước cung cấp cho cây, đổi lại cây quang hợp tạo ra đường nuôi sống nấm. "
            "Khi một cây trong rừng bị sâu bệnh tấn công, mạng lưới sợi nấm thậm chí còn truyền tín hiệu cảnh báo hóa học giúp các cây xung quanh tự sản sinh độc tố phòng vệ."
        ),
        "question": "Bài học sâu sắc nào về tư duy hợp tác trong kinh doanh và lãnh đạo được phản ánh qua mô hình này?",
        "options": [
            "A. Trò chơi có tổng bằng không (Zero-sum): Phải triệt hạ đối tác để giành lấy toàn bộ tài nguyên",
            "B. Tư duy Cộng sinh cùng thắng (Mutualism / Positive-sum): Tạo ra mạng lưới cộng sinh bền vững mà ở đó sự thành công của đối tác trực tiếp củng cố sức mạnh sinh tồn của chính mình",
            "C. Ký sinh một chiều nhằm vắt kiệt vật chủ",
            "D. Cô lập tự cung tự cấp"
        ],
        "correct_index": 1,
        "explanation": "Trong tự nhiên và xã hội loài người, các cấu trúc vĩ đại nhất đều vận hành trên sự cộng sinh đôi bên cùng có lợi (Win-Win). Xây dựng hệ sinh thái mà ở đó mọi thành viên đều hưởng lợi là cách phòng thủ vững chắc nhất.",
        "trap_analysis": "Nhầm lẫn quan hệ ký sinh với cộng sinh: Tự an ủi rằng mình đang hợp tác, trong khi thực tế đối tác chỉ đang âm thầm bòn rút tài nguyên và uy tín của bạn mà không trả lại giá trị tương xứng."
    },
    {
        "id": "Q-BIO-08",
        "model_id": "BIO-08",
        "pillar": "Sinh học",
        "tier": 2,
        "model_name": "Đột biến & Đa dạng Di truyền (Mutation & Genetic Diversity)",
        "scenario": (
            "Tập đoàn công nghệ 3M áp dụng chính sách cho phép các kỹ sư dành 15% thời gian làm việc để theo đuổi các thử nghiệm cá nhân kỳ lạ. "
            "Từ một thử nghiệm tạo ra chất keo 'dính không chặt' tưởng chừng thất bại, một kỹ sư đã phát minh ra sản phẩm Giấy ghi chú Post-it mang lại hàng tỷ USD."
        ),
        "question": "Cơ chế sinh học nào giải thích tại sao các tổ chức cần dung dưỡng các thử nghiệm sai số nhỏ?",
        "options": [
            "A. Sao chép DNA hoàn hảo 100% không cho phép sai số",
            "B. Đột biến ngẫu nhiên (Mutation): Sự sai lệch vi mô chính là nguồn nguyên liệu duy nhất tạo ra các biến dị thích nghi đột phá cho giống loài",
            "C. Tuyệt chủng hàng loạt",
            "D. Ký sinh trùng bắt buộc"
        ],
        "correct_index": 1,
        "explanation": "Nếu không có đột biến ngẫu nhiên, sự sống không bao giờ tiến hóa. Doanh nghiệp muốn đổi mới phải chủ động tạo không gian cho các thử nghiệm sai số an toàn.",
        "trap_analysis": "Áp đặt quy trình kiểm soát 100% không tì vết, triệt tiêu mọi không gian thử nghiệm khiến tổ chức chết mòn vì thiếu đột biến sáng tạo."
    },
    {
        "id": "Q-BIO-10",
        "model_id": "BIO-10",
        "pillar": "Sinh học",
        "tier": 2,
        "model_name": "Sức Tải Môi Trường (Carrying Capacity)",
        "scenario": (
            "Một hồ cá sinh thái có diện tích nuôi thả tối đa 1.000 con cá. Một người nuôi cá tham lam thả thêm 3.000 con vào hồ. "
            "Chỉ sau 2 tuần, lượng oxy hòa tan cạn kiệt, chất thải ô nhiễm quá tải khiến toàn bộ 4.000 con cá bị chết ngạt trắng bụng."
        ),
        "question": "Khái niệm sinh thái học nào đã bị vi phạm nghiêm trọng trong trường hợp này?",
        "options": [
            "A. Sức tải môi trường (Carrying Capacity): Giới hạn tối đa về quy mô mà một hệ sinh thái có thể duy trì mà không bị phá hủy hoàn toàn",
            "B. Tháp năng lượng sinh thái",
            "C. Đa dạng sinh học",
            "D. Chuỗi thức ăn tuần hoàn"
        ],
        "correct_index": 0,
        "explanation": "Bất kỳ hệ thống vật lý hay sinh thái nào cũng có trần tải giới hạn. Ép hệ thống vượt quá sức tải sẽ dẫn đến sự sụp đổ thảm họa phi tuyến tính.",
        "trap_analysis": "Cố ép doanh nghiệp tăng trưởng nóng vượt qua ngưỡng năng lực chịu đựng của đội ngũ vận hành và hạ tầng kỹ thuật."
    },
    # -------------------------------------------------------------------------
    # TRỤ CỘT 3: TÂM LÝ HỌC (6 CÂU: TIER 1 & TIER 2)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PSY-01",
        "model_id": "PSY-01",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Thiên kiến Xác nhận (Confirmation Bias)",
        "scenario": (
            "Sau khi mua một mã cổ phiếu bất động sản, nhà đầu tư chỉ tìm đọc các bài phân tích khen ngợi tiềm năng của công ty, "
            "tham gia các nhóm chat của những người cùng ôm cổ phiếu đó để tung hô nhau, và gạt bỏ mọi cảnh báo về nợ trái phiếu."
        ),
        "question": "Thiên kiến tâm lý nguy hiểm nào đang che mờ mắt nhà đầu tư này?",
        "options": [
            "A. Thiên kiến Xác nhận (Confirmation Bias): Chỉ thu nạp thông tin củng cố niềm tin có sẵn và gạt bỏ bằng chứng phản bác",
            "B. Hiệu ứng Mỏ neo",
            "C. Hiệu ứng Tương phản",
            "D. Hiệu ứng Hào quang"
        ],
        "correct_index": 0,
        "explanation": "Bộ não muốn bảo vệ sự dễ chịu của nhận thức bằng cách chỉ lọc lấy thông tin hợp ý mình. Khắc phục bằng cách chủ động tìm kiếm bằng chứng chứng minh mình sai.",
        "trap_analysis": "Confirmation bias là nguyên nhân số một dẫn tới việc gồng lỗ và phá sản trong đầu tư tài chính."
    },
    {
        "id": "Q-PSY-02",
        "model_id": "PSY-02",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Ác Cảm Mất Mát (Loss Aversion — Kahneman & Tversky)",
        "scenario": (
            "Một người được đề nghị tham gia trò chơi tung đồng xu: Ngửa thì nhận 10 triệu đồng, Sấp thì mất 10 triệu đồng. "
            "Dù kỳ vọng toán học bằng 0, đa số mọi người đều từ chối và yêu cầu: Nếu ngửa phải nhận ít nhất 20-25 triệu thì họ mới chấp nhận rủi ro mất 10 triệu."
        ),
        "question": "Quy luật tâm lý học hành vi nào giải thích sự bất đối xứng cảm xúc này?",
        "options": [
            "A. Ác cảm mất mát (Loss Aversion): Nỗi đau khi mất một khoản tiền lớn gấp 2 đến 2.5 lần niềm vui khi kiếm được chính khoản tiền đó",
            "B. Bẫy chi phí chìm",
            "C. Ảo tưởng kiểm soát",
            "D. Thiên kiến vị kỷ"
        ],
        "correct_index": 0,
        "explanation": "Não người tiến hóa để sinh tồn: Mất thức ăn đồng nghĩa với cái chết, nên nỗi sợ mất mát luôn áp đảo khao khát đạt được điều mới.",
        "trap_analysis": "Vì sợ mất mát nhỏ mà không dám cắt lỗ sớm, để rồi khoản lỗ nhỏ biến thành khoản lỗ khổng lồ hủy hoại toàn bộ tài khoản."
    },
    {
        "id": "Q-PSY-04",
        "model_id": "PSY-04",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Bằng Chứng Xã Hội (Social Proof & Bầy Đàn)",
        "scenario": (
            "Một người đi dạo trên phố tìm quán ăn. Có hai quán phở cạnh nhau: Quán A rất đông người xếp hàng tràn ra vỉa hè, "
            "Quán B bên cạnh rộng rãi, sạch sẽ nhưng không có một bóng khách nào. Người này lập tức đứng vào hàng đợi của quán A."
        ),
        "question": "Cơ chế tâm lý học tiến hóa nào đã định đoạt quyết định của người này?",
        "options": [
            "A. Đánh giá chất lượng độc lập dựa trên khẩu vị",
            "B. Bằng chứng xã hội (Social Proof): Khi ở trong trạng thái không chắc chắn, ta mặc định hành vi của đám đông là đúng đắn",
            "C. Hiệu ứng tương phản ánh sáng",
            "D. Nguyên lý khan hiếm nhân tạo"
        ],
        "correct_index": 1,
        "explanation": "Thời tiền sử, chạy theo đám đông giúp bạn thoát khỏi thú dữ mà không cần nhìn thấy nó. Thời hiện đại, đám đông thường xuyên cùng nhau lao xuống vực thẳm tài chính.",
        "trap_analysis": "Mua tài sản ở đỉnh bong bóng chỉ vì thấy tất cả bạn bè, báo chí và mạng xã hội đều đang đổ xô mua."
    },
    {
        "id": "Q-PSY-05",
        "model_id": "PSY-05",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Hiệu Ứng Lollapalooza (Charlie Munger)",
        "scenario": (
            "Trong một buổi đấu giá tranh từ thiện sôi động, một người bình thường vốn rất tiết kiệm đã bỏ ra số tiền gấp 10 lần giá trị thật. "
            "Phân tích cho thấy sự cộng hưởng cùng lúc của: Bằng chứng xã hội (đám đông hò reo), Ác cảm mất mát (sợ người khác cướp mất), "
            "Thiên kiến nhất quán (đã lỡ giơ biển 3 lần), và Men say chiến thắng."
        ),
        "question": "Charlie Munger gọi hiện tượng nhiều khuynh hướng tâm lý cùng cộng hưởng đẩy về một hướng này là gì?",
        "options": [
            "A. Hiệu ứng Mỏ neo đơn lẻ",
            "B. Hiệu ứng Lollapalooza: Sự hội tụ cộng hưởng đa chiều dẫn tới hành vi bùng nổ phi lý trí cực độ",
            "C. Thuyết tương đối xã hội",
            "D. Định luật Gresham"
        ],
        "correct_index": 1,
        "explanation": "Khi 3-4 thiên kiến tâm lý tác động cùng một lúc, chúng không cộng gộp tuyến tính mà nhân bản sức mạnh theo hàm mũ, đánh sập lý trí của con người.",
        "trap_analysis": "Coi thường sức mạnh cộng hưởng: Nghĩ rằng từng yếu tố nhỏ không đáng lo ngại mà quên mất sự hội tụ của chúng có thể tạo nên thảm họa."
    },
    {
        "id": "Q-PSY-08",
        "model_id": "PSY-08",
        "pillar": "Tâm lý học",
        "tier": 2,
        "model_name": "Thiên Kiến Sẵn Có (Availability Heuristic)",
        "scenario": (
            "Sau khi xem tin tức về một vụ rơi máy bay thảm khốc trên tivi, nhiều người lập tức hủy vé máy bay để đi tàu hỏa hoặc lái xe ô tô đường dài, "
            "mặc dù số liệu thống kê chứng minh xác suất chết vì tai nạn giao thông đường bộ cao gấp 100 lần tai nạn hàng không."
        ),
        "question": "Lỗi tư duy định lượng nào đang chi phối phản ứng này của đám đông?",
        "options": [
            "A. Phân tích xác suất Bayes khách quan",
            "B. Thiên kiến sẵn có (Availability Heuristic): Đánh giá xác suất một sự kiện xảy ra dựa trên mức độ dễ dàng hồi tưởng lại hình ảnh sống động của nó trong tâm trí",
            "C. Bỏ qua tỷ lệ nền",
            "D. Quy luật số lớn"
        ],
        "correct_index": 1,
        "explanation": "Hình ảnh càng giật gân, đẫm máu thì càng dễ nhớ, khiến não bộ lầm tưởng rằng tần suất xảy ra của nó trong thực tế là rất cao.",
        "trap_analysis": "Ra các quyết định quản trị rủi ro tốn kém chỉ để phòng ngừa những biến cố giật gân hiếm gặp, trong khi phớt lờ những rủi ro thầm lặng hàng ngày."
    },
    {
        "id": "Q-PSY-12",
        "model_id": "PSY-12",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Vòng Tròn Năng Lực (Circle of Competence — Buffett & Munger)",
        "scenario": (
            "Trong bong bóng Dot-com năm 1999, cả phố Wall chế giễu Warren Buffett là 'ông già lỗi thời' vì từ chối rót vốn vào các cổ phiếu công nghệ đang tăng giá phi mã hàng ngày. "
            "Buffett bình thản trả lời: 'Tôi không đầu tư vào những thứ mình không hiểu rõ cách họ tạo ra dòng tiền bền vững sau 10 năm nữa'. Khi bong bóng vỡ năm 2000-2001, các quỹ đầu cơ công nghệ bốc hơi 80-90% trong khi Berkshire Hathaway bình yên tăng trưởng."
        ),
        "question": "Mô hình nhận thức cốt lõi nào đã bảo vệ gia tài của Buffett trước sự cám dỗ điên cuồng của thị trường?",
        "options": [
            "A. Vòng tròn Năng lực (Circle of Competence): Biết rõ ranh giới hiểu biết thực sự của mình, kiên định ở trong vòng tròn và dứt khoát nói 'Không' với những thứ bên ngoài ranh giới đó",
            "B. Hiệu ứng bầy đàn và tâm lý FOMO",
            "C. Đòn bẩy vốn vay tài chính tối đa",
            "D. Thiên kiến xác nhận thông tin tích cực"
        ],
        "correct_index": 0,
        "explanation": "Biết những gì mình không biết quan trọng hơn việc tỏ ra thông minh. Kích thước vòng tròn năng lực không quan trọng bằng việc bạn biết chính xác chu vi ranh giới của nó.",
        "trap_analysis": "Bẫy ngạo mạn nhận thức & Kiến thức tài xế (Chauffeur Knowledge): Thành công rực rỡ trong một lĩnh vực hẹp rồi ảo tưởng mình có thể đầu tư thắng lợi ở mọi lĩnh vực khác."
    },
    {
        "id": "Q-PSY-18",
        "model_id": "PSY-18",
        "pillar": "Tâm lý học",
        "tier": 1,
        "model_name": "Dao Cạo Hanlon (Hanlon's Razor — Robert J. Hanlon)",
        "scenario": (
            "Một đối tác làm ăn lâu năm gửi nhầm tài liệu báo giá cho một khách hàng khác khiến công ty bạn bị lỡ mất một hợp đồng lớn. "
            "Người quản lý tức giận đập bàn tuyên bố: 'Hắn ta cố tình chơi xấu đâm sau lưng tôi!'. Nhưng khi điều tra thực tế, nhân viên đối tác chỉ vì phải thức trắng đêm chăm con ốm nên đã đính kèm nhầm file."
        ),
        "question": "Quy tắc nhận thức sâu sắc nào giúp chúng ta tránh được căn bệnh hoang tưởng và bảo vệ các mối quan hệ quý giá?",
        "options": [
            "A. Dao cạo Hanlon: Đừng bao giờ quy kết cho ác ý những gì có thể giải thích thỏa đáng bằng sự bất cẩn, thiếu hiểu biết, mệt mỏi hoặc sơ suất",
            "B. Luôn luôn nghi ngờ người khác để tự bảo vệ",
            "C. Cắt đứt quan hệ ngay lập tức khi đối phương mắc sai sót đầu tiên",
            "D. Thiên kiến kết quả"
        ],
        "correct_index": 0,
        "explanation": "Con người thường vụng về và bất toàn hơn là xấu xa. Áp dụng Dao cạo Hanlon giúp bạn giữ được sự bình tĩnh, giải phóng tâm trí khỏi sự hận thù và tập trung sửa chữa quy trình.",
        "trap_analysis": "Mù quáng ngây thơ bỏ qua những kẻ lừa đảo hoặc có động cơ trục lợi thật sự khi hành vi ác ý đã lặp đi lặp lại nhiều lần."
    },

    # -------------------------------------------------------------------------
    # TRỤ CỘT 4: KINH TẾ HỌC (11 CÂU: GMM VOL 4 ENRICHED)
    # -------------------------------------------------------------------------
    {
        "id": "Q-ECON-01",
        "model_id": "ECON-01",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Quy Luật Cung & Cầu (Supply and Demand)",
        "scenario": (
            "Một thợ may thủ công mất 300 giờ để hoàn thành một chiếc áo choàng bằng lông chim quý hiếm với chi phí nguyên liệu đắt đỏ. "
            "Anh ta định giá chiếc áo 500 triệu đồng. Tuy nhiên, khi rao bán suốt 2 năm, không có bất kỳ ai hỏi mua dù chỉ một lần "
            "vì thị trường không có nhu cầu về loại áo choàng này."
        ),
        "question": "Quy luật kinh tế học thị trường nào đã phủ định quan điểm định giá theo công sức của người thợ may?",
        "options": [
            "A. Định luật bảo toàn giá trị",
            "B. Quy luật Cung & Cầu (Supply & Demand): Giá cả thị trường chỉ được quyết định tại điểm cân bằng giữa lượng cung sẵn bán và lượng cầu sẵn sàng chi trả, không phụ thuộc vào chi phí công sức bỏ ra",
            "C. Độc quyền cưỡng bức",
            "D. Hiệu ứng mỏ neo"
        ],
        "correct_index": 1,
        "explanation": "Thị trường chỉ trả tiền cho những gì nó cần (Cầu) và những gì khan hiếm (Cung thấp). Dành 1.000 giờ làm việc không có cầu thì giá trị kinh tế vẫn bằng 0.",
        "trap_analysis": "Ngộ nhận chi phí công sức (Labor Fallacy): Tin rằng mình khổ cực làm việc thì xã hội bắt buộc phải đền đáp xứng đáng."
    },
    {
        "id": "Q-ECON-02",
        "model_id": "ECON-02",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Chi Phí Cơ Hội (Opportunity Cost)",
        "scenario": (
            "Một người trẻ nhận được lời mời làm việc với mức lương 15 triệu/tháng tại một cơ quan nhà nước nhàn rỗi, không có cơ hội thăng tiến hay học kỹ năng mới. "
            "Cùng lúc, anh có cơ hội làm trợ lý cho một CEO công nghệ xuất chúng với mức trợ cấp chỉ 8 triệu/tháng nhưng được trực tiếp học hỏi cách xây dựng doanh nghiệp toàn cầu. "
            "Người trẻ quyết định chọn công việc 15 triệu vì 'lương cao hơn 7 triệu'."
        ),
        "question": "Khái niệm kinh tế học nào vạch trần sai lầm tính toán thiển cận của người trẻ này?",
        "options": [
            "A. Chi phí chìm",
            "B. Chi phí Cơ hội (Opportunity Cost): Chi phí thực sự của việc chọn công việc nhàn rỗi chính là toàn bộ mạng lưới quan hệ, kỹ năng tinh hoa và tiềm năng thu nhập hàng trăm triệu trong tương lai bị đánh mất",
            "C. Lợi thế kinh tế quy mô",
            "D. Tỷ lệ đòn bẩy"
        ],
        "correct_index": 1,
        "explanation": "Chi phí cơ hội đo lường giá trị của phương án tốt nhất bị bỏ qua. Nhận thêm 7 triệu ngắn hạn nhưng đánh mất cơ hội trưởng thành vượt bậc là thương vụ lỗ nặng nề nhất đời người.",
        "trap_analysis": "Chỉ nhìn vào tiền mặt cầm tay trước mắt mà mù tịt trước những chi phí vô hình và tiềm năng tăng trưởng bị xóa sổ vĩnh viễn."
    },
    {
        "id": "Q-ECON-03",
        "model_id": "ECON-03",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Lợi Thế Kinh Tế Nhờ Quy Mô (Economies of Scale)",
        "scenario": (
            "Tập đoàn bán lẻ Costco mua hàng triệu sản phẩm trực tiếp từ nhà máy để hưởng chiết khấu số lượng tối đa, giúp giá thành đầu vào rẻ hơn 30% so với siêu thị nhỏ. "
            "Thay vì tăng giá để kiếm lợi nhuận tức thì, Costco giới hạn biên lợi nhuận ròng dưới 14% và bán giá rẻ nhất thị trường cho hội viên, khiến đối thủ cạnh tranh hoàn toàn không thể bắt chước."
        ),
        "question": "Mô hình kinh tế học kết hợp chiến lược chia sẻ quy mô (Scale Economics Shared) này tạo ra lợi thế gì?",
        "options": [
            "A. Chi phí biên tiệm cận vô cùng",
            "B. Lợi thế Kinh tế nhờ Quy mô (Economies of Scale): Chi phí cố định trên mỗi đơn vị giảm dần khi sản lượng bùng nổ, tạo thành bức tường phòng thủ chi phí thấp bất khả xâm phạm",
            "C. Độc quyền cưỡng chế của nhà nước",
            "D. Lạm phát chi phí đẩy"
        ],
        "correct_index": 1,
        "explanation": "Quy mô càng lớn, giá thành càng rẻ; giá càng rẻ thu hút càng nhiều khách; nhiều khách lại làm quy mô to hơn nữa. Đây là con hào kinh tế bền vững nhất thời đại công nghiệp.",
        "trap_analysis": "Nhầm lẫn giữa quy mô to và hiệu quả: Bộ máy phình to nếu sinh ra quan liêu và trì trệ sẽ rơi vào Bất lợi quy mô (Diseconomies of Scale)."
    },
    {
        "id": "Q-ECON-04",
        "model_id": "ECON-04",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Hiệu Ứng Mạng Lưới (Network Effects — Metcalfe's Law)",
        "scenario": (
            "Một ứng dụng nhắn tin mới ra mắt có giao diện đẹp hơn và bảo mật cao hơn Zalo, nhưng người dùng cài thử rồi xóa ngay "
            "vì bạn bè, đối tác và gia đình của họ đều đang ở trên Zalo. Ứng dụng mới không thể lôi kéo được thị phần."
        ),
        "question": "Con hào kinh tế bất khả xâm phạm nào đang bảo vệ vị thế của Zalo?",
        "options": [
            "A. Chi phí sản xuất rẻ hơn",
            "B. Hiệu ứng Mạng lưới (Network Effects): Giá trị của mạng lưới tăng theo cấp số nhân với mỗi người dùng mới gia nhập (Định luật Metcalfe: $V \\sim n^2$)",
            "C. Đòn bẩy vốn nhà nước",
            "D. Bản quyền sở hữu trí tuệ"
        ],
        "correct_index": 1,
        "explanation": "Sản phẩm tốt hơn chưa chắc thắng sản phẩm có mạng lưới người dùng lớn hơn. Mỗi mắt xích mới làm tăng giá trị cho toàn bộ các mắt xích còn lại.",
        "trap_analysis": "Đầu tư vào sản phẩm chỉ chăm chăm làm tính năng mà không thiết kế cơ chế tạo ra hiệu ứng mạng lưới tự tích lũy."
    },
    {
        "id": "Q-ECON-05",
        "model_id": "ECON-05",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Lợi Thế So Sánh & Chuyên Môn Hóa (Comparative Advantage — David Ricardo)",
        "scenario": (
            "Một CEO công nghệ xuất chúng có khả năng gõ bàn phím và nhập liệu nhanh gấp đôi cô trợ lý, dọn dẹp văn phòng sạch hơn lao công. "
            "Tuy nhiên, vị CEO không bao giờ tự gõ hợp đồng hay tự dọn văn phòng; anh ta ủy quyền toàn bộ để dành 100% thời gian nghiên cứu sản phẩm và gặp gỡ đối tác chiến lược."
        ),
        "question": "Định luật kinh tế học vĩ đại nào của David Ricardo chứng minh hành động của vị CEO là hoàn toàn tối ưu?",
        "options": [
            "A. Lợi thế Tuyệt đối (Absolute Advantage)",
            "B. Lợi thế So sánh (Comparative Advantage): Tập trung vào công việc có chi phí cơ hội thấp nhất và tạo giá trị gia tăng tương đối cao nhất, ủy quyền các việc còn lại",
            "C. Quy luật giá trị thặng dư",
            "D. Cân bằng tiền tệ"
        ],
        "correct_index": 1,
        "explanation": "Dù bạn giỏi hơn người khác ở mọi việc (lợi thế tuyệt đối), bạn vẫn phải ủy quyền việc bạn ít giỏi nhất để tối đa hóa tổng sản lượng thông qua chuyên môn hóa.",
        "trap_analysis": "Bệnh ôm đồm của người giỏi: Nghĩ rằng 'mình làm tốt hơn người khác thì mình nên tự làm hết', tự giam cầm bản thân trong các tác vụ giá trị thấp."
    },
    {
        "id": "Q-ECON-06",
        "model_id": "ECON-06",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Phá Hủy Sáng Tạo (Creative Destruction — Joseph Schumpeter)",
        "scenario": (
            "Năm 2007, Steve Jobs ra mắt chiếc iPhone màn hình cảm ứng điện dung tích hợp máy nghe nhạc iPod và trình duyệt internet, "
            "dù biết rõ hành động này sẽ tự 'ăn thịt' và khai tử dòng máy nghe nhạc iPod đang mang về hàng tỷ USD doanh thu cho Apple."
        ),
        "question": "Nguyên lý kinh tế học cốt lõi nào của Joseph Schumpeter giải thích hành động dũng cảm này của Apple?",
        "options": [
            "A. Cạnh tranh độc quyền tĩnh",
            "B. Phá hủy Sáng tạo (Creative Destruction): Chủ động tự phá hủy sản phẩm cũ của chính mình bằng một sản phẩm đột phá ưu việt hơn trước khi bị đối thủ tiêu diệt",
            "C. Bẫy thanh khoản",
            "D. Lợi thế người đi sau"
        ],
        "correct_index": 1,
        "explanation": "Chủ nghĩa tư bản vận động không ngừng bằng cách phá hủy các cấu trúc cũ để tạo ra trật tự mới. Nếu bạn không dám tự phá hủy mô hình của mình, thị trường sẽ làm điều đó cho bạn.",
        "trap_analysis": "Thảm kịch bảo thủ của Kodak: Phát minh ra máy ảnh số đầu tiên nhưng giấu đi vì sợ mất doanh thu bán phim nhựa truyền thống, dẫn đến phá sản."
    },
    {
        "id": "Q-ECON-07",
        "model_id": "ECON-07",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Con Hào Kinh Tế & Rào Cản Gia Nhập (Economic Moats — Warren Buffett)",
        "scenario": (
            "Một công ty sản xuất phần mềm kế toán doanh nghiệp có hàng triệu công ty sử dụng. Dù có đối thủ mới ra mắt phần mềm rẻ hơn 50%, "
            "hầu hết khách hàng vẫn kiên quyết không đổi phần mềm vì chi phí rủi ro sai sót dữ liệu, đào tạo lại toàn bộ nhân sự kế toán là quá khủng khiếp."
        ),
        "question": "Loại con hào kinh tế nào của Warren Buffett đang bảo vệ doanh nghiệp này?",
        "options": [
            "A. Chi phí Chuyển đổi cao (High Switching Costs): Khách hàng bị khóa chặt vào hệ sinh thái vì chi phí và rủi ro chuyển đổi sang đối thủ vượt xa lợi ích giảm giá",
            "B. Độc quyền do nhà nước bảo hộ",
            "C. Bán phá giá có trợ cấp",
            "D. Rào cản địa lý tự nhiên"
        ],
        "correct_index": 0,
        "explanation": "Con hào kinh tế là khả năng duy trì lợi nhuận cao dài hạn trước sự tấn công của đối thủ. Chi phí chuyển đổi cao là một trong những con hào bền vững nhất.",
        "trap_analysis": "Nhầm lẫn doanh thu lớn với con hào kinh tế: Doanh nghiệp không có con hào phòng thủ sẽ bị đối thủ bào mòn lợi nhuận về 0 ngay khi thị trường bão hòa."
    },
    {
        "id": "Q-ECON-08",
        "model_id": "ECON-08",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Hiệu Dụng Biên Giảm Dần (Diminishing Marginal Utility)",
        "scenario": (
            "Một người đi bộ khát khô cổ giữa sa mạc sẵn sàng trả 10 triệu đồng cho chai nước lọc đầu tiên (thỏa mãn cực hạn). "
            "Khi uống đến chai thứ hai, anh ta chỉ sẵn lòng trả 50.000 đồng; đến chai thứ tư anh ta từ chối uống dù được cho miễn phí vì bụng đã căng tròn."
        ),
        "question": "Quy luật tâm lý và kinh tế học hành vi nào điều khiển sự sụt giảm mức độ thỏa mãn này?",
        "options": [
            "A. Lạm phát tiền tệ",
            "B. Hiệu dụng Biên Giảm dần (Diminishing Marginal Utility): Mức độ thỏa mãn tăng thêm thu được từ mỗi đơn vị tiêu thụ bổ sung sẽ giảm dần theo thời gian",
            "C. Đòn bẩy tâm lý",
            "D. Điểm uốn công nghệ"
        ],
        "correct_index": 1,
        "explanation": "Quy luật này nhắc nhở con người về điểm bão hòa: Càng tiêu thụ nhiều cùng một thứ, giá trị cận biên càng tiến về 0. Biết đủ và đa dạng hóa trải nghiệm là chìa khóa hạnh phúc.",
        "trap_analysis": "Bẫy cày cuốc kiệt quệ: Ngồi làm việc thêm từ tiếng thứ 12 đến tiếng thứ 15 khi não đã kiệt sức; hiệu dụng biên của 3 tiếng này bằng 0 hoặc gây ra lỗi sai tai hại."
    },
    {
        "id": "Q-ECON-09",
        "model_id": "ECON-09",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Bi Kịch Của Của Chung (Tragedy of the Commons — Hardin & Ostrom)",
        "scenario": (
            "Một đồng cỏ chung của làng mở cửa tự do cho tất cả các hộ dân thả bò. Mỗi hộ nông dân vì muốn tối đa hóa lợi nhuận riêng đã mua thêm nhiều bò về thả. "
            "Chỉ sau 6 tháng, đồng cỏ bị giẫm đạp trơ trụi đất cát, cỏ không kịp mọc lại khiến toàn bộ đàn bò của cả làng cùng chết đói."
        ),
        "question": "Mô hình kinh tế học cảnh báo về sự hủy hoại tài nguyên tự do này có tên là gì?",
        "options": [
            "A. Bi kịch của Của chung (Tragedy of the Commons): Khi tài nguyên không có quyền sở hữu rõ ràng, hành vi duy lý cá nhân ngắn hạn sẽ dẫn đến thảm họa cho cả tập thể",
            "B. Cân bằng tiền tệ mở",
            "C. Lợi thế so sánh tập thể",
            "D. Thị trường cạnh tranh hoàn hảo"
        ],
        "correct_index": 0,
        "explanation": "Khi tài sản là của chung không ai sở hữu trực tiếp, không ai có động lực bảo trì mà chỉ có động lực bòn rút tối đa. Giải pháp là tư nhân hóa hoặc thiết lập quy chế chế tài minh bạch.",
        "trap_analysis": "Cơ chế 'cha chung không ai khóc': Trong một tổ chức, nhiệm vụ nào được giao chung cho cả phòng mà không chỉ định một người chịu trách nhiệm duy nhất (DRI) thì chắc chắn bị bỏ bê."
    },
    {
        "id": "Q-ECON-10",
        "model_id": "ECON-10",
        "pillar": "Kinh tế học",
        "tier": 1,
        "model_name": "Lý Thuyết Trò Chơi & Cân Bằng Nash (Game Theory & Nash Equilibrium)",
        "scenario": (
            "Hai hãng hàng không cùng bay trên một tuyến đường. Cả hai đều biết nếu cùng giữ giá vé 2 triệu đồng thì cả hai đều có lãi lớn. "
            "Nhưng vì sợ đối thủ giảm giá cướp khách, hãng A hạ giá xuống 1.5 triệu; hãng B lập tức hạ giá xuống 1.2 triệu để trả đũa. "
            "Kết quả là cả hai hãng cùng rơi vào thua lỗ nặng nề nhưng không bên nào dám đơn phương tăng giá trở lại."
        ),
        "question": "Trạng thái kẹt cứng chiến lược tồi tệ này trong Lý thuyết Trò chơi được gọi là gì?",
        "options": [
            "A. Tối ưu hóa Pareto",
            "B. Cân bằng Nash trong Thế tiến thoái lưỡng nan của tù nhân (Prisoner's Dilemma): Không bên nào có động lực đơn phương thay đổi chiến lược vì sợ bị đối phương hạ gục",
            "C. Độc quyền nhóm liên minh",
            "D. Lợi thế người đi đầu"
        ],
        "correct_index": 1,
        "explanation": "Cân bằng Nash giải thích tại sao hai bên hoàn toàn duy lý lại có thể đưa nhau đến một kết cục bi thảm. Muốn thoát bẫy phải thay đổi luật chơi hoặc xây dựng cam kết hợp tác lặp lại.",
        "trap_analysis": "Bị cuốn vào trò chơi có tổng bằng không (Zero-sum) và cuộc đua xuống đáy (Race to the bottom) mà không nhận ra cả ngành đang cùng nhau tự sát."
    },
    {
        "id": "Q-ECON-11",
        "model_id": "ECON-11",
        "pillar": "Kinh tế học",
        "tier": 2,
        "model_name": "Bất Cân Xứng Thông Tin & Thị Trường Xe Cũ (Akerlof's Market for Lemons)",
        "scenario": (
            "Trên thị trường xe ô tô cũ, người bán biết chính xác xe có bị ngập nước hay tai nạn không, nhưng người mua thì không thể biết được. "
            "Vì sợ mua phải xe hỏng (xe quả chanh), người mua chỉ đồng ý trả mức giá trung bình thấp. Kết quả là những người có xe tốt thực sự rút khỏi thị trường, "
            "chỉ còn lại xe nát được đem bán."
        ),
        "question": "Hiện tượng thị trường bị hủy hoại do thiếu minh bạch thông tin được kinh tế học gọi là gì?",
        "options": [
            "A. Lựa chọn Bất lợi (Adverse Selection) do Bất cân xứng thông tin (Information Asymmetry)",
            "B. Cạnh tranh hoàn hảo",
            "C. Cân bằng tiền tệ",
            "D. Phân bổ hiệu quả Pareto"
        ],
        "correct_index": 0,
        "explanation": "Khi một bên nắm nhiều thông tin hơn bên kia, hàng kém chất lượng sẽ đánh bạt hàng tốt ra khỏi thị trường nếu thiếu cơ chế bảo hành hoặc kiểm định độc lập.",
        "trap_analysis": "Trong bất kỳ cuộc đàm phán hay đầu tư nào: nếu bạn không biết đối phương đang nắm lợi thế thông tin gì, bạn chính là bên chịu lựa chọn bất lợi."
    },
    # -------------------------------------------------------------------------
    # TRỤ CỘT 5: TOÁN HỌC & XÁC SUẤT (8 CÂU: GMM VOL 1 & VOL 3 ENRICHED)
    # -------------------------------------------------------------------------
    {
        "id": "Q-MATH-01",
        "model_id": "MATH-01",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Lãi Kép (Compounding — Kỳ quan thứ 8)",
        "scenario": (
            "Hai người bạn cùng bắt đầu sự nghiệp ở tuổi 20: Người A đầu tư 50 triệu/năm với lãi suất 12%/năm từ năm 20 đến 30 tuổi (tổng nộp 500 triệu) rồi ngừng không nạp thêm. "
            "Người B đợi đến năm 30 tuổi mới bắt đầu đầu tư 50 triệu/năm liên tục suốt 30 năm từ 30 đến 60 tuổi (tổng nộp 1.5 tỷ đồng). "
            "Đến tuổi 60, tài sản của Người A lại lớn hơn Người B gấp bội."
        ),
        "question": "Yếu tố toán học nào đóng vai trò khuếch đại uy lực nhất trong công thức lãi kép $A = P(1+r)^t$?",
        "options": [
            "A. Số vốn ban đầu $P$",
            "B. Thời gian tích lũy $t$ nằm ở số mũ của hàm số",
            "C. Việc chọn ngân hàng giao dịch",
            "D. May mắn ngắn hạn"
        ],
        "correct_index": 1,
        "explanation": "Lãi kép là sự tích lũy theo hàm mũ. 99% tài sản của Warren Buffett được tạo ra sau sinh nhật lần thứ 50 của ông nhờ giữ vốn chạy qua số mũ thời gian.",
        "trap_analysis": "Ngắt quãng chu kỳ lãi kép: Nhảy qua nhảy lại giữa các phương pháp đầu tư hoặc rút vốn chi tiêu trước khi đường cong hàm mũ cất cánh."
    },
    {
        "id": "Q-MATH-02",
        "model_id": "MATH-02",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Định Luật Lũy Thừa & Pareto 80/20 (Power Law)",
        "scenario": (
            "Phân tích doanh thu của một công ty cho thấy: trong số 100 sản phẩm đang bán, chỉ có 20 sản phẩm mang lại 80% tổng lợi nhuận ròng. "
            "80 sản phẩm còn lại làm tiêu tốn 80% thời gian hỗ trợ khách hàng, kho bãi và vận hành nhưng chỉ đem về 20% lợi nhuận."
        ),
        "question": "Mô hình phân phối toán học nào giải thích hiện tượng phân bổ bất đối xứng này?",
        "options": [
            "A. Phân phối Chuẩn hình chuông Gauss",
            "B. Định luật Lũy thừa & Nguyên lý Pareto 80/20: Mối quan hệ bất đối xứng sâu sắc giữa đầu vào và đầu ra",
            "C. Hồi quy về trung bình",
            "D. Nghịch lý Simpson"
        ],
        "correct_index": 1,
        "explanation": "Thế giới hiện đại bị thống trị bởi phân phối lũy thừa. 20% nguyên nhân tạo ra 80% kết quả. Giới tinh hoa tập trung tối đa nguồn lực vào 20% hạt nhân này.",
        "trap_analysis": "Dàn trải nguồn lực cào bằng: Đối xử bình đẳng với mọi công việc, dẫn đến cạn kiệt năng lượng mà không tạo ra đột phá."
    },
    {
        "id": "Q-MATH-03",
        "model_id": "MATH-03",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Xác Suất Bayes & Tỷ Lệ Nền (Base Rate)",
        "scenario": (
            "Một căn bệnh hiếm gặp có tỷ lệ mắc trong cộng đồng là 1/1.000 (0.1%). "
            "Một que xét nghiệm có độ chính xác 99%. Một người đi xét nghiệm ngẫu nhiên và nhận kết quả 'Dương tính'. "
            "Bác sĩ nói với người đó rằng: 'Xác suất bạn thực sự bị bệnh chỉ khoảng 9%, đừng quá hoảng sợ'."
        ),
        "question": "Tại sao xác suất mắc bệnh thật chỉ là 9% chứ không phải 99% như độ chính xác của que thử?",
        "options": [
            "A. Vì que thử bị hết hạn sử dụng",
            "B. Do Bỏ quên Tỷ lệ nền (Base Rate): Vì tỷ lệ người không mắc bệnh quá lớn (99.9%), 1% dương tính giả của nhóm người khỏe mạnh vẫn áp đảo số ca bệnh thật",
            "C. Vì bác sĩ tính nhầm toán",
            "D. Vì virus tự biến mất trong máu"
        ],
        "correct_index": 1,
        "explanation": "Khi tỷ lệ nền cực thấp, số ca dương tính giả sẽ lấn át số ca dương tính thật. Không bao giờ đánh giá một tín hiệu mà quên đi tỷ lệ nền của tổng thể.",
        "trap_analysis": "Bẫy thờ ơ tỷ lệ nền (Base Rate Fallacy): Tin vào các lời hứa hẹn làm giàu siêu tốc mà quên rằng tỷ lệ thành công nền chỉ là 1 phần vạn."
    },
    {
        "id": "Q-MATH-04",
        "model_id": "MATH-04",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Giá Trị Kỳ Vọng & Tiêu Chuẩn Kelly (Expected Value & Kelly Criterion)",
        "scenario": (
            "Một nhà đầu tư phân tích một cơ hội: Xác suất cổ phiếu tăng giá 60% mang lại lợi nhuận 40% (p = 0.6, b = 0.4); xác suất giảm giá là 40% với mức lỗ 20% (q = 0.4). "
            "Tính toán cho thấy giá trị kỳ vọng (EV) dương. Tuy nhiên, anh ta băn khoăn nên phân bổ bao nhiêu phần trăm danh mục để vừa tăng trưởng tối đa vừa không có nguy cơ cháy tài khoản."
        ),
        "question": "Công thức toán học nào giải quyết chính xác bài toán quy mô vị thế tối ưu này?",
        "options": [
            "A. Cược tất tay (All-in 100%) vì EV dương",
            "B. Tiêu chuẩn Kelly (Kelly Criterion): Xác định tỷ lệ vốn tối ưu $f^* = \frac{bp - q}{b}$ để tối đa hóa tốc độ tăng trưởng logarit dài hạn",
            "C. Chia đều tài sản thành 100 phần bằng nhau",
            "D. Gấp đôi tiền cược sau mỗi lần thua (Martingale)"
        ],
        "correct_index": 1,
        "explanation": "Tiêu chuẩn Kelly chứng minh rằng cược quá ít thì bỏ lỡ cơ hội, nhưng cược quá mức Kelly (Over-betting) chắc chắn sẽ dẫn đến phá sản dài hạn do chuỗi rủi ro liên tiếp.",
        "trap_analysis": "Bẫy cược quá tay: Đánh đồng việc có EV dương với việc được phép cược toàn bộ tài sản; một cú sảy chân sẽ xóa sổ toàn bộ vốn liếng."
    },
    {
        "id": "Q-MATH-05",
        "model_id": "MATH-05",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Tư Duy Đảo Ngược (Inversion Thinking — Jacobi & Munger)",
        "scenario": (
            "Nhà toán học Đức Carl Jacobi có câu châm ngôn kinh điển: 'Đảo ngược, luôn luôn đảo ngược' (Man muss immer umkehren). "
            "Khi Charlie Munger được hỏi làm thế nào để có một cuộc đời thành công và hạnh phúc, ông không tìm kiếm những bí quyết phi thường, mà trả lời: "
            "'Tất cả những gì tôi muốn biết là tôi sẽ chết ở đâu, để tôi không bao giờ đến đó. Hãy tìm xem điều gì chắc chắn sẽ làm cuộc đời bạn đau khổ, tàn tạ và thất bại thảm hại nhất — rồi sau đó kiên quyết né tránh chúng suốt đời'."
        ),
        "question": "Bản chất toán học và tư duy đòn bẩy của phương pháp Tư duy Đảo ngược (Inversion) là gì?",
        "options": [
            "A. Lập kế hoạch chi tiết từng bước theo chiều xuôi từ hiện tại đến tương lai",
            "B. Tư duy Đảo ngược (Inversion): Thay vì chỉ tìm cách thành công, hãy xác định mọi nguyên nhân gây ra thất bại thảm khốc và thiết kế các chốt chặn triệt tiêu chúng trước tiên",
            "C. Đợi chờ vận may ngẫu nhiên từ thị trường",
            "D. Bắt chước hành vi của người giàu nhất"
        ],
        "correct_index": 1,
        "explanation": "Tránh né sự ngu ngốc và các thảm họa chết người dễ dàng hơn và mang lại kết quả bền vững hơn nhiều so với việc cố gắng trở nên xuất chúng phi thường.",
        "trap_analysis": "Chỉ mải mê vẽ viễn cảnh thắng lợi (Upside) mà hoàn toàn mù tịt trước các cạm bẫy hủy diệt (Downside risk) có thể xóa sổ toàn bộ cơ đồ."
    },
    {
        "id": "Q-MATH-06",
        "model_id": "MATH-06",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Hồi Quy Về Giá Trị Trung Bình (Regression to the Mean)",
        "scenario": (
            "Một cầu thủ bóng đá vừa có một mùa giải thăng hoa rực rỡ với số bàn thắng gấp 3 lần mức trung bình sự nghiệp nhờ hàng loạt pha dứt điểm may mắn trúng cột dọc bay vào lưới. "
            "Câu lạc bộ vội vàng ký hợp đồng 5 năm với mức lương kỷ lục. Mùa giải tiếp theo, số bàn thắng của anh ta quay trở lại đúng mức trung bình của 5 năm trước."
        ),
        "question": "Quy luật thống kê nào chi phối hiện tượng phong độ quay về mức nền tảng này?",
        "options": [
            "A. Quy luật triệt tiêu năng lượng",
            "B. Hồi quy về giá trị trung bình (Regression to the Mean): Các biến cố cực đoan do yếu tố may mắn ngẫu nhiên đóng góp sẽ có xu hướng tự nhiên quay trở về gần giá trị trung bình tổng thể trong các lần quan sát tiếp theo",
            "C. Hiệu ứng mỏ neo",
            "D. Thuyết tương đối"
        ],
        "correct_index": 1,
        "explanation": "Phong độ cực đoan là sự kết hợp của năng lực thực tế và may mắn đột biến. Theo thời gian, may mắn sẽ cân bằng lại và kết quả sẽ hội tụ về đường trung bình.",
        "trap_analysis": "Nhầm lẫn giữa phong độ nhất thời do may mắn với đẳng cấp nội tại bền vững; mua đỉnh tài sản vì tưởng thành tích đột biến sẽ kéo dài mãi mãi."
    },
    {
        "id": "Q-MATH-07",
        "model_id": "MATH-07",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Phân Phối Chuẩn vs Đuôi Béo (Normal vs Fat-Tailed Distributions)",
        "scenario": (
            "Một quỹ phòng hộ phố Wall kiếm được lợi nhuận đều đặn 1.5% mỗi tháng suốt 5 năm bằng chiến lược bán quyền chọn (nhặt tiền lẻ trước đầu xe lu). "
            "Đến năm thứ 6, một cuộc khủng hoảng tài chính bất ngờ xảy ra chỉ trong 3 ngày đã xóa sạch toàn bộ vốn liếng và đẩy quỹ vào cảnh phá sản nợ nần."
        ),
        "question": "Nassim Taleb dùng mô hình toán học nào để cảnh báo về các thảm họa này?",
        "options": [
            "A. Phân phối Chuẩn hình chuông Gauss",
            "B. Phân phối Đuôi béo (Fat-Tailed Distribution / Extremistan): Các biến cố cực đoan hiếm gặp có tác động hủy diệt vượt ngoài mọi mô hình tính toán rủi ro truyền thống",
            "C. Luật bù trừ số học",
            "D. Cực tiểu toàn cục"
        ],
        "correct_index": 1,
        "explanation": "Trong môi trường đuôi béo, 1 ngày duy nhất có thể xóa sổ thành quả của 10 năm. Không bao giờ chơi trò chơi mà trong đó một thất bại có thể tiêu diệt bạn hoàn toàn.",
        "trap_analysis": "Dùng mô hình phân phối chuẩn (Gaussian) vốn chỉ đúng cho chiều cao/cân nặng để tính toán rủi ro tài chính và thị trường."
    },
    {
        "id": "Q-MATH-10",
        "model_id": "MATH-10",
        "pillar": "Toán học & Xác suất",
        "tier": 1,
        "model_name": "Tính Phi Công Thái Học & Nhân Với Số 0 (Non-Ergodicity & Multiplying by Zero)",
        "scenario": (
            "Một người chơi trò Cò quay Nga (Russian Roulette) với khẩu súng lục có 6 ổ đạn và 1 viên đạn. Mỗi lần bóp cò thoát chết, anh ta nhận được 10 tỷ đồng. "
            "Xét theo trung bình nhóm 6 người chơi, kỳ vọng tiền thưởng là cực lớn. Nhưng nếu một cá nhân chơi liên tục 6 lần qua thời gian, xác suất sống sót rơi tự do về 0."
        ),
        "question": "Thuộc tính toán học sâu sắc nào giải thích tại sao mức trung bình nhóm không áp dụng được cho cuộc đời một cá nhân?",
        "options": [
            "A. Tính đối xứng hoàn hảo",
            "B. Tính Phi công thái học (Non-Ergodicity): Xác suất trung bình của tập hợp không bằng xác suất của cá nhân theo chuỗi thời gian khi hệ thống có điểm chết/hấp thụ (Absorbing Barrier / Ruin)",
            "C. Luật số lớn thuần nhất",
            "D. Phân phối Poisson"
        ],
        "correct_index": 1,
        "explanation": "Đời người là Non-ergodic. Mọi số lớn nhân với 0 đều bằng 0. Nếu bạn chết hoặc phá sản ở bước 10, bạn không bao giờ được tham gia tiếp bước 11 dù xác suất tương lai có đẹp đến đâu.",
        "trap_analysis": "Đánh cược mạng sống, tự do hay danh dự vào những thương vụ có rủi ro tuyệt chủng chỉ vì bị mờ mắt bởi tỷ lệ lợi nhuận kỳ vọng cao."
    },

    # -------------------------------------------------------------------------
    # TRỤ CỘT 6: KỸ THUẬT & HỆ THỐNG (9 CÂU: GMM VOL 1 & VOL 3 ENRICHED)
    # -------------------------------------------------------------------------
    {
        "id": "Q-SYS-01",
        "model_id": "SYS-01",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Vòng Phản Hồi Âm & Dương (Feedback Loops)",
        "scenario": (
            "Trong một hệ thống sưởi ấm thông minh: Khi nhiệt độ phòng tăng quá 28 độ C, cảm biến kích hoạt rơ-le ngắt nguồn sưởi; "
            "khi nhiệt độ giảm dưới 20 độ C, cảm biến tự bật máy sưởi trở lại để giữ phòng luôn ở mức 24 độ C ổn định."
        ),
        "question": "Cơ chế điều khiển học (Cybernetics) nào đang giúp căn phòng duy trì trạng thái cân bằng động?",
        "options": [
            "A. Vòng phản hồi dương khuếch đại không giới hạn",
            "B. Vòng phản hồi âm (Negative Feedback Loop): Tự động sinh lực đảo nghịch để triệt tiêu độ lệch và đưa hệ thống về điểm cân bằng mong muốn",
            "C. Mất cân bằng nội môi",
            "D. Vận hành tuyến tính hở"
        ],
        "correct_index": 1,
        "explanation": "Phản hồi âm là cơ chế sống còn để duy trì sự ổn định của sinh vật (thân nhiệt) và tổ chức (kiểm soát rủi ro). Không có phản hồi âm, hệ thống sẽ nổ tung.",
        "trap_analysis": "Nhầm tưởng 'phản hồi âm' là điều tiêu cực; thực chất phản hồi âm là chiếc phanh hãm cứu mạng giữ cho cỗ máy không trật bánh."
    },
    {
        "id": "Q-SYS-02",
        "model_id": "SYS-02",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Biên Độ An Toàn & Dự Phòng (Margin of Safety & Redundancy)",
        "scenario": (
            "Khi thiết kế thang máy dự kiến chở tối đa 10 người (khoảng 700 kg), các kỹ sư sử dụng dây cáp và động cơ có sức chịu tải thực tế lên tới 3.500 kg (gấp 5 lần). "
            "Tương tự, khi nhà đầu tư định giá cổ phiếu đáng giá 100.000đ, họ kiên nhẫn đợi giá thị trường giảm xuống 65.000đ mới giải ngân."
        ),
        "question": "Nguyên lý kỹ thuật và đầu tư cốt lõi này có tên là gì?",
        "options": [
            "A. Tối ưu hóa hiệu suất tối đa không dư thừa",
            "B. Biên độ An toàn (Margin of Safety): Tạo lớp đệm dự phòng chống lại sai số trong đo lường và những cú sốc bất ngờ của tương lai",
            "C. Vòng phản hồi dương",
            "D. Nút cổ chai"
        ],
        "correct_index": 1,
        "explanation": "Tương lai vốn chứa đựng những điều không thể biết. Biên độ an toàn giúp bạn sống sót ngay cả khi tính toán sai hoặc gặp thiên nga đen.",
        "trap_analysis": "Vận hành hệ thống ở mức 100% công suất không có lớp đệm dự phòng; chỉ cần một cú xóc nhỏ là toàn bộ hệ thống sụp đổ dây chuyền."
    },
    {
        "id": "Q-SYS-03",
        "model_id": "SYS-03",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Điểm Nghẽn Nút Cổ Chai (Theory of Constraints / Bottleneck)",
        "scenario": (
            "Một dây chuyền sản xuất gồm 4 công đoạn: Cắt vải (100 áo/h) -> May ráp (30 áo/h) -> Đính cúc (80 áo/h) -> Đóng gói (120 áo/h). "
            "Giám đốc nhà máy quyết định chi 2 tỷ đồng mua máy Đóng gói siêu tốc mới để nâng công suất đóng gói lên 300 áo/h."
        ),
        "question": "Theo Thuyết Điểm thắt (Goldratt's Theory of Constraints), sản lượng của cả nhà máy sẽ thay đổi thế nào?",
        "options": [
            "A. Sản lượng tăng lên 300 áo/h",
            "B. Sản lượng vẫn giữ nguyên 30 áo/h và 2 tỷ đồng bị lãng phí, vì công đoạn May ráp (nút cổ chai) chưa được giải phóng",
            "C. Sản lượng tăng gấp đôi",
            "D. Toàn bộ nhà máy bị đình trệ"
        ],
        "correct_index": 1,
        "explanation": "Sức mạnh của một sợi xích được quyết định bởi mắt xích yếu nhất. Tối ưu hóa bất kỳ bộ phận nào ngoài nút cổ chai đều là sự lãng phí vô ích.",
        "trap_analysis": "Bệnh tối ưu hóa cục bộ: Chi tiền và sức lực vào những mắt xích không phải là điểm thắt cổ chai của hệ thống."
    },
    {
        "id": "Q-SYS-04",
        "model_id": "SYS-04",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Tính Chống Mong Manh (Antifragility & Barbell Strategy)",
        "scenario": (
            "Cơ bắp con người sau khi bị rách vi mô do tập tạ nặng sẽ tự tái tạo sợi cơ dày hơn và khỏe hơn để chống chịu tải trọng lớn hơn lần sau. "
            "Tương tự, một hệ thống tài chính áp dụng Chiến lược Quả tạ (Barbell Strategy): 90% để ở tài sản an toàn tuyệt đối và 10% đặt cược vào các thử nghiệm có tiềm năng x100 lần."
        ),
        "question": "Thuộc tính vượt trội hơn cả sự mạnh mẽ bền bỉ (Robustness) này được Nassim Taleb định nghĩa là gì?",
        "options": [
            "A. Tính Mong manh (Fragile)",
            "B. Tính Chống Mong manh (Antifragile): Hệ thống hưởng lợi, học hỏi và trở nên mạnh mẽ hơn từ sự biến động, va đập và căng thẳng có kiểm soát",
            "C. Trạng thái cân bằng bất động",
            "D. Giảm chấn thụ động"
        ],
        "correct_index": 1,
        "explanation": "Thứ mạnh mẽ chỉ chịu đựng được va đập; thứ chống mong manh cần va đập và biến động để tiến hóa và trở nên vượt trội.",
        "trap_analysis": "Bao bọc trong lồng kính (Fragilizing): Loại bỏ mọi va chạm nhỏ khiến hệ thống mất hoàn toàn khả năng miễn dịch và sụp đổ trước biến cố lớn đầu tiên."
    },
    {
        "id": "Q-SYS-05",
        "model_id": "SYS-05",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 2,
        "model_name": "Sự Dư Thừa Dự Phòng (Redundancy & Fail-Safe)",
        "scenario": (
            "Máy bay thương mại Boeing hay Airbus luôn được trang bị 2 hoặc 3 hệ thống thủy lực và máy tính điều khiển bay độc lập. "
            "Nếu hệ thống chính bị chập cháy hoặc hỏng hóc giữa không trung, hệ thống phụ lập tức kích hoạt tự động trong vòng 0.1 giây để phi công hạ cánh an toàn."
        ),
        "question": "Nguyên lý thiết kế hệ thống quan trọng này được gọi là gì?",
        "options": [
            "A. Tinh gọn triệt để",
            "B. Sự dư thừa dự phòng (Redundancy): Sao chép các thành phần cốt tử để đảm bảo hệ thống không bị tê liệt hoàn toàn khi một bộ phận bị hỏng",
            "C. Đòn bẩy vô hình",
            "D. Vòng lặp đơn lẻ"
        ],
        "correct_index": 1,
        "explanation": "Hiệu quả ngắn hạn ghét sự dư thừa (vì tốn chi phí); nhưng sự sinh tồn dài hạn bắt buộc phải có sự dư thừa dự phòng.",
        "trap_analysis": "Cắt giảm toàn bộ quỹ dự phòng tiền mặt và nhân sự thay thế để 'tối ưu hóa chi phí', để rồi phá sản khi gặp biến cố bất ngờ."
    },
    {
        "id": "Q-SYS-08",
        "model_id": "SYS-08",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 2,
        "model_name": "Điểm Gãy Đơn Lẻ (Single Point of Failure — SPOF)",
        "scenario": (
            "Một công ty phần mềm có 50 nhân viên nhưng toàn bộ mật khẩu quản trị máy chủ cơ sở dữ liệu và mã nguồn gốc "
            "chỉ được lưu trong chiếc máy tính xách tay của một lập trình viên duy nhất. Một ngày nọ, lập trình viên này bị tai nạn và chiếc máy tính bị mất."
        ),
        "question": "Lỗi kiến trúc hệ thống chết người nào đã đẩy công ty vào bờ vực sụp đổ?",
        "options": [
            "A. Quá nhiều bậc tự do",
            "B. Điểm gãy đơn lẻ (Single Point of Failure): Một mắt xích duy nhất mà nếu nó ngừng hoạt động, toàn bộ hệ thống lớn sẽ sụp đổ theo",
            "C. Lỗi phần mềm ngẫu nhiên",
            "D. Chi phí cận biên tăng vọt"
        ],
        "correct_index": 1,
        "explanation": "Giới tinh hoa luôn kiểm tra hệ thống của mình để tìm kiếm và triệt tiêu mọi SPOF: Từ tài chính (phụ thuộc 1 nguồn thu), vận hành đến nhân sự then chốt.",
        "trap_analysis": "Chủ quan tin tưởng một cá nhân hoặc một nhà cung cấp duy nhất mà không có phương án thay thế sẵn sàng."
    },
    {
        "id": "Q-SYS-10",
        "model_id": "SYS-10",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Hệ Quả Bậc Hai & Bậc Cao (Second-Order Thinking — Howard Marks)",
        "scenario": (
            "Chính quyền một thành phố quyết định áp đặt mức giá trần cho thuê nhà ở mức rất thấp nhằm giúp đỡ người nghèo (Bậc 1: Giá thuê rẻ tức thì). "
            "Sau 2 năm, các chủ nhà ngừng đầu tư bảo trì chung cư, ngừng xây thêm nhà cho thuê vì không có lãi; nguồn cung nhà ở sụt giảm thê thảm khiến người nghèo hoàn toàn không còn nhà để thuê (Hệ quả Bậc 2 & 3)."
        ),
        "question": "Câu hỏi kích hoạt tư duy nào của Howard Marks giúp các nhà hoạch định tránh được thảm họa chính sách này?",
        "options": [
            "A. 'Làm sao để làm hài lòng cử tri ngay trong tuần này?'",
            "B. 'Và sau đó điều gì sẽ xảy ra?' (And then what?) — Dự phóng phản ứng của các tác nhân và biến động cung cầu trong tương lai",
            "C. 'Ai là người chịu trách nhiệm pháp lý?'",
            "D. 'Mức giá này đã rẻ nhất khu vực chưa?'"
        ],
        "correct_index": 1,
        "explanation": "Tư duy bậc một chỉ thấy cái lợi trước mắt. Tư duy bậc hai thấy phản ứng thích nghi của con người và cấu trúc động lực dài hạn của hệ thống.",
        "trap_analysis": "Bẫy giải pháp ngây thơ: Can thiệp thô bạo vào hệ thống phức hợp mà không lường trước các phản ứng bù trừ của thị trường."
    },
    {
        "id": "Q-SYS-11",
        "model_id": "SYS-11",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Bản Đồ Không Phải Lãnh Thổ (The Map is not the Territory — Korzybski)",
        "scenario": (
            "Một nhóm thám hiểm đi trong rừng rậm dựa vào tấm bản đồ địa hình vẽ cách đây 20 năm. Bản đồ ghi rõ phía trước là một cây cầu sắt kiên cố bắc qua sông lớn. "
            "Khi đoàn đến nơi, cây cầu đã bị lũ cuốn trôi từ năm ngoái và dòng nước đang cuồn cuộn chảy xiết. Tuy nhiên, người đội trưởng vẫn ngoan cố ép đoàn vượt sông tại đúng vị trí đó vì: 'Bản đồ quân sự chính quy không bao giờ sai!', suýt nữa nhấn chìm toàn bộ đoàn thám hiểm."
        ),
        "question": "Chân lý nhận thức học và tư duy hệ thống nào vạch trần sai lầm chết người của người đội trưởng?",
        "options": [
            "A. Bản đồ không phải là Lãnh thổ (The Map is not the Territory): Mọi mô hình, biểu đồ, bảng tính Excel hay lý thuyết chỉ là sự giản lược hóa và luôn có sai số, thực tế khách quan bên ngoài mới là chân lý tối thượng",
            "B. Bản đồ luôn luôn đúng hơn thực tế do có các chuyên gia đo đạc địa lý vẽ ra",
            "C. Vận tốc dòng nước không ảnh hưởng đến cấu trúc cầu",
            "D. Hiệu ứng mỏ neo số học"
        ],
        "correct_index": 0,
        "explanation": "Bản đồ là công cụ hữu ích để định hướng, nhưng không bao giờ thay thế được thực địa sống động. Khi thực địa mâu thuẫn với bản đồ, luôn tin vào thực địa.",
        "trap_analysis": "Đồng nhất mô hình với thực tại (Confusing the Model with Reality): Tin vào mô hình định giá tài chính trên Excel mà phớt lờ thực tế doanh nghiệp đang cạn kiệt tiền mặt và đối mặt phá sản."
    },
    {
        "id": "Q-SYS-13",
        "model_id": "SYS-13",
        "pillar": "Kỹ thuật & Hệ thống",
        "tier": 1,
        "model_name": "Dao Cạo Occam (Occam's Razor — William of Ockham)",
        "scenario": (
            "Một nhà đầu tư thấy một cổ phiếu đang có thanh khoản bình thường đột ngột sụt giảm 15% trong phiên. "
            "Anh ta xây dựng thuyết âm mưu: 'Chắc chắn có một nhóm cá mập quốc tế đang câu kết với ban lãnh đạo rung lắc để cướp hàng của nhỏ lẻ!'. "
            "Một người bạn kiểm tra thông báo và chỉ ra: 'Hôm nay là ngày công ty chốt danh sách chia cổ tức tiền mặt 1.500đ và giá bị điều chỉnh kỹ thuật'."
        ),
        "question": "Nguyên lý logic và nhận thức nào giúp người bạn loại bỏ ngay thuyết âm mưu hoang đường?",
        "options": [
            "A. Dao cạo Occam (Occam's Razor): Trong các giả thuyết cùng giải thích được hiện tượng, hãy ưu tiên giả thuyết đòi hỏi ít giả định ngầm nhất và trực tiếp nhất",
            "B. Càng nhiều âm mưu phức tạp thì càng đúng",
            "C. Đòn bẩy tài chính",
            "D. Luật số lớn"
        ],
        "correct_index": 0,
        "explanation": "Đừng phức tạp hóa những gì có thể giải thích bằng nguyên nhân đơn giản và hiển nhiên nhất. Càng nhiều giả định 'nếu như', xác suất đúng càng tiến về 0.",
        "trap_analysis": "Bẫy thích thuyết âm mưu: Não người có xu hướng thích những câu chuyện ly kỳ bí hiểm hơn là chấp nhận những sự thật đơn giản nhưng trần trụi."
    },

]

# =============================================================================
# 3. NGÂN HÀNG TRẮC NGHIỆM TÌNH HUỐNG 100 NGUYÊN LÝ KHỞI THỦY (28 BÀI TOÁN THỰC CHIẾN 7 LĨNH VỰC)
# =============================================================================
PRINCIPLES_QUIZ = [
    # -------------------------------------------------------------------------
    # LĨNH VỰC 1: VẬT LÝ HỌC (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-PHYS-01",
        "principle_name": "Nguyên lý Bất định Heisenberg (Uncertainty Principle)",
        "domain": "Vật lý học",
        "scenario": (
            "Khi ban giám đốc lắp đặt camera giám sát chi tiết từng bàn làm việc và đo số lần gõ phím của lập trình viên, "
            "họ nhận thấy các lập trình viên bắt đầu gõ phím liên tục các dòng code rác vô nghĩa để đối phó, trong khi chất lượng phần mềm thực sự đi xuống."
        ),
        "question": "Hiện tượng 'hành động quan sát làm biến dạng chính đối tượng bị quan sát' phản ánh nguyên lý nào?",
        "options": [
            "A. Định luật 1 Newton",
            "B. Nguyên lý Bất định Heisenberg & Hiệu ứng Người quan sát (Observer Effect / Định luật Goodhart)",
            "C. Định luật Ohm",
            "D. Định luật Coulomb"
        ],
        "correct_index": 1,
        "explanation": "Trong vật lý lượng tử cũng như trong khoa học xã hội: khi một thước đo trở thành mục tiêu quản lý, nó lập tức không còn là một thước đo tốt nữa.",
        "trap_analysis": "Tin rằng có thể đo lường và giám sát con người một cách hoàn toàn khách quan mà không làm thay đổi tâm lý và hành vi của họ."
    },
    {
        "id": "Q-PRIN-PHYS-02",
        "principle_name": "Định luật 1 Nhiệt động học (Bảo toàn Năng lượng)",
        "domain": "Vật lý học",
        "scenario": (
            "Một người làm việc 16 tiếng mỗi ngày, uống 4 lon nước tăng lực và chỉ ngủ 3 tiếng. Họ tự hào rằng mình đã 'hack được thời gian' "
            "và tạo ra năng lượng vô tận từ ý chí. Đến tuần thứ ba, họ ngã quỵ nhập viện vì suy kiệt thượng thận và mất 2 tháng để hồi phục."
        ),
        "question": "Quy luật vật lý bất biến nào đã trừng phạt người này?",
        "options": [
            "A. Định luật Bảo toàn Năng lượng: Năng lượng không tự nhiên sinh ra, việc dùng chất kích thích chỉ là vay nóng năng lượng từ tương lai với lãi suất cắt cổ",
            "B. Thuyết vạn vật hấp dẫn",
            "C. Hiện tượng khúc xạ ánh sáng",
            "D. Định luật phản xạ"
        ],
        "correct_index": 0,
        "explanation": "Cơ thể con người là một cỗ máy sinh học tuân theo định luật bảo toàn năng lượng. Mọi sự vay mượn sinh lực không bền vững đều phải trả bằng suy thoái hệ thống.",
        "trap_analysis": "Ảo tưởng rằng ý chí tinh thần có thể phá vỡ các giới hạn sinh lý và nhiệt động học của cơ thể vật lý."
    },
    {
        "id": "Q-PRIN-PHYS-03",
        "principle_name": "Nguyên lý Cực tiểu Tác dụng (Principle of Least Action)",
        "domain": "Vật lý học",
        "scenario": (
            "Một tia sáng khi truyền từ không khí vào mặt nước luôn tự động bẻ cong (khúc xạ) theo đúng đường đi giúp nó tốn ít thời gian nhất để đến đích. "
            "Tương tự, dòng sông luôn uốn lượn theo sườn đồi thay vì đâm xuyên qua vách đá hoa cương."
        ),
        "question": "Nguyên lý tự nhiên tối ưu hóa đường đi ngắn nhất này được gọi là gì?",
        "options": [
            "A. Nguyên lý Cực tiểu Tác dụng (Principle of Least Action / Fermat): Tự nhiên luôn vận hành theo con đường tiêu hao ít hành động/năng lượng nhất",
            "B. Định luật ly tâm",
            "C. Hiện tượng mao dẫn",
            "D. Hiệu ứng Doppler"
        ],
        "correct_index": 0,
        "explanation": "Bậc thầy chiến lược không dùng sức mạnh thô bạo chống lại dòng chảy tự nhiên; họ thiết kế hệ thống theo con đường có lực cản nhỏ nhất.",
        "trap_analysis": "Húc đầu vào bức tường đá kiên cố của đối thủ thay vì luồn lách qua những khe hở tự nhiên không có người phòng thủ."
    },
    {
        "id": "Q-PRIN-PHYS-04",
        "principle_name": "Hiện tượng Cộng hưởng (Resonance)",
        "domain": "Vật lý học",
        "scenario": (
            "Một trung đoàn quân đội khi đi đều bước qua một cây cầu treo đã vô tình tạo ra nhịp chân trùng khít với tần số dao động riêng của cây cầu. "
            "Biên độ dao động của cầu tăng vọt dữ dội khiến cây cầu thép sụp đổ tan tành, dù trọng lượng của đoàn quân không hề quá tải."
        ),
        "question": "Quy luật vật lý nào biến các xung lực nhỏ đồng nhịp thành sức mạnh phá hủy hoặc kiến tạo khổng lồ?",
        "options": [
            "A. Hiện tượng giao thoa sóng",
            "B. Hiện tượng Cộng hưởng (Resonance): Khi tần số cưỡng bức trùng với tần số riêng của hệ thống, biên độ dao động sẽ tăng lên cực đại",
            "C. Phản xạ toàn phần",
            "D. Áp suất tĩnh học"
        ],
        "correct_index": 1,
        "explanation": "Trong truyền thông và lãnh đạo: khi thông điệp của bạn cộng hưởng đúng tần số tâm lý và nỗi đau của đám đông, một lực tác động nhỏ sẽ tạo nên làn sóng bùng nổ.",
        "trap_analysis": "Bỏ qua sức mạnh cộng hưởng nhịp điệu: Đẩy một chiếc xích đu sai nhịp sẽ triệt tiêu lực; đẩy đúng nhịp sẽ đưa xích đu lên trời cao."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 2: HÓA HỌC & KHOA HỌC VẬT LIỆU (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-CHEM-01",
        "principle_name": "Nguyên lý Chuyển dịch Cân bằng Le Chatelier",
        "domain": "Hóa học & Khoa học Vật liệu",
        "scenario": (
            "Khi một người lãnh đạo mới về một phòng ban đang vận hành ổn định và ngay lập tức ban hành hàng loạt nội quy thắt chặt đột ngột, "
            "nhân viên không công khai phản đối nhưng ngầm làm việc chậm lại, xin nghỉ ốm nhiều hơn, khiến năng suất tụt giảm trầm trọng."
        ),
        "question": "Nguyên lý tự nhiên nào giải thích phản ứng kháng cự tự động này của hệ thống?",
        "options": [
            "A. Định luật Bảo toàn Khối lượng",
            "B. Nguyên lý Le Chatelier: Khi một hệ thống cân bằng bị cưỡng bức thay đổi, nó sẽ tự động sinh phản lực chống lại sự thay đổi đó",
            "C. Định luật Vạn vật hấp dẫn",
            "D. Nguyên lý Bất định Heisenberg"
        ],
        "correct_index": 1,
        "explanation": "Muốn thay đổi một hệ thống đang cân bằng bền, không thể dùng bạo lực áp đặt tức thời mà phải tăng nhiệt độ từ từ hoặc dịch chuyển điều kiện biên khéo léo.",
        "trap_analysis": "Ảo tưởng có thể ép buộc con người hoặc tổ chức thay đổi mà không phải trả giá bằng phản lực nội tại."
    },
    {
        "id": "Q-PRIN-CHEM-02",
        "principle_name": "Nguyên lý Chất Xúc tác (Catalysis)",
        "domain": "Hóa học & Khoa học Vật liệu",
        "scenario": (
            "Hai nhóm sinh viên cùng tham gia nghiên cứu khoa học. Nhóm A cặm cụi đọc tài liệu giấy và dịch thủ công từng trang, mất 3 tháng. "
            "Nhóm B dùng công cụ AI tổng hợp tài liệu và lập trình mã nguồn, hoàn thành nghiên cứu chỉ sau 1 tuần với chất lượng tương đương."
        ),
        "question": "Công cụ AI đóng vai trò gì trong phản ứng nghiên cứu khoa học theo nguyên lý hóa học?",
        "options": [
            "A. Chất phản ứng bị tiêu hao",
            "B. Chất Xúc tác (Catalyst): Làm hạ thấp năng lượng hoạt hóa (rào cản độ khó) giúp phản ứng xảy ra nhanh gấp bội mà không bị hao mòn",
            "C. Chất ức chế",
            "D. Sản phẩm phụ"
        ],
        "correct_index": 1,
        "explanation": "Người thông minh không dùng bạo lực vượt qua rào cản năng lượng; họ tìm kiếm chất xúc tác (công nghệ, quy trình, mạng lưới) để hạ độ khó xuống.",
        "trap_analysis": "Cố chấp làm việc theo lối khổ hạnh, xem thường các đòn bẩy xúc tác hiện đại."
    },
    {
        "id": "Q-PRIN-CHEM-03",
        "principle_name": "Nửa Đời Phân Rã (Half-Life)",
        "domain": "Hóa học & Khoa học Vật liệu",
        "scenario": (
            "Một kỹ sư phần mềm nắm vững một công nghệ lập trình thịnh hành năm 2015. Sau 5 năm không học thêm kiến thức mới, "
            "hơn 50% kiến thức cũ của anh ta đã trở nên lỗi thời và không còn công ty nào tuyển dụng công nghệ đó nữa."
        ),
        "question": "Quy luật phân rã phóng xạ nào mô tả tốc độ suy hao giá trị của tri thức công nghệ theo thời gian?",
        "options": [
            "A. Chu kỳ Bán rã (Half-Life of Knowledge): Khoảng thời gian để một nửa lượng tri thức trong một lĩnh vực bị thay thế hoặc trở nên lỗi thời",
            "B. Phản ứng trùng hợp",
            "C. Tốc độ kết tủa",
            "D. Cân bằng hóa học"
        ],
        "correct_index": 0,
        "explanation": "Trong thời đại số, chu kỳ bán rã của kỹ năng công nghệ rút ngắn xuống chỉ còn 2-3 năm. Muốn giữ giá trị, bạn phải liên tục tái nạp tri thức mới.",
        "trap_analysis": "Thỏa mãn với tấm bằng đại học và nghĩ rằng kiến thức học một lần có thể dùng để kiếm sống suốt 40 năm."
    },
    {
        "id": "Q-PRIN-CHEM-04",
        "principle_name": "Giới Hạn Bão Hòa Dung Dịch (Saturation Limit)",
        "domain": "Hóa học & Khoa học Vật liệu",
        "scenario": (
            "Một cốc nước chỉ có thể hòa tan tối đa 36g muối ở nhiệt độ phòng. Nếu bạn đổ thêm 100g muối vào, "
            "lượng muối thừa sẽ không thể tan thêm mà lắng xuống đáy cốc thành cặn bã làm đục ngầu nước."
        ),
        "question": "Quy luật hóa học này cảnh báo điều gì về việc tiếp thu thông tin và học tập nhồi nhét?",
        "options": [
            "A. Dung lượng hấp thụ nhận thức của não bộ có Giới hạn bão hòa; tiếp tục nhồi nhét khi não đã bão hòa chỉ tạo ra rác và sự kiệt sức",
            "B. Muối luôn tan vô hạn trong nước",
            "C. Càng đổ nhiều kiến thức thì não càng thông minh ngay lập tức",
            "D. Nước sẽ biến thành chất rắn"
        ],
        "correct_index": 0,
        "explanation": "Học tập hiệu quả đòi hỏi các khoảng nghỉ để kết tinh tinh thể tri thức. Vượt quá ngưỡng bão hòa chỉ tạo ra sự quá tải nhận thức.",
        "trap_analysis": "Cố học liên tục 10 tiếng một ngày mà không cho não ngủ nghỉ để tổng hợp khớp thần kinh."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 3: SINH HỌC & TIẾN HÓA (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-BIO-01",
        "principle_name": "Cân Bằng Nội Môi (Homeostasis)",
        "domain": "Sinh học & Tiến hóa",
        "scenario": (
            "Khi trời nóng 40 độ C, cơ thể con người tự động toát mồ hôi để hạ nhiệt; khi trời lạnh 5 độ C, cơ thể tự động run rẩy sinh nhiệt "
            "để duy trì thân nhiệt chuẩn 37 độ C bảo vệ các cơ quan nội tạng."
        ),
        "question": "Khả năng tự điều chỉnh duy trì sự ổn định sinh học bên trong bất chấp biến động môi trường ngoài được gọi là gì?",
        "options": [
            "A. Cân bằng nội môi (Homeostasis): Khả năng của hệ thống tự duy trì các thông số sinh tồn ổn định trước ngoại cảnh",
            "B. Thích nghi đột biến",
            "C. Phản xạ có điều kiện",
            "D. Chuyển hóa kỵ khí"
        ],
        "correct_index": 0,
        "explanation": "Một tổ chức xuất sắc phải xây dựng được cơ chế Homeostasis: Dù thị trường biến động bão bùng bên ngoài, kỷ luật và dòng tiền bên trong vẫn giữ được sự vững chãi.",
        "trap_analysis": "Để hoàn cảnh bên ngoài chi phối hoàn toàn tâm trạng và cấu trúc vận hành bên trong."
    },
    {
        "id": "Q-PRIN-BIO-02",
        "principle_name": "Tiến Hóa Phân Kỳ vs Đồng Quy (Convergent Evolution)",
        "domain": "Sinh học & Tiến hóa",
        "scenario": (
            "Cá mập (loài cá sụn) và Cá heo (loài thú có vú thở bằng phổi) có tổ tiên cách nhau hàng trăm triệu năm. "
            "Tuy nhiên, do cùng sống trong môi trường nước và săn mồi tốc độ cao, cả hai loài đều tiến hóa thành hình dáng thủy động học hình thoi giống hệt nhau."
        ),
        "question": "Hiện tượng các thực thể có nguồn gốc khác nhau tự tiến hóa về cùng một giải pháp tối ưu được gọi là gì?",
        "options": [
            "A. Tiến hóa phân kỳ",
            "B. Tiến hóa đồng quy (Convergent Evolution): Khi đối mặt với cùng một áp lực môi trường vật lý, các giải pháp tối ưu độc lập sẽ tự tìm về cùng một hình thái",
            "C. Đột biến gen nhân tạo",
            "D. Ký sinh đồng chủng"
        ],
        "correct_index": 1,
        "explanation": "Tại sao các ứng dụng công nghệ như Uber và Grab lại giống nhau? Không hẳn là sao chép, mà vì áp lực tối ưu hóa trải nghiệm người dùng dẫn về cùng một cấu trúc tối ưu.",
        "trap_analysis": "Cố gắng tạo ra sự khác biệt dị hợm chỉ để khác người mà vi phạm các quy luật tối ưu hóa đã được chọn lọc tự nhiên chứng thực."
    },
    {
        "id": "Q-PRIN-BIO-03",
        "principle_name": "Đột Biến Thích Nghi (Adaptive Mutation)",
        "domain": "Sinh học & Tiến hóa",
        "scenario": (
            "Khi một loại thuốc kháng sinh mới được đưa vào bệnh viện, 99.9% vi khuẩn bị tiêu diệt ngay lập tức. "
            "Tuy nhiên, có một số lượng cực nhỏ vi khuẩn mang đột biến gen ngẫu nhiên giúp chúng sống sót và nhân bản thành chủng siêu vi khuẩn kháng thuốc."
        ),
        "question": "Quy luật sinh học này nhắc nhở điều gì về việc loại trừ rủi ro trong quản trị chiến lược?",
        "options": [
            "A. Không có giải pháp đơn lẻ nào có thể tiêu diệt hoàn toàn một vấn đề phức tạp; sự sống luôn tìm ra lối thoát thông qua các biến thể mới",
            "B. Thuốc kháng sinh luôn vô dụng",
            "C. Vi khuẩn có trí thông minh nhân tạo",
            "D. Đột biến luôn có hại"
        ],
        "correct_index": 0,
        "explanation": "Thế giới thực liên tục tiến hóa chống lại các giải pháp can thiệp thô bạo. Hãy chuẩn bị cho các đợt biến dị thích nghi tiếp theo của đối thủ.",
        "trap_analysis": "Chủ quan tuyên bố chiến thắng vĩnh viễn sau một chiến dịch thành công ngắn hạn."
    },
    {
        "id": "Q-PRIN-BIO-04",
        "principle_name": "Cộng Sinh Tương Hỗ (Mutualism)",
        "domain": "Sinh học & Tiến hóa",
        "scenario": (
            "Loài ong hút mật hoa để làm thức ăn nuôi đàn, đồng thời phấn hoa dính vào thân ong được phát tán đi khắp nơi giúp cây cối thụ phấn sinh sản. "
            "Cả hai loài cùng hưởng lợi và nương tựa vào nhau để bùng nổ dân số."
        ),
        "question": "Mô hình quan hệ sinh học đôi bên cùng có lợi này mang tên là gì?",
        "options": [
            "A. Ký sinh bắt buộc (Parasitism)",
            "B. Cộng sinh tương hỗ (Mutualism): Mối quan hệ hợp tác mà cả hai bên cùng nâng đỡ nhau phát triển vượt bậc so với việc sống đơn độc",
            "C. Cạnh tranh sinh tồn",
            "D. Hội sinh một chiều"
        ],
        "correct_index": 1,
        "explanation": "Chiến lược bền vững nhất trong kinh doanh và đời sống không phải là ăn thịt đối tác (Ký sinh/Zero-sum), mà là thiết kế hệ sinh thái đôi bên cùng thịnh vượng (Positive-sum).",
        "trap_analysis": "Tư duy vắt kiệt nhà cung cấp hoặc đối tác để tối đa hóa lợi nhuận ngắn hạn, dẫn đến việc đối tác phá sản và hệ thống sụp đổ."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 4: TÂM LÝ & NHẬN THỨC (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-PSY-01",
        "principle_name": "Định Luật Weber-Fechner",
        "domain": "Tâm lý & Nhận thức",
        "scenario": (
            "Nếu bạn đang cầm một gói đường 100g, ai đó đặt thêm 10g bạn sẽ cảm nhận thấy sự nặng thêm ngay lập tức. "
            "Nhưng nếu bạn đang vác một bao tải cát 50kg, ai đó đặt thêm 10g đường thì bạn hoàn toàn không thể cảm nhận được bất kỳ sự khác biệt nào."
        ),
        "question": "Định luật tâm lý học giác quan này phản ánh điều gì về nhận thức con người?",
        "options": [
            "A. Khả năng cảm nhận sự thay đổi tỷ lệ nghịch với cường độ kích thích nền ban đầu: Kích thích nền càng lớn, ta càng cần sự thay đổi lớn hơn mới nhận biết được",
            "B. Mọi giác quan đều hoàn toàn chính xác",
            "C. Bao cát nặng hơn gói đường",
            "D. Cảm giác của con người không đổi"
        ],
        "correct_index": 0,
        "explanation": "Khi một người đã quen tiêu 100 triệu mỗi ngày, việc thưởng thêm 1 triệu sẽ vô nghĩa. Khi bắt đầu từ số 0, 1 triệu là món quà kỳ diệu. Hiệu ứng biên giảm dần.",
        "trap_analysis": "Bệnh chai lì nhận thức: Sống trong môi trường tiêu cực lâu ngày sẽ mất khả năng nhận diện các dấu hiệu nguy hiểm nhỏ."
    },
    {
        "id": "Q-PRIN-PSY-02",
        "principle_name": "Quy Tắc Đỉnh - Đáy (Peak-End Rule — Kahneman)",
        "domain": "Tâm lý & Nhận thức",
        "scenario": (
            "Một kỳ nghỉ dưỡng 7 ngày: 6 ngày đầu tiên diễn ra bình thường, nhưng ngày thứ 4 bạn được trải nghiệm lặn biển ngắm san hô ngoạn mục (Đỉnh cao), "
            "và vào giây phút trả phòng ngày cuối cùng, khách sạn tặng bạn một món quà lưu niệm viết tay xúc động (Kết thúc). "
            "Nhiều năm sau nhìn lại, bạn vẫn đánh giá kỳ nghỉ đó là 10/10 điểm hoàn hảo."
        ),
        "question": "Quy luật ghi nhớ trải nghiệm nào của Daniel Kahneman chi phối ký ức của bạn?",
        "options": [
            "A. Tính toán trung bình cộng thời gian thực",
            "B. Quy tắc Đỉnh - Kết (Peak-End Rule): Não bộ đánh giá một trải nghiệm hầu như chỉ dựa vào cảm xúc tại điểm mãnh liệt nhất (Peak) và cảm xúc ở giây phút kết thúc (End)",
            "C. Trí nhớ nhiếp ảnh toàn diện",
            "D. Hiệu ứng quên lãng đều đặn"
        ],
        "correct_index": 1,
        "explanation": "Khách hàng không nhớ toàn bộ quá trình trải nghiệm; họ chỉ nhớ khoảnh khắc thăng hoa nhất và cách bạn chào tạm biệt họ. Thiết kế điểm kết thúc thật ấn tượng.",
        "trap_analysis": "Làm rất tốt từ đầu đến cuối nhưng phá hỏng giây phút bàn giao cuối cùng, để lại ký ức tồi tệ trong tâm trí đối tác."
    },
    {
        "id": "Q-PRIN-PSY-03",
        "principle_name": "Hiệu Ứng Zeigarnik (Zeigarnik Effect)",
        "domain": "Tâm lý & Nhận thức",
        "scenario": (
            "Một người bồi bàn có thể ghi nhớ chính xác bàn nào gọi món gì của 20 bàn ăn cùng lúc mà không cần ghi chép. "
            "Nhưng ngay sau khi hóa đơn được thanh toán xong xuôi, người bồi bàn lập tức quên sạch toàn bộ chi tiết các món ăn của bàn đó."
        ),
        "question": "Hiện tượng não bộ liên tục nhắc nhở về những công việc chưa hoàn thành được gọi là gì?",
        "options": [
            "A. Hiệu ứng Zeigarnik: Não bộ duy trì sự tập trung và căng thẳng nhận thức đối với các tác vụ dang dở, và chỉ giải phóng bộ nhớ khi tác vụ được đóng lại",
            "B. Bệnh mất trí nhớ ngắn hạn",
            "C. Hiệu ứng hào quang",
            "D. Thuyết phản xạ vô thức"
        ],
        "correct_index": 0,
        "explanation": "Các việc dang dở (Open Loops) giống như các ứng dụng chạy ngầm ngốn pin não bộ. Muốn giải phóng sương mù não, hãy ghi toàn bộ việc dang dở ra giấy.",
        "trap_analysis": "Mở ra hàng chục dự án cùng lúc mà không đóng lại cái nào, khiến năng lượng tinh thần bị cạn kiệt bởi hàng trăm vòng lặp Zeigarnik gặm nhấm."
    },
    {
        "id": "Q-PRIN-PSY-04",
        "principle_name": "Bất Hòa Nhận Thức (Cognitive Dissonance — Festinger)",
        "domain": "Tâm lý & Nhận thức",
        "scenario": (
            "Một người biết rõ rằng hút thuốc lá gây ung thư phổi và tốn tiền. Thay vì bỏ thuốc lá, "
            "người đó tự biện minh: 'Hút thuốc giúp tôi sáng tạo công việc, và ông hàng xóm hút thuốc suốt đời vẫn sống thọ 90 tuổi đấy thôi!'."
        ),
        "question": "Cơ chế tâm lý tự dối mình để giải tỏa sự mâu thuẫn nội tâm này có tên là gì?",
        "options": [
            "A. Bất hòa nhận thức (Cognitive Dissonance): Nỗi khó chịu tột cùng khi hành vi đi ngược lại niềm tin, buộc não bộ phải bẻ cong lý lẽ để tự an ủi",
            "B. Tư duy logic hình thức",
            "C. Thuyết động lực nội tại",
            "D. Hiệu ứng tự kỷ ám thị"
        ],
        "correct_index": 0,
        "explanation": "Khi hành vi thực tế và niềm tin đạo đức mâu thuẫn nhau, con người hiếm khi thay đổi hành vi mà thường thay đổi lý lẽ ngụy biện để bảo vệ cái tôi.",
        "trap_analysis": "Tự huyễn hoặc bản thân bằng những lý do giả tạo khi phạm phải sai lầm thay vì dũng cảm đối diện với sự thật."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 5: KINH TẾ HỌC & TIỀN TỆ (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-ECON-01",
        "principle_name": "Định Luật Gresham",
        "domain": "Kinh tế học & Tiền tệ",
        "scenario": (
            "Trong một môi trường làm việc mà những người giỏi, trung thực, cống hiến thật sự không được công nhận, "
            "trong khi những kẻ nịnh bợ, làm màu lại được thăng tiến, dần dần những người tài năng nộp đơn nghỉ việc hết, chỉ còn lại những kẻ nịnh bợ."
        ),
        "question": "Định luật kinh tế học kinh điển nào được diễn đạt qua câu 'Tiền xấu đuổi tiền tốt'?",
        "options": [
            "A. Định luật Cung Cầu",
            "B. Định luật Gresham: Khi tiền xấu và tiền tốt cùng lưu hành theo mệnh giá pháp định, tiền xấu sẽ đánh bật tiền tốt ra khỏi lưu thông",
            "C. Hiệu ứng Mạng lưới",
            "D. Nghịch lý Giá trị của Kim cương và Nước"
        ],
        "correct_index": 1,
        "explanation": "Nếu tổ chức không có cơ chế thanh lọc nghiêm ngặt, cái xấu/chất lượng kém sẽ tích tụ và đuổi sạch các giá trị tinh hoa ra ngoài.",
        "trap_analysis": "Bẫy thờ ơ với tiêu chuẩn: Nghĩ rằng dung túng một vài nhân sự yếu kém sẽ không ảnh hưởng tới nhân sự xuất sắc."
    },
    {
        "id": "Q-PRIN-ECON-02",
        "principle_name": "Lợi Ích Cận Biên Giảm Dần (Diminishing Marginal Utility)",
        "domain": "Kinh tế học & Tiền tệ",
        "scenario": (
            "Khi bạn đang đói cồn cào, chiếc bánh pizza đầu tiên mang lại cảm giác ngon tuyệt đỉnh (100 điểm thỏa mãn). "
            "Chiếc thứ hai chỉ còn 60 điểm, chiếc thứ ba còn 20 điểm, và đến chiếc thứ tư bạn cảm thấy buồn nôn và ghê sợ."
        ),
        "question": "Quy luật kinh tế học hành vi này phản ánh điều gì?",
        "options": [
            "A. Lợi ích cận biên giảm dần: Lợi ích tăng thêm thu được từ việc tiêu dùng thêm một đơn vị sản phẩm sẽ giảm dần sau mỗi lần tiêu dùng",
            "B. Giá trị trao đổi không đổi",
            "C. Chi phí cố định",
            "D. Lạm phát chi phí đẩy"
        ],
        "correct_index": 0,
        "explanation": "Quy luật này chi phối từ tiền bạc, đồ ăn đến tình cảm: Cái gì quá nhiều cũng sẽ mất giá trị biên. Bí quyết hạnh phúc là biết điểm dừng tối ưu.",
        "trap_analysis": "Cố tích lũy thêm của cải vượt quá ngưỡng hưởng dụng mà không biết rằng giá trị biên của chúng đang tiến về 0."
    },
    {
        "id": "Q-PRIN-ECON-03",
        "principle_name": "Hiệu Ứng Cantillon (Cantillon Effect)",
        "domain": "Kinh tế học & Tiền tệ",
        "scenario": (
            "Khi ngân hàng trung ương in tiền để cứu trợ kinh tế, các ngân hàng thương mại lớn, tập đoàn tài chính và giới tinh hoa gần nguồn tiền "
            "nhận được tiền trước tiên khi giá cả hàng hóa chưa kịp tăng. Đến khi dòng tiền này lan tới tay người lao động nghèo, giá thịt, giá nhà đã tăng vọt 50%."
        ),
        "question": "Quy luật kinh tế vĩ mô nào giải thích tại sao việc bơm tiền luôn làm giàu cho giới tài phiệt và làm nghèo người làm công ăn lương?",
        "options": [
            "A. Thuyết phân phối tiền tệ đồng đều",
            "B. Hiệu ứng Cantillon: Dòng tiền mới bơm không lan tỏa tức thời mà chảy qua các mắt xích, tạo lợi thế bất đối xứng khổng lồ cho người đứng gần van bơm tiền",
            "C. Cân bằng tiền tệ Fisher",
            "D. Định luật tiền tệ M2"
        ],
        "correct_index": 1,
        "explanation": "Lạm phát là một loại thuế ngầm vô hình. Người gần nguồn tiền được mua tài sản giá rẻ; người xa nguồn tiền phải gánh trọn cơn bão giá cả.",
        "trap_analysis": "Giữ tiền mặt trong thời kỳ bơm tiền tệ và nghĩ rằng mình đang an toàn, trong khi sức mua thực tế đang bị bốc hơi 10-15% mỗi năm."
    },
    {
        "id": "Q-PRIN-ECON-04",
        "principle_name": "Chi Phí Giao Dịch Coase (Coase's Theory of the Firm)",
        "domain": "Kinh tế học & Tiền tệ",
        "scenario": (
            "Tại sao các công ty lại tồn tại thay vì để mọi cá nhân tự do ký hợp đồng mua bán dịch vụ với nhau trên thị trường tự do? "
            "Nhà kinh tế học đoạt giải Nobel Ronald Coase chỉ ra: Chi phí tìm kiếm đối tác, thương lượng, đàm phán hợp đồng và giám sát thực thi trên thị trường là rất đắt đỏ."
        ),
        "question": "Khái niệm kinh tế học nào quyết định ranh giới độ lớn của một doanh nghiệp?",
        "options": [
            "A. Chi phí giao dịch (Transaction Costs): Công ty sẽ mở rộng quy mô chừng nào chi phí tổ chức nội bộ còn rẻ hơn chi phí giao dịch ngoài thị trường mở",
            "B. Chi phí kế toán thuần túy",
            "C. Thuế thu nhập doanh nghiệp",
            "D. Chi phí quảng cáo tiếp thị"
        ],
        "correct_index": 0,
        "explanation": "Khi Internet và AI kéo tụt chi phí giao dịch về 0, các tập đoàn khổng lồ cồng kềnh sẽ bị phân rã thành các mạng lưới cá nhân tự trị (Sovereign Individuals).",
        "trap_analysis": "Cố nuôi một bộ máy nhân sự nội bộ cồng kềnh khi chi phí thuê ngoài và dùng AI công cụ bên ngoài đã rẻ hơn gấp 10 lần."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 6: TOÁN HỌC & KHOA HỌC MÁY TÍNH (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-COMP-01",
        "principle_name": "Định Luật Moore & Tăng Trưởng Hàm Mũ",
        "domain": "Toán học & Khoa học Máy tính",
        "scenario": (
            "Năm 1965, Gordon Moore dự báo: Số lượng bóng bán dẫn trên một vi mạch sẽ tăng gấp đôi sau mỗi 2 năm trong khi giá thành không đổi. "
            "Nhờ quy luật này, một chiếc điện thoại thông minh giá vài triệu đồng hôm nay có sức mạnh tính toán vượt xa toàn bộ siêu máy tính của NASA thời đưa người lên Mặt Trăng."
        ),
        "question": "Sức mạnh toán học nào đang lèo lái sự phát triển của công nghệ thông tin và AI?",
        "options": [
            "A. Tăng trưởng tuyến tính số học (1, 2, 3, 4...)",
            "B. Tăng trưởng hàm mũ (Exponential Growth): Tốc độ tăng trưởng tỷ lệ thuận với chính quy mô hiện tại của hệ thống, tạo ra sự bùng nổ vũ bão sau điểm uốn",
            "C. Phân phối logarit đều",
            "D. Dao động điều hòa"
        ],
        "correct_index": 1,
        "explanation": "Bộ não người tiến hóa trong thế giới tuyến tính nên rất kém trong việc hình dung sự tăng trưởng hàm mũ. Sau 30 bước nhảy hàm mũ, bạn không đi được 30 mét mà đi được 1 tỷ mét.",
        "trap_analysis": "Đánh giá thấp tương lai của công nghệ chỉ vì thấy những phiên bản đầu tiên còn ngô nghê và vụng về."
    },
    {
        "id": "Q-PRIN-COMP-02",
        "principle_name": "Định Lý Giới Hạn Trung Tâm (Central Limit Theorem)",
        "domain": "Toán học & Khoa học Máy tính",
        "scenario": (
            "Bạn tung một con xúc xắc 6 mặt độc lập nhiều lần: Mỗi lần tung kết quả là ngẫu nhiên đều từ 1 đến 6. "
            "Tuy nhiên, nếu bạn lấy trung bình cộng của 30 lần tung và lặp lại thí nghiệm 1.000 lần, đồ thị phân bố của các giá trị trung bình này sẽ tự động vẽ nên một hình chuông hoàn hảo."
        ),
        "question": "Định lý xác suất nền tảng nào bảo đảm rằng tổng của nhiều biến ngẫu nhiên độc lập sẽ hội tụ về phân phối chuẩn?",
        "options": [
            "A. Định luật số lớn",
            "B. Định lý Giới hạn Trung tâm (Central Limit Theorem): Bất kể phân phối gốc là gì, giá trị trung bình mẫu sẽ xấp xỉ phân phối chuẩn khi kích thước mẫu đủ lớn",
            "C. Bất đẳng thức Cauchy-Schwarz",
            "D. Ma trận nghịch đảo"
        ],
        "correct_index": 1,
        "explanation": "Định lý này là hòn đá tảng của thống kê thực nghiệm và học máy: Cho phép ta đo lường sai số và kiểm định giả thuyết khoa học một cách vững chắc.",
        "trap_analysis": "Đưa ra kết luận vội vàng từ một kích thước mẫu quá nhỏ (2-3 lần thử) mà không đạt đến ngưỡng hội tụ của định lý."
    },
    {
        "id": "Q-PRIN-COMP-03",
        "principle_name": "Bài Toán Dừng Tối Ưu (Optimal Stopping / Quy Tắc 37%)",
        "domain": "Toán học & Khoa học Máy tính",
        "scenario": (
            "Bạn có kế hoạch phỏng vấn 100 ứng viên để chọn 1 trợ lý xuất sắc nhất. Bạn phải quyết định nhận hoặc loại ngay sau mỗi buổi phỏng vấn mà không được gọi lại người cũ. "
            "Toán học máy tính đưa ra thuật toán tối ưu: Phỏng vấn 37 ứng viên đầu tiên chỉ để quan sát chuẩn mực, sau đó chọn ngay người đầu tiên xuất sắc hơn tất cả những người trong nhóm 37 người đó."
        ),
        "question": "Thuật toán toán học nổi tiếng này giải quyết bài toán gì trong cuộc sống?",
        "options": [
            "A. Chọn ngẫu nhiên cầu may",
            "B. Bài toán Dừng tối ưu (Optimal Stopping / 37% Rule): Cân bằng hoàn hảo giữa Chi phí thăm dò (Explore) và Lợi ích khai thác (Exploit)",
            "C. Quy hoạch tuyến tính",
            "D. Sắp xếp nổi bọt"
        ],
        "correct_index": 1,
        "explanation": "Quy tắc 37% giúp bạn tối đa hóa xác suất chọn được phương án tốt nhất trong việc tìm nhà, tuyển dụng nhân sự hay chọn bạn đời.",
        "trap_analysis": "Dừng lại quá sớm khi chưa có đủ dữ liệu thăm dò, hoặc thăm dò quá lâu cho đến khi cơ hội tốt nhất đã trôi qua mất."
    },
    {
        "id": "Q-PRIN-COMP-04",
        "principle_name": "Nghịch Lý Moravec (Moravec's Paradox)",
        "domain": "Toán học & Khoa học Máy tính",
        "scenario": (
            "Một siêu máy tính AI có thể đánh bại đại kiện tướng cờ vua số 1 thế giới và giải các phương trình vi phân phức tạp chỉ trong vài mili-giây. "
            "Tuy nhiên, việc lập trình cho một cánh tay robot nhận biết và nhặt một quả táo trong rổ mà không làm dập nát lại ngốn hàng chục năm nghiên cứu của các viện khoa học hàng đầu."
        ),
        "question": "Nghịch lý công nghệ máy tính này mang tên là gì?",
        "options": [
            "A. Nghịch lý Moravec: Những bài toán trí tuệ trừu tượng cấp cao (cờ vua, toán học) lại đòi hỏi rất ít tính toán máy tính, trong khi các kỹ năng cảm giác - vận động bản năng của đứa trẻ 1 tuổi lại đòi hỏi tài nguyên tính toán khổng lồ",
            "B. Nghịch lý Fermi",
            "C. Định lý Bất toàn Gödel",
            "D. Thuyết dừng Turing"
        ],
        "correct_index": 0,
        "explanation": "Kỹ năng vận động của con người đã được tự nhiên tôi luyện hàng triệu năm tiến hóa; còn tư duy trừu tượng mới xuất hiện vài ngàn năm. AI dễ dàng làm chủ cái mới hơn cái cũ.",
        "trap_analysis": "Lo sợ AI sẽ thay thế các công việc tay chân thợ điện, thợ sửa ống nước trước các công việc bàn giấy phân tích tài chính và luật sư."
    },

    # -------------------------------------------------------------------------
    # LĨNH VỰC 7: TRIẾT HỌC & NHẬN THỨC LUẬN (4 CÂU)
    # -------------------------------------------------------------------------
    {
        "id": "Q-PRIN-PHIL-01",
        "principle_name": "Chiếc Dao Cạo Ockham (Occam's Razor)",
        "domain": "Triết học & Nhận thức luận",
        "scenario": (
            "Một bệnh nhân bị sốt nhẹ, đau đầu và hắt hơi sổ mũi vào mùa đông. Một bác sĩ trẻ đưa ra chẩn đoán mắc một hội chứng rối loạn thần kinh hiếm gặp chỉ có 1 ca trên 1 triệu người. "
            "Bác sĩ trưởng khoa bác bỏ và nói: 'Bệnh nhân chỉ đơn thuần bị cảm cúm thông thường'."
        ),
        "question": "Nguyên lý triết học khoa học nào được phát biểu qua câu 'Khi nghe tiếng vó ngựa, hãy nghĩ đến ngựa trước khi nghĩ đến kỳ lân'?",
        "options": [
            "A. Chiếc dao cạo Ockham (Occam's Razor): Khi có hai lời giải thích cho cùng một hiện tượng, lời giải thích nào đòi hỏi ít giả định chưa được chứng minh nhất thường là lời giải thích đúng",
            "B. Thuyết đa vũ trụ",
            "C. Thuyết hoài nghi tuyệt đối",
            "D. Ngụy biện khái quát hóa"
        ],
        "correct_index": 0,
        "explanation": "Không nhân thêm các thực thể nếu không cần thiết. Đừng thêu dệt các thuyết âm mưu phức tạp khi một sai sót do cẩu thả giản đơn có thể giải thích trọn vẹn sự việc.",
        "trap_analysis": "Phức tạp hóa vấn đề để tạo cảm giác thông thái giả tạo thay vì đi thẳng vào giải pháp đơn giản và hiệu quả nhất."
    },
    {
        "id": "Q-PRIN-PHIL-02",
        "principle_name": "Tính Khả Bác Của Karl Popper (Falsifiability)",
        "domain": "Triết học & Nhận thức luận",
        "scenario": (
            "Một thầy bói phán: 'Năm nay anh sẽ gặp một biến cố lớn, nhưng nếu nó không xảy ra thì tức là phúc đức tổ tiên của anh đã hóa giải nó rồi'. "
            "Dù năm đó chuyện gì xảy ra, lời phán của thầy bói dường như luôn luôn 'đúng'."
        ),
        "question": "Triết gia khoa học Karl Popper chỉ ra tại sao các lý thuyết kiểu này là ngụy khoa học?",
        "options": [
            "A. Vì thầy bói lấy phí quá đắt",
            "B. Tính Khả bác (Falsifiability): Một lý thuyết chỉ được coi là khoa học khi nó chỉ rõ điều kiện thực nghiệm cụ thể nào có thể chứng minh nó là SAI; nếu một lý thuyết không thể bị bác bỏ, nó vô giá trị",
            "C. Vì không ai kiểm chứng tương lai",
            "D. Thuyết định mệnh luận"
        ],
        "correct_index": 1,
        "explanation": "Khoa học tiến bộ bằng cách bác bỏ các giả thuyết sai, không phải bằng cách tìm kiếm sự khẳng định vòng vo. Một giả thuyết không thể bị chứng minh sai thì không thể tạo ra tri thức mới.",
        "trap_analysis": "Xây dựng các kế hoạch kinh doanh hoặc nhận định mơ hồ đến mức xảy ra kết quả nào mình cũng có thể tự nhận là 'đã dự đoán từ trước'."
    },
    {
        "id": "Q-PRIN-PHIL-03",
        "principle_name": "Nghịch Lý Con Tàu Theseus (Ship of Theseus)",
        "domain": "Triết học & Nhận thức luận",
        "scenario": (
            "Con tàu của người anh hùng Theseus sau nhiều năm đi biển được bảo tồn tại cảng. Mỗi khi một tấm ván gỗ bị mục nát, người ta thay bằng một tấm ván mới. "
            "Sau 50 năm, 100% các tấm ván, cột buồm và dây thừng trên tàu đều đã được thay mới hoàn toàn."
        ),
        "question": "Nghịch lý triết học sâu sắc này đặt ra câu hỏi gì cho quản trị tổ chức và bản sắc con người?",
        "options": [
            "A. Con tàu sau khi thay hết ván có còn là con tàu Theseus ban đầu không? Bản sắc của một hệ thống nằm ở Vật chất cấu thành hay nằm ở Cấu trúc tổ chức và Dòng chảy liên tục?",
            "B. Gỗ mới luôn tốt hơn gỗ cũ",
            "C. Cần phá hủy con tàu để xây bảo tàng",
            "D. Vận tốc con tàu bị suy giảm"
        ],
        "correct_index": 0,
        "explanation": "Mỗi tế bào trong cơ thể bạn đều thay mới sau 7 năm; toàn bộ nhân sự công ty bạn có thể thay đổi sau 10 năm. Bản sắc tồn tại ở cấu trúc giá trị và văn hóa, không ở từng tế bào vật chất.",
        "trap_analysis": "Cố chấp bám víu vào những con người hoặc công cụ cũ mà quên mất linh hồn và sứ mệnh cốt lõi của tổ chức mới là thứ cần bảo tồn."
    },
    {
        "id": "Q-PRIN-PHIL-04",
        "principle_name": "Trách Nhiệm Dấn Thân (Skin in the Game — Taleb)",
        "domain": "Triết học & Nhận thức luận",
        "scenario": (
            "Bộ luật Hammurabi của Babylon cổ đại quy định: 'Nếu một người thợ xây một ngôi nhà cho người khác, và ngôi nhà bị sập làm chết người chủ nhà, "
            "thì chính người thợ xây đó phải bị xử tử hình'."
        ),
        "question": "Quy tắc đạo đức và quản trị rủi ro tối thượng này của Nassim Taleb có tên là gì?",
        "options": [
            "A. Trách nhiệm Dấn thân (Skin in the Game): Người đưa ra quyết định hoặc lời khuyên phải trực tiếp chịu chung rủi ro và tổn thất nếu quyết định đó sai lầm",
            "B. Bất bạo động tuyệt đối",
            "C. Trách nhiệm hữu hạn của cổ đông",
            "D. Bảo hiểm toàn diện rủi ro"
        ],
        "correct_index": 0,
        "explanation": "Thảm họa kinh tế xảy ra khi các chuyên gia tư vấn hay lãnh đạo nhận thưởng khi thắng, nhưng đẩy toàn bộ hậu quả thua lỗ cho người dân gánh chịu (Không có Skin in the Game).",
        "trap_analysis": "Nghe theo lời khuyên đầu tư của những kẻ không hề bỏ một đồng tiền thật nào của chính họ vào thương vụ mà họ đang quảng cáo."
    },
]

# =============================================================================
# 4. ACTIVE RECALL FLASHCARDS GENERATOR
# =============================================================================
def get_all_flashcards(filter_type: str = "models", pillar: Optional[str] = None, tier: Optional[int] = None) -> List[Dict[str, Any]]:
    """Tạo danh sách thẻ Flashcard chuẩn hóa từ cơ sở dữ liệu để phục vụ Active Recall."""
    cards = []

    if filter_type in ("models", "all"):
        all_models = get_all_models()
        models = filter_models(all_models, pillar=pillar, tier=tier)
        for m in models:
            cards.append({
                "id": m.get("id"),
                "type": "model",
                "category": "88 Mô hình Hạt nhân",
                "pillar": m.get("pillar"),
                "tier": m.get("tier"),
                "name_vi": m.get("name_vi"),
                "name_en": m.get("name_en"),
                # Mặt trước: Câu hỏi kích hoạt 5 giây
                "front_trigger": m.get("trigger_question") or f"Làm thế nào để nhận diện và vận dụng mô hình {m.get('name_vi')}?",
                "front_badge": f"🏛️ {m.get('pillar')} · Tier {m.get('tier')}",
                # Mặt sau: Bản chất gốc rễ & đòn bẩy
                "back_principle": m.get("first_principle"),
                "back_leverage": m.get("elite_leverage"),
                "back_trap": m.get("inversion_trap"),
                "back_lollapalooza": ", ".join(m.get("lollapalooza_pairs", [])),
                "action_steps": m.get("action_steps"),
                "boundary_conditions": m.get("boundary_conditions"),
                "real_world_case": m.get("real_world_case"),
            })

    if filter_type in ("modes", "all") and not pillar and not tier:
        for q in MODES_QUIZ:
            cards.append({
                "id": q.get("id"),
                "type": "mode",
                "category": "9 Chế độ Tư duy",
                "pillar": "Chế độ Tư duy Elite",
                "tier": 1,
                "name_vi": q.get("concept"),
                "name_en": "Elite Mode",
                "front_trigger": f"Khi nào nên kích hoạt chế độ: {q.get('concept')}?",
                "front_badge": "🧠 9 Chế độ Tư duy Tinh hoa",
                "back_principle": q.get("explanation"),
                "back_leverage": q.get("scenario"),
                "back_trap": q.get("trap_analysis"),
                "back_lollapalooza": "First Principles, Inversion, Bayesian",
            })

    if filter_type in ("principles", "all") and not tier:
        kb = load_knowledge_base()
        for p in kb.get("principles", []):
            if pillar and pillar != "Tất cả" and p.get("domain") != pillar:
                continue
            cards.append({
                "id": p.get("principle_name"),
                "type": "principle",
                "category": "100 Nguyên lý Khởi thủy",
                "pillar": p.get("domain", "Nguyên lý Khoa học"),
                "tier": p.get("tier", 1),
                "name_vi": p.get("principle_name"),
                "name_en": p.get("principle_name"),
                "front_trigger": f"💡 Chân lý bất biến của '{p.get('principle_name')}' là gì và khi nào nó bị phá vỡ?",
                "front_badge": f"🔬 {p.get('domain', 'Khoa học')}",
                "back_principle": p.get("intuitive_summary") or p.get("description"),
                "back_leverage": p.get("formal_definition"),
                "back_trap": f"Điều kiện biên: {p.get('boundary_conditions', '—')} | Khả bác: {p.get('falsification_test', '—')}",
                "back_lollapalooza": p.get("domain", ""),
            })

    return cards


# =============================================================================
# 5. USER PROGRESS & MASTERY TRACKING
# =============================================================================
def record_quiz_completion(username: str, quiz_category: str, score: int, total: int) -> Dict[str, Any]:
    """Lưu kết quả trắc nghiệm vào lịch sử người dùng."""
    hist = load_user_history(username)
    quiz_stats = hist.setdefault("quiz_stats", {
        "total_quizzes_taken": 0,
        "total_questions_answered": 0,
        "total_correct_answers": 0,
        "recent_tests": []
    })

    quiz_stats["total_quizzes_taken"] += 1
    quiz_stats["total_questions_answered"] += total
    quiz_stats["total_correct_answers"] += score

    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": quiz_category,
        "score": score,
        "total": total,
        "percentage": round((score / total * 100), 1) if total > 0 else 0
    }
    quiz_stats["recent_tests"].insert(0, entry)
    quiz_stats["recent_tests"] = quiz_stats["recent_tests"][:30]

    save_user_history(username, hist)
    return quiz_stats


def update_flashcard_mastery(username: str, item_id: str, status: str) -> Dict[str, Any]:
    """
    Cập nhật trạng thái nhớ thẻ Flashcard:
    status in ['mastered' (Đã thuộc), 'learning' (Nhớ mang máng), 'review_needed' (Chưa nhớ)]
    """
    hist = load_user_history(username)
    flashcards = hist.setdefault("flashcards_mastery", {
        "mastered": [],
        "learning": [],
        "review_needed": []
    })

    for s in ["mastered", "learning", "review_needed"]:
        if item_id in flashcards.get(s, []):
            flashcards[s].remove(item_id)

    if status in flashcards:
        flashcards[status].append(item_id)

    save_user_history(username, hist)
    return flashcards


def get_user_mastery_summary(username: str) -> Dict[str, Any]:
    """Tính toán thống kê tỷ lệ làm chủ kiến thức."""
    hist = load_user_history(username)
    quiz_stats = hist.get("quiz_stats", {
        "total_quizzes_taken": 0,
        "total_questions_answered": 0,
        "total_correct_answers": 0,
        "recent_tests": []
    })
    flashcards = hist.get("flashcards_mastery", {
        "mastered": [],
        "learning": [],
        "review_needed": []
    })

    total_ans = quiz_stats.get("total_questions_answered", 0)
    total_corr = quiz_stats.get("total_correct_answers", 0)
    accuracy = round(total_corr / total_ans * 100, 1) if total_ans > 0 else 0.0

    mastered_count = len(flashcards.get("mastered", []))
    learning_count = len(flashcards.get("learning", []))
    review_count = len(flashcards.get("review_needed", []))

    # Tỷ lệ làm chủ trên tổng số 88 mô hình hạt nhân cốt lõi
    mastery_pct = round(mastered_count / 88 * 100, 1)

    return {
        "accuracy": accuracy,
        "total_quizzes": quiz_stats.get("total_quizzes_taken", 0),
        "mastered_count": mastered_count,
        "learning_count": learning_count,
        "review_count": review_count,
        "mastery_pct": min(100.0, mastery_pct),
        "recent_tests": quiz_stats.get("recent_tests", [])
    }


# =============================================================================
# 6. AI DYNAMIC QUIZ GENERATOR & FEYNMAN EVALUATION (GEMINI MULTI-KEY)
# =============================================================================
def _normalize_keys(api_keys: Union[str, List[str], tuple]) -> List[str]:
    if isinstance(api_keys, str):
        raw = [k.strip() for k in api_keys.split(",") if k.strip()]
    elif isinstance(api_keys, (list, tuple)):
        raw = [str(k).strip() for k in api_keys if str(k).strip()]
    else:
        raw = []
    seen = set()
    res = []
    for k in raw:
        if k and k not in seen:
            seen.add(k)
            res.append(k)
    return res


def generate_ai_quiz(
    api_keys: Union[str, List[str], tuple],
    model_name: str,
    category: str,
    topic: str = "Đầu tư CKVN, Khởi nghiệp & Đời sống",
    num_questions: int = 3
) -> Optional[List[Dict[str, Any]]]:
    """Sinh bộ câu hỏi trắc nghiệm tình huống mới toanh bằng AI qua Gemini đa khóa."""
    if genai is None:
        return None
    keys = _normalize_keys(api_keys)
    if not keys:
        return None

    prompt = f"""Bạn là Huấn luyện viên Tư duy Tinh hoa (Elite Mental Models Coach).
Hãy tạo {num_questions} câu hỏi trắc nghiệm tình huống thực tế hóc búa để kiểm tra phản xạ nhận diện mô hình/nguyên lý.

Danh mục yêu cầu: {category}
Chủ đề / Bối cảnh: {topic}

Yêu cầu BẮT BUỘC:
1. KHÔNG hỏi lý thuyết suông kiểu "Mô hình X là gì?". Mỗi câu PHẢI là một tình huống đời thực sinh động (Case Study) trong đầu tư, kinh doanh, hoặc học đường.
2. 4 phương án lựa chọn (A, B, C, D). Các phương án sai phải là các bẫy ngụy biện tâm lý hoặc hiểu lầm phổ biến.
3. Giải thích sâu sắc từ Chân lý gốc (First Principles) và chỉ rõ Bẫy ngụy biện của các đáp án sai.
4. Trả về DUY NHẤT một chuỗi JSON hợp lệ (không markdown block, không giải thích ngoài JSON).

Cấu trúc JSON:
[
  {{
    "id": "AI-Q-01",
    "concept": "Tên mô hình hoặc chế độ",
    "scenario": "Tình huống thực tế chi tiết...",
    "question": "Câu hỏi nhận diện...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "correct_index": 0,
    "explanation": "Giải thích tại sao đúng từ chân lý gốc...",
    "trap_analysis": "Giải thích bẫy của các phương án sai..."
  }}
]
"""

    for k in keys:
        try:
            genai.configure(api_key=k)
            model = genai.GenerativeModel(model_name=model_name or "gemini-2.5-flash")
            resp = model.generate_content(prompt)
            if resp and resp.text:
                cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", resp.text.strip())
                cleaned = re.sub(r"\s*```$", "", cleaned)
                data = json.loads(cleaned)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            continue
    return None


def evaluate_feynman_challenge(
    api_keys: Union[str, List[str], tuple],
    model_name: str,
    concept_name: str,
    concept_type: str,
    user_explanation: str
) -> Optional[Dict[str, Any]]:
    """Đánh giá bài kiểm tra Feynman: Giải thích nguyên lý phức tạp bằng ngôn ngữ giản dị nhất."""
    if genai is None:
        return None
    keys = _normalize_keys(api_keys)
    if not keys:
        return None

    prompt = f"""Bạn là Giám khảo Kỹ thuật Feynman (Feynman Technique Evaluator).
Khái niệm cần giải thích: {concept_name} ({concept_type})
Lời giải thích của người học:
\"\"\"{user_explanation}\"\"\"

Tiêu chí đánh giá của Richard Feynman:
1. Độ giản dị: Có dùng biệt ngữ học thuật (jargon) để che giấu sự thiếu hiểu biết không? (Học sinh lớp 6 có hiểu được không?)
2. Độ chính xác từ First Principles: Có nắm đúng chân lý bất biến không?
3. Tính sinh động & Ứng dụng: Ví dụ đưa ra có thuyết phục không?

Trả về DUY NHẤT một chuỗi JSON hợp lệ:
{{
  "feynman_score": 8, // Thang điểm từ 1 đến 10
  "verdict": "Xuất sắc / Khá / Còn hàn lâm / Chưa đúng bản chất",
  "praise": "Điểm sáng trong cách giải thích của bạn...",
  "blind_spots": "Lỗ hổng tư duy hoặc điểm bạn đã bỏ sót...",
  "feynman_refinement": "Cách Richard Feynman sẽ giải thích lại khái niệm này trong 2 câu cực kỳ sinh động..."
}}
"""

    for k in keys:
        try:
            genai.configure(api_key=k)
            model = genai.GenerativeModel(model_name=model_name or "gemini-2.5-flash")
            resp = model.generate_content(prompt)
            if resp and resp.text:
                cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", resp.text.strip())
                cleaned = re.sub(r"\s*```$", "", cleaned)
                data = json.loads(cleaned)
                if isinstance(data, dict):
                    return data
        except Exception:
            continue
    return None
