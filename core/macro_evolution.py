# -*- coding: utf-8 -*-
"""
Module Macro Evolution & Elite Hidden Laws (Lăng kính Thế cuộc & Quy luật Tinh hoa).
Bóc tách dòng chảy lịch sử văn minh và cơ chế vận hành ngầm dưới lăng kính First Principles:
- 5 Kỷ nguyên kinh tế (Survival -> Agricultural -> Industrial -> Information -> AI & Authenticity)
- 8 Mật mã vận hành ngầm của giới Elite (The Hidden Elite Playbook)
- AI Macro Radar: Máy quét giải mã thế cuộc theo First Principles
"""

from __future__ import annotations

import json
import re
import os
from typing import Dict, List, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from core.farrow_engine import get_all_gemini_api_keys

# -----------------------------------------------------------------------------
# 1. TRỤC TIẾN HÓA 5 KỶ NGUYÊN KINH TẾ (THE 5 CIVILIZATIONAL ERAS)
# -----------------------------------------------------------------------------
CIVILIZATIONAL_ERAS: List[Dict[str, Any]] = [
    {
        "id": "survival",
        "era_number": 1,
        "name": "Thời Đại Săn Bắt & Hái Lượm",
        "subtitle": "Kinh Tế Sinh Tồn (Survival Economy)",
        "icon": "🏹",
        "timeframe": "200.000 năm trước – 10.000 TCN",
        "core_resource": "Lãnh thổ tự nhiên (Rừng nguyên sinh, sông ngòi, đàn thú hoang).",
        "energy_tech": "Năng lượng sinh học cơ bắp, lửa trại, công cụ đá thô sơ.",
        "constraint": "Sức lực sinh học hữu hạn và sự phụ thuộc 100% vào thời tiết, mùa màng tự nhiên.",
        "economic_model": "Tiêu thụ trực tiếp (Zero Surplus) — Kiếm được bao nhiêu ăn bấy nhiêu, không có tích lũy.",
        "turning_point": "Dân số chạm ngưỡng tải sinh học (Carrying Capacity). Thức ăn tự nhiên không kịp tái tạo -> Áp lực tuyệt chủng buộc con người phải tìm cách thuần hóa và kiểm soát tự nhiên thay vì phụ thuộc thụ động.",
        "commoditized": "Kỹ năng rình bắt thú hoang và lang thang tìm quả dại đơn lẻ.",
        "new_scarce_asset": "Đất đai màu mỡ định cư, hạt giống ngũ cốc thuần hóa, gia súc sinh sản.",
        "elite_leverage": "Sức mạnh thể chất của thủ lĩnh bộ tộc, kinh nghiệm truyền khẩu của già làng.",
        "associated_models": [
            {"id": "carrying_capacity", "name": "Sức Chứa Môi Trường (Carrying Capacity)"},
            {"id": "malthusian_trap", "name": "Bẫy Malthus"},
            {"id": "energy_limits", "name": "Định Luật Bảo Toàn Năng Lượng"},
        ],
        "associated_modes": ["First Principles", "Tư duy Thực nghiệm vi mô"],
        "deep_dive": (
            "Ở thời kỳ này, thặng dư bằng 0 đồng nghĩa với việc không tồn tại khái niệm của cải tích lũy, "
            "nhà nước hay quân đội chuyên nghiệp. Mọi cá nhân đều phải dùng 100% thời gian thức để tìm calo. "
            "Bài học nguyên bản: Khi một hệ thống chạm trần năng lượng sinh học, nó buộc phải chuyển dịch pha (Phase Transition) "
            "hoặc tự sụp đổ."
        ),
    },
    {
        "id": "agricultural",
        "era_number": 2,
        "name": "Thời Đại Nông Nghiệp",
        "subtitle": "Kinh Tế Đất Đai & Thặng Dư Khởi Thủy (Land & Feudal Economy)",
        "icon": "🌾",
        "timeframe": "10.000 TCN – Giữa thế kỷ 18",
        "core_resource": "Đất Đai (Land) & Nguồn Nước. Ai nắm đất, kẻ đó có quyền lực tối cao (Vua chúa, Lãnh chúa, Địa chủ).",
        "energy_tech": "Quang hợp (chuyển quang năng thành lương thực), sức kéo gia súc, công cụ kim loại (Đồng, Sắt), kênh thủy lợi.",
        "constraint": "Diện tích đất canh tác màu mỡ hữu hạn và tốc độ quang hợp tự nhiên của cây trồng.",
        "economic_model": "Nông nghiệp định cư, Chế độ Phong kiến. Lần đầu tiên con người tạo ra THẶNG DƯ (Surplus).",
        "turning_point": "Vướng Bẫy Malthus (Malthusian Trap): Đất đai tăng theo cấp số cộng (+), nhưng dân số sinh sản theo cấp số nhân (×). Định kỳ, dân số vượt quá sản lượng lương thực -> Nạn đói, dịch bệnh, chiến tranh nổ ra để reset hệ thống.",
        "commoditized": "Lao động săn bắt thú hoang tự do.",
        "new_scarce_asset": "Động cơ hơi nước, máy dệt cơ khí, mỏ khoáng sản than đá năng lượng tập trung.",
        "elite_leverage": "Đòn bẩy nhân lực: Quyền lực tuyệt đối chi phối tá điền, nô lệ và quân đội thường trực bảo vệ bờ cõi.",
        "associated_models": [
            {"id": "malthusian_trap", "name": "Bẫy Malthus & Giới Hạn Sinh Học"},
            {"id": "ricardian_rent", "name": "Địa Tô Ricardo & Lợi Tức Giảm Dần"},
            {"id": "opportunity_cost", "name": "Chi Phí Cơ Hội"},
            {"id": "incentives", "name": "Động Lực Hệ Thống (Incentives)"},
        ],
        "associated_modes": ["First Principles", "Tư duy Bậc hai", "Lý thuyết Trò chơi"],
        "deep_dive": (
            "Thặng dư calo sinh ra tầng lớp không cần làm ruộng: học giả, linh mục, quan lại, binh lính. "
            "Từ đó, chữ viết, luật pháp, tiền tệ và nhà nước ra đời. Tuy nhiên, giới tinh hoa phong kiến "
            "vẫn bị khóa chặt bởi định luật quang hợp: họ không thể tạo thêm calo nếu không cướp thêm đất. "
            "Chiến tranh mở rộng bờ cõi là bài toán tối ưu duy nhất thời đại đó."
        ),
    },
    {
        "id": "industrial",
        "era_number": 3,
        "name": "Thời Đại Công Nghiệp",
        "subtitle": "Kinh Tế Tư Bản, Máy Móc & Năng Lượng Hóa Thạch (Industrial Capitalism)",
        "icon": "🏭",
        "timeframe": "Giữa thế kỷ 18 – Cuối thế kỷ 20",
        "core_resource": "Tư Bản (Capital) & Máy Móc (Tư liệu sản xuất). Đất đai lùi lại làm thứ cấp.",
        "energy_tech": "Năng lượng hóa thạch đậm đặc (Than đá, Dầu mỏ), Động cơ hơi nước, Điện lực, Dây chuyền lắp ráp.",
        "constraint": "Kênh phân phối vật lý, tìm kiếm thị trường tiêu thụ thặng dư, và chi phí logistics toàn cầu.",
        "economic_model": "Sản xuất hàng loạt (Mass Production), Kinh tế quy mô (Economies of Scale), Đô thị hóa, Tập đoàn cổ phần.",
        "turning_point": "Khi máy móc sản xuất quá nhanh, sản lượng bùng nổ theo hàm mũ. Nút thắt không còn là sản xuất ra cái áo hay chiếc xe, mà là điều phối chuỗi cung ứng, tiếp thị, và giảm thiểu chi phí giao dịch thông tin.",
        "commoditized": "Sức lao động cơ bắp của công nhân thủ công.",
        "new_scarce_asset": "Băng thông viễn thông, chip bán dẫn, dữ liệu người dùng, thuật toán tối ưu hóa.",
        "elite_leverage": "Đòn bẩy tài chính & máy móc: Các ông trùm tư bản (Vanderbilt, Rockefeller, Ford) sở hữu nhà máy và hệ thống đường sắt.",
        "associated_models": [
            {"id": "economies_of_scale", "name": "Kinh Tế Quy Mô"},
            {"id": "creative_destruction", "name": "Phá Hủy Sáng Tạo (Schumpeter)"},
            {"id": "network_effects", "name": "Hiệu Ứng Mạng Lưới"},
            {"id": "coase_theorem", "name": "Bản Chất Công Ty & Chi Phí Giao Dịch (Coase)"},
        ],
        "associated_modes": ["First Principles", "Tư duy Đòn bẩy Tối thượng", "Tư duy Hệ thống"],
        "deep_dive": (
            "Lần đầu tiên trong lịch sử nhân loại, sự thịnh vượng được tách rời khỏi giới hạn đất đai. "
            "Một nhà máy luyện thép 10 ha có thể tạo ra của cải gấp 10.000 ha ruộng lúa. "
            "Thế giới chuyển từ tư duy Zero-sum (Cướp đất) sang Positive-sum (Mở rộng quy mô công nghiệp)."
        ),
    },
    {
        "id": "information",
        "era_number": 4,
        "name": "Thời Đại Thông Tin & Internet",
        "subtitle": "Kinh Tế Tri Thức, Phần Mềm & Dòng Chú Ý (Knowledge & Attention Economy)",
        "icon": "🌐",
        "timeframe": "Thập niên 1990 – 2022",
        "core_resource": "Mã nguồn (Code), Dữ liệu (Data), và Dòng Chú Ý (Human Attention).",
        "energy_tech": "Điện tử bán dẫn Silicon, Cáp quang Internet toàn cầu, Điện toán đám mây, Thuật toán phân phối nội dung.",
        "constraint": "Sự khan hiếm của thời gian và dung lượng xử lý chú ý của não bộ con người (Attention Span).",
        "economic_model": "Chi Phí Biên Bằng Không (Zero Marginal Cost) cho việc sao chép phần mềm. Mô hình Người thắng thâu tóm tất cả (Winner-takes-all).",
        "turning_point": "Sự bão hòa thông tin và sự xuất hiện của Trí tuệ Nhân tạo tạo sinh (Generative AI). Chi phí tạo ra mã code, chữ viết và hình ảnh lao dốc thẳng đứng về 0đ. Sự xuất hiện của 'Rác thông tin' (AI Slop) phá vỡ niềm tin vào không gian số mở.",
        "commoditized": "Lưu trữ dữ liệu, băng thông truyền dẫn, và phần mềm đóng gói cơ bản.",
        "new_scarce_asset": "Điện toán AI chuyên biệt (Compute/FLOPs), Nguồn năng lượng điện tinh khiết, và Tính Chân Thực Con Người (Human Authenticity).",
        "elite_leverage": "Đòn bẩy không cần xin phép (Permissionless Leverage - Naval Ravikant): Code & Media. Một kỹ sư phần mềm có thể phục vụ 1 tỷ người dùng mà không cần thêm nhân công.",
        "associated_models": [
            {"id": "zero_marginal_cost", "name": "Chi Phí Biên Bằng 0"},
            {"id": "winner_takes_all", "name": "Winner-Take-All & Phân Phối Lũy Thừa"},
            {"id": "attention_economy", "name": "Kinh Tế Dòng Chú Ý"},
            {"id": "metcalfe_law", "name": "Định Luật Metcalfe"},
        ],
        "associated_modes": ["First Principles", "Tùy chọn (Optionality)", "Tư duy Xác suất & Đuôi dày"],
        "deep_dive": (
            "Nếu bạn bán xe hơi, bạn cần sắt thép và công nhân cho từng chiếc xe mới. "
            "Nhưng nếu bạn viết hệ điều hành Windows hay thuật toán Google Search, chi phí để phục vụ người dùng thứ 1 tỷ là 0 đồng. "
            "Quyền lực không còn nằm ở nhà máy xi măng hay giếng dầu, mà nằm ở thuật toán phân phối dòng chú ý của nhân loại."
        ),
    },
    {
        "id": "ai_authenticity",
        "era_number": 5,
        "name": "Kỷ Nguyên AI & Sự Khan Hiếm Chân Thực",
        "subtitle": "Dồi Dào Nhân Tạo & Kinh Tế Xác Thực (Synthetic Abundance & Proof Economy)",
        "icon": "🤖",
        "timeframe": "2023 – Tương lai (Đang định hình)",
        "core_resource": "Năng lượng Điện hạt nhân/Sạch (Watts), Điện toán chuyên biệt (FLOPs/Compute), Tính Chân Thực Con Người (Authenticity), Mạng Lưới Niềm Tin Cao (High-Trust Networks).",
        "energy_tech": "Mô hình ngôn ngữ lớn (LLMs), AI Agents tự hành, Lò phản ứng hạt nhân SMR, Robot hình người, Mật mã học xác thực (ZK-Proof, World ID).",
        "constraint": "Công suất lưới điện vật lý, vật liệu làm mát siêu trung tâm dữ liệu, và Niềm tin giữa người với người.",
        "economic_model": "Dồi Dào Nhân Tạo (Synthetic Abundance) cho nhận thức; Định giá siêu cao cho những gì thuộc Thế giới Vật lý & Sự Xác thực Con người (Proof-of-Personhood).",
        "turning_point": "Thuyết Internet Chết (Dead Internet): Web mở tràn ngập AI Slop rẻ tiền. Con người rút lui khỏi không gian công cộng vào các ốc đảo khép kín (Gated Communities).",
        "commoditized": "Soạn thảo văn bản, viết code cơ bản, thiết kế đồ họa thương mại, lập trình viên junior, nội dung mạng xã hội phổ thông.",
        "new_scarce_asset": "1. Chứng minh con người thật (Proof-of-Personhood)\n2. Định giá cho sự không hoàn hảo (Imperfection Premium)\n3. Trải nghiệm vật lý trực tiếp (Live Presence)\n4. Năng lượng điện tinh khiết cấp cho AI.",
        "elite_leverage": "Đội quân AI Agents tự trị 24/7 + Quyền tiếp cận độc quyền các Ốc đảo Tín hiệu Cao (High-Signal Private Rooms).",
        "associated_models": [
            {"id": "complementary_scarcity", "name": "Định Lý Khan Hiếm Bổ Trợ"},
            {"id": "dead_internet", "name": "Thuyết Internet Chết & Tỷ Lệ Tín Hiệu/Nhiễu"},
            {"id": "costly_signaling", "name": "Phí Tổn Phát Tín Hiệu (Costly Signaling)"},
            {"id": "antifragility", "name": "Tính Phản Dễ Vỡ (Antifragility)"},
        ],
        "associated_modes": ["First Principles", "Tư duy Bậc hai", "Tư duy Đảo ngược (Inversion)", "Tư duy Đa quy mô Thời gian"],
        "deep_dive": (
            "Định lý bất hủ của kinh tế học: 'Khi một thứ trở nên vô tận và miễn phí, giá trị kinh tế sẽ ngay lập tức "
            "dịch chuyển sang thứ khan hiếm gắn liền với nó.' Nhận thức cơ bản có giá bằng 0, do đó thứ đắt đỏ nhất "
            "sẽ là: Danh tính sinh học thật, những cái bắt tay trực tiếp, sự vụng về chân thật mang tính người, "
            "và nguồn điện hạt nhân sạch nuôi sống các cụm máy chủ AI."
        ),
    },
]

# -----------------------------------------------------------------------------
# 2. BỘ MẬT MÃ 8 QUY TẮC VẬN HÀNH NGẦM CỦA GIỚI ELITE (THE ELITE PLAYBOOK)
# -----------------------------------------------------------------------------
ELITE_HIDDEN_LAWS: List[Dict[str, Any]] = [
    {
        "id": "complementary_scarcity",
        "number": 1,
        "title": "Định Lý Khan Hiếm Bổ Trợ (The Law of Complementary Scarcity)",
        "axiom": "Khi một nguồn lực trở nên miễn phí và vô tận, giá trị kinh tế không bốc hơi, mà dồn tụ vào nút thắt cổ chai khan hiếm liền kề.",
        "icon": "⚖️",
        "physics_math_basis": "Định luật bảo toàn giá trị kinh tế: Trong một hệ thống sản xuất đa yếu tố Y = f(A, B), nếu chi phí của A tiến về 0, thặng dư biên của B sẽ bùng nổ theo hàm mũ để cân bằng giá trị thặng dư toàn phần.",
        "mass_perception": "Đám đông lo sợ hoặc phấn khích trước thứ vừa trở nên miễn phí (Ví dụ: 'AI làm ảnh và viết bài miễn phí thì ai cũng giàu!'). Họ lao vào làm thợ prompt hoặc cạnh tranh tạo nội dung giá rẻ.",
        "elite_execution": "Giới Elite không bao giờ cạnh tranh với thứ đang rớt giá về 0. Họ hỏi: 'Để thứ miễn phí này chạy được, nó buộc phải quỳ lạy trước nguyên liệu đầu vào nào?' -> Họ âm thầm thâu tóm: Điện hạt nhân, Chip bán dẫn TSMC, Bất động sản làm trung tâm dữ liệu, và Bản quyền dữ liệu gốc không công khai.",
        "real_world_case": "Thời kỳ đào vàng California 1849: Hàng vạn thợ đào vàng trắng tay, nhưng Levi Strauss bán quần Jean và Sam Brannan bán xẻng/cuốc trở thành triệu phú. Năm 2024: Các công ty tạo nội dung AI cạnh tranh khốc liệt, trong khi Nvidia (bán cuốc xẻng GPU) và Constellation Energy (bán điện hạt nhân cho Microsoft) thu trọn thặng dư.",
        "linked_models": ["Cung & Cầu", "Lợi Nhuận Biên", "Nút Thắt Cổ Chai (Theory of Constraints)"],
        "linked_modes": ["First Principles", "Tư duy Bậc hai"],
        "self_inquiry": "Kỹ năng hoặc tài sản hiện tại của tôi đang là thứ 'rớt giá về 0' hay là 'nút thắt khan hiếm bổ trợ'?",
    },
    {
        "id": "cantillon_effect",
        "number": 2,
        "title": "Hiệu Ứng Cantillon & Vị Thế Cận Nguồn Bơm (Proximity to the Spigot)",
        "axiom": "Tiền tệ, công nghệ và thông tin mới không lan tỏa đồng đều. Ai đứng gần miệng vòi bơm nhất sẽ thu hoạch 90% giá trị nguyên bản trước khi sự pha loãng xảy ra.",
        "icon": "💧",
        "physics_math_basis": "Hiện tượng trễ pha và ma sát entropy trong mạng lưới phân tán: Dòng chảy thanh khoản mất thời gian để thẩm thấu qua các nút mạng, tạo ra cửa sổ chênh lệch định giá (Arbitrage Window) cực lớn ở nút gốc.",
        "mass_perception": "Tin rằng thị trường là hoàn hảo và công bằng; chờ đợi tin tức xuất hiện trên báo chí hoặc TV rồi mới hành động; chịu đựng lạm phát và sự mất giá của đồng tiền/kỹ năng ở tầng tiêu thụ cuối cùng.",
        "elite_execution": "Luôn định vị bản thân ở tầng thượng nguồn (Upstream / Primary Liquidity). Khi ngân hàng trung ương bơm tiền, họ vay với lãi suất cực thấp để gom tài sản cứng trước khi giá tăng; khi AI ra đời, họ đầu tư vào hạ tầng gốc (Foundation Labs, GPU clusters) trước khi ứng dụng chạm tới người dùng cuối.",
        "real_world_case": "Trong đại dịch 2020: Các gói cứu trợ hàng ngàn tỷ USD khiến thị trường chứng khoán và bất động sản của giới thượng lưu tăng vọt ngay tháng thứ 3, trong khi người lao động phổ thông phải chờ 1-2 năm sau mới nhận tiền và chịu lạm phát thực phẩm tăng 30%.",
        "linked_models": ["Hiệu Ứng Cantillon", "Bất Đối Xứng Thông Tin", "Chênh Lệch Giá (Arbitrage)"],
        "linked_modes": ["Tư duy Hệ thống", "Tư duy Đa quy mô Thời gian"],
        "self_inquiry": "Vị trí của tôi trong chuỗi cung ứng thông tin/dòng tiền đang cách miệng vòi bơm bao nhiêu bước trung gian?",
    },
    {
        "id": "convex_asymmetry",
        "number": 3,
        "title": "Bất Đối Xứng Lồi & Tính Phản Dễ Vỡ (Convex Asymmetry & Antifragility)",
        "axiom": "Đừng bao giờ chơi trò đối xứng rủi ro. Khoanh vùng tổn thất tối đa ở mức nhỏ nhất, nhưng mở toang tiềm năng sinh lời vô hạn.",
        "icon": "🛡️",
        "physics_math_basis": "Bất đẳng thức Jensen trong lý thuyết xác suất: Hàm lồi f(E[x]) <= E[f(x)]. Khi một hệ thống có cấu trúc lồi (Convex Payoff), sự biến động, hỗn loạn và không chắc chắn sẽ làm gia tăng giá trị kỳ vọng thay vì hủy diệt nó.",
        "mass_perception": "Bán thời gian lấy lương cố định hàng tháng (Cấu trúc Lõm - Concave): Lợi nhuận bị chặn trần (lương cố định), nhưng rủi ro tổn thất là vô hạn (bị sa thải, đột quỵ, công ty phá sản = mất 100% thu nhập).",
        "elite_execution": "Thiết kế vị thế theo chiến lược Quả tạ (Barbell Strategy - Nassim Taleb): 90% tài sản/thời gian đặt ở nơi cực kỳ an toàn, 10% đặt vào các quyền chọn có tiềm năng sinh lời phi tuyến 100x - 1000x (Cổ phần khởi nghiệp, tài sản trí tuệ gốc, công nghệ đột phá). Biến động thị trường càng lớn, họ càng mạnh.",
        "real_world_case": "Warren Buffett giữ hàng trăm tỷ USD tiền mặt trong giai đoạn bình lặng; khi khủng hoảng 2008 nổ ra, ông tung tiền mua cổ phiếu ưu đãi của Goldman Sachs và GE với điều khoản siêu lồi, thâu tóm thặng dư khổng lồ khi thị trường hồi phục.",
        "linked_models": ["Tính Phản Dễ Vỡ (Antifragile)", "Quyền Chọn Thực (Real Options)", "Phân Phối Đuôi Dày (Fat-Tailed Distribution)"],
        "linked_modes": ["Tùy chọn (Optionality)", "Tư duy Đảo ngược (Inversion)"],
        "self_inquiry": "Nếu một biến cố tồi tệ nhất xảy ra vào ngày mai, tôi sẽ mất bao nhiêu? Và nếu một điều may mắn bất ngờ đến, tôi có hứng trọn được hàm mũ không?",
    },
    {
        "id": "gated_enclaves",
        "number": 4,
        "title": "Ốc Đảo Tín Hiệu Cao vs Rạp Xiếc Đại Chúng (High-Trust Gated Enclaves)",
        "axiom": "Không gian công cộng mở luôn suy thoái thành bãi rác thông tin. Giao dịch thực sự và liên minh lớn chỉ diễn ra trong các căn phòng kín có bảo chứng.",
        "icon": "🏰",
        "physics_math_basis": "Định luật Gresham mở rộng cho thông tin: Thông tin xấu và giật gân (Nhiễu) luôn xua đuổi thông tin có giá trị (Tín hiệu) trong môi trường mở có chi phí phát tán = 0. Tỷ lệ Signal-to-Noise tiến về 0.",
        "mass_perception": "Dành hàng giờ lướt TikTok, Facebook, tranh cãi với người lạ trên mạng; coi mạng xã hội đại chúng là nguồn tiếp nhận tri thức và tin tưởng vào các thông cáo báo chí công khai.",
        "elite_execution": "Rút lui hoàn toàn khỏi các 'rạp xiếc công cộng'. Xây dựng các mạng lưới kín (Chatham House Rule, Private Dinners, Closed Alpha Groups) với rào cản gia nhập cực cao (phải có bảo lãnh nhân thân). Ở đó, chi phí niềm tin = 0, thông tin chính xác 99%, và các thỏa thuận hàng tỷ đô được chốt chỉ bằng một cái gật đầu.",
        "real_world_case": "Diễn đàn Kinh tế Thế giới (WEF Davos) hay các hội nghị kín Allen & Co Sun Valley: Các bài phát biểu trên sân khấu chỉ là trình diễn truyền thông; các thương vụ sáp nhập M&A hàng chục tỷ USD (như Disney mua Pixar) diễn ra khi các CEO cùng đi dạo dọc bờ suối trong khuôn viên được bảo vệ nghiêm ngặt.",
        "linked_models": ["Tỷ Lệ Tín Hiệu / Nhiễu", "Song Đề Tù Nhân Lặp Lại", "Luật Số Dunbar"],
        "linked_modes": ["Tư duy Lý thuyết Trò chơi", "Tư duy Xác suất & Bayes"],
        "self_inquiry": "Vòng tròn 5 người tôi thảo luận chiến lược mỗi tuần đang mang lại 'Tín hiệu chất lượng cao' hay chỉ là 'Nhiễu loạn cảm xúc'?",
    },
    {
        "id": "permissionless_leverage",
        "number": 5,
        "title": "Đòn Bẩy Không Cần Xin Phép (Permissionless Leverage)",
        "axiom": "Của cải của bạn được quyết định bởi loại đòn bẩy bạn nắm giữ. Người làm chủ đòn bẩy không cần xin phép sẽ nhân bản năng lực gấp 10.000 lần mà không cần nuôi bộ máy cồng kềnh.",
        "icon": "⚡",
        "physics_math_basis": "Hàm sản xuất phi tuyến: Đòn bẩy truyền thống (Lao động, Vốn) tăng trưởng theo cấp số cộng hoặc phụ thuộc sự cấp phép của người khác. Đòn bẩy hiện đại (Code, Media, AI Agents) có chi phí biên = 0 và nhân bản tự động 24/7.",
        "mass_perception": "Nghĩ rằng muốn thành công phải tuyển thật nhiều nhân viên, xin ngân hàng cấp tín dụng, hoặc van xin sự công nhận từ cấp trên / ban ngành.",
        "elite_execution": "Trở thành 'Cá nhân Tự trị' (Sovereign Individual) bằng cách kết hợp Code + Media + AI Agents. Một cá nhân kiệt xuất có thể viết phần mềm hoặc sản xuất nội dung phục vụ hàng triệu người trên toàn cầu khi đang ngủ, không phụ thuộc vào giờ hành chính hay bất kỳ ông chủ nào.",
        "real_world_case": "Notch (Markus Persson) tự tay lập trình game Minecraft trong phòng ngủ và bán cho Microsoft với giá 2,5 tỷ USD với đội ngũ nhân sự siêu nhỏ. Ngày nay, một nhà sáng lập với 5 AI agents có thể vận hành công ty ARR 10 triệu USD.",
        "linked_models": ["Đòn Bẩy Archimedes", "Chi Phí Biên Bằng Không", "Cá Nhân Tự Trị (Sovereign Individual)"],
        "linked_modes": ["First Principles", "Tư duy Đòn bẩy Tối thượng"],
        "self_inquiry": "Tôi đang kiếm tiền bằng cách cho thuê thời gian sinh học, hay bằng một cỗ máy đòn bẩy vẫn tự chạy khi tôi đang ngủ?",
    },
    {
        "id": "coase_transaction_cost",
        "number": 6,
        "title": "Chi Phí Giao Dịch & Định Lý Coase Kỷ Nguyên AI (Transaction Costs & The Lean Nucleus)",
        "axiom": "Quy mô tối ưu của một tổ chức tỷ lệ thuận với chi phí giao dịch trên thị trường mở. Khi AI kéo chi phí giao dịch về 0, các tập đoàn khổng lồ cồng kềnh sẽ bị chia nhỏ thành các hạt nhân vi mô tinh gọn.",
        "icon": "🔬",
        "physics_math_basis": "Định lý Ronald Coase (Giải Nobel 1991): Công ty hình thành để giảm chi phí tìm kiếm, đàm phán và giám sát. Khi công nghệ số và AI biến chi phí phối hợp ngoài thị trường rẻ hơn chi phí quan liêu nội bộ, kích thước công ty sẽ co lại về hạt nhân.",
        "mass_perception": "Ảo tưởng về quy mô nhân sự: Xem việc công ty có 10.000 nhân viên, tòa nhà chọc trời đồ sộ là biểu tượng của sức mạnh vô địch.",
        "elite_execution": "Tái cấu trúc tổ chức thành một 'Hạt nhân Tinh hoa' (Lean Core) chỉ gồm 3-5 người giữ chiến lược và phân bổ vốn; toàn bộ khâu thực thi (viết code, kế toán, marketing, CSKH, pháp chế cơ bản) được ủy quyền cho AI Agents và mạng lưới chuyên gia độc lập.",
        "real_world_case": "Midjourney đạt doanh thu hơn 200 triệu USD/năm chỉ với khoảng 40 nhân viên và không hề có đội ngũ sales truyền thống. Trong khi đó, các công ty truyền thống cùng quy mô doanh thu phải gánh bộ máy 1.500 người với chi phí hành chính khổng lồ.",
        "linked_models": ["Chi Phí Giao Dịch Coase", "Lý Thuyết Đại Diện (Principal-Agent)", "Mô-đun Hóa Hệ Thống"],
        "linked_modes": ["Tư duy Hệ thống", "First Principles"],
        "self_inquiry": "Bộ máy làm việc của tôi đang chịu bao nhiêu phần trăm 'chi phí quan liêu nội bộ' thay vì tạo ra giá trị trực tiếp?",
    },
    {
        "id": "nth_order_thinking",
        "number": 7,
        "title": "Tư Duy Bậc N & Đọc Vị Dòng Dịch Chuyển Năng Lượng (N-th Order Energy Tracking)",
        "axiom": "Đám đông chỉ phản ứng với tác động Bậc 1 (Sự kiện trước mắt). Elite đọc vị chuỗi phản ứng dây chuyền ở Bậc 2, Bậc 3 và đón đầu tại nơi dòng năng lượng sẽ tụ về.",
        "icon": "🌊",
        "physics_math_basis": "Định luật bảo toàn năng lượng và hiệu ứng lan truyền (Cascade Effect): Mọi cú hích trong một hệ thống phức tạp đều tạo ra phản ứng thứ cấp và phản hồi trễ (Feedback Delays), trong đó tác động dài hạn thường trái ngược hoàn toàn với tác động tức thời.",
        "mass_perception": "Nhìn thấy xe điện ra đời -> Mua cổ phiếu xe điện. Nhìn thấy AI bùng nổ -> Mua cổ phiếu công ty phần mềm ứng dụng AI.",
        "elite_execution": "Truy vết chuỗi phản ứng: Xe điện bùng nổ -> Lưới điện quá tải và nhu cầu đồng/lithium tăng vọt -> Đầu tư trạm biến áp và mỏ kim loại. AI bùng nổ -> Nhu cầu điện toán ngốn hàng terawatt điện -> Đầu tư lò phản ứng hạt nhân SMR, hệ thống làm mát chất lỏng, và hợp đồng bao tiêu điện năng sạch dài hạn.",
        "real_world_case": "Khi cơn sốt AI bùng nổ năm 2023, trong khi đám đông tranh cãi về ChatGPT thì các quỹ đầu tư lớn nhất thế giới đã âm thầm mua gom cổ phần của các nhà máy điện hạt nhân đã đóng cửa (như nhà máy Three Mile Island) để chuẩn bị bán điện độc quyền cho Microsoft và Amazon.",
        "linked_models": ["Tư Duy Bậc Hai (Second-Order)", "Phản Hồi Trễ & Vòng Lặp", "Bảo Toàn Năng Lượng"],
        "linked_modes": ["Tư duy Bậc hai", "Tư duy Đa quy mô Thời gian"],
        "self_inquiry": "Sau khi sự kiện này xảy ra, điều gì BẮT BUỘC phải diễn ra tiếp theo ở bước 2 và bước 3 mà đám đông chưa nhìn thấy?",
    },
    {
        "id": "costly_signaling",
        "number": 8,
        "title": "Phí Tổn Tín Hiệu & Bằng Chứng Lao Động Thật (Costly Signaling & Biological Proof-of-Work)",
        "axiom": "Khi mọi lời nói, hình ảnh và cam kết đều có thể được giả lập miễn phí bằng AI, chỉ những tín hiệu đi kèm sự trả giá thực tế (Mồ hôi, Uy tín, Rủi ro cá nhân) mới có giá trị.",
        "icon": "💎",
        "physics_math_basis": "Nguyên lý phát tín hiệu tốn kém của Zahavi (Zahavi's Handicap Principle): Một tín hiệu chỉ đáng tin cậy khi kẻ phát tín hiệu phải chịu một chi phí mà kẻ giả mạo không thể kham nổi mà không chịu thiệt hại nặng nề.",
        "mass_perception": "Tin vào những hồ sơ CV bóng bẩy, những slide thuyết trình hào nhoáng, hoặc những lời hứa hẹn hoa mỹ trên mạng xã hội mà không kiểm chứng chi phí thực tế đằng sau.",
        "elite_execution": "Đòi hỏi nguyên tắc 'Skin in the game' (Có da thịt trong cuộc chơi): Đối tác phải bỏ tiền thật, chịu trách nhiệm pháp lý cá nhân, hoặc có lịch sử uy tín đã được thử lửa qua khủng hoảng. Họ đánh giá cao bằng chứng thực nghiệm (Proof of Work) hơn là bằng chứng bằng cấp (Proof of Degree).",
        "real_world_case": "Tại sao các trường đại học Ivy League hay các câu lạc bộ quý tộc vẫn duy trì các bài kiểm tra khắc nghiệt và quy trình tuyển sinh tốn kém? Vì đó là 'Costly Signal' chứng minh ứng viên có sức chịu đựng kỷ luật phi thường, điều mà không bằng cấp mua bằng tiền nào có thể ngụy tạo.",
        "linked_models": ["Phát Tín Hiệu Tốn Kém (Costly Signaling)", "Skin In The Game (Rủi Ro Đồng Hành)", "Chọn Lọc Tự Nhiên"],
        "linked_modes": ["Tư duy Thực nghiệm", "Tư duy Lý thuyết Trò chơi"],
        "self_inquiry": "Những cam kết của tôi và đối tác có đi kèm cái giá phải trả nếu thất bại không? Hay đây chỉ là những tín hiệu rẻ tiền dễ ngụy tạo?",
    },
]

# -----------------------------------------------------------------------------
# 3. DANH SÁCH CÁC KỊCH BẢN MẪU CHO RADAR
# -----------------------------------------------------------------------------
SAMPLE_MACRO_TRENDS: List[Dict[str, str]] = [
    {
        "title": "🤖 AI Agents Tự Hành Thay Thế 80% Công Việc Văn Phòng",
        "query": "Sự xuất hiện của các AI Agents tự hành có khả năng lập trình, viết báo cáo, xử lý dữ liệu và vận hành quy trình kinh doanh 24/7 với chi phí tiệm cận 0.",
    },
    {
        "title": "⚡ Cuộc Khủng Hoảng Năng Lượng Điện Cho Trung Tâm Dữ Liệu AI",
        "query": "Các siêu trung tâm dữ liệu AI dự kiến tiêu thụ lượng điện khổng lồ vượt quá khả năng cung ứng của lưới điện truyền thống, dẫn đến cuộc đua năng lượng hạt nhân sạch SMR.",
    },
    {
        "title": "📉 Dân Số Già Hóa Toàn Cầu & Sự Suy Giảm Tỷ Lệ Sinh",
        "query": "Các nền kinh tế lớn (Đông Á, châu Âu) bước vào thời kỳ dân số suy giảm nhanh, quỹ hưu trí thâm hụt và lực lượng lao động trẻ co cụm.",
    },
    {
        "title": "💵 Xu Hướng Hủy USD Hóa (De-Dollarization) & Tiền Số Ngân Hàng Trung Ương (CBDC)",
        "query": "Khối BRICS mở rộng đẩy mạnh thanh toán nội tệ, trong khi các ngân hàng trung ương thử nghiệm CBDC nhằm kiểm soát dòng tiền và thắt chặt quản lý tài chính số.",
    },
    {
        "title": "🚗 Xe Điện Tự Hành (Robotaxi) & Logistics Tự Động Hóa Toàn Diện",
        "query": "Xe tự hành thương mại hóa quy mô lớn kéo chi phí vận chuyển hành khách và giao nhận hàng hóa xuống dưới giá vé xe buýt, xóa bỏ nghề tài xế truyền thống.",
    },
]

# -----------------------------------------------------------------------------
# 4. BỘ MÁY AI MACRO RADAR
# -----------------------------------------------------------------------------
MACRO_RADAR_SYSTEM_PROMPT = """Bạn là Elite Macro Strategist & First-Principles Master (Chuyên gia Phân tích Thế cuộc & Cố vấn Chiến lược Tinh hoa).

Nhiệm vụ của bạn: Tiếp nhận một xu hướng công nghệ, kinh tế hoặc biến động xã hội vĩ mô, sau đó bóc tách tận gốc rễ cơ chế chuyển dịch quyền lực và tài sản theo First Principles.

BẮT BUỘC trả lời bằng một JSON hợp lệ duy nhất, không thêm markdown bao bọc ngoài JSON, không thêm lời dẫn:
{
  "trend_summary": "Tóm tắt bản chất gốc rễ của xu hướng này trong 2 câu ngắn gọn",
  "transaction_costs_impact": "Chi phí giao dịch (tìm kiếm, niềm tin, đàm phán, thực thi) nào bị kéo tụt thẳng đứng?",
  "commoditized_assets": [
    {"asset": "Tên nguồn lực bị trượt giá về 0", "why": "Lý do sụp đổ giá trị biên"}
  ],
  "complementary_scarcities": [
    {"asset": "Tên nút thắt khan hiếm mới lên ngôi", "why": "Lý do tại sao giá trị kinh tế bắt buộc phải tụ về đây"}
  ],
  "elite_strategic_moves": [
    "Nước cờ 1 mà giới tinh hoa âm thầm triển khai...",
    "Nước cờ 2...",
    "Nước cờ 3..."
  ],
  "activated_mental_models": [
    {"model_name": "Tên mô hình hạt nhân (từ 88 mô hình)", "mechanism": "Cách mô hình này giải thích sự chuyển dịch"}
  ],
  "action_playbook_for_individual": [
    "Khuyến nghị 1: Điều gì người học cần DỪNG làm ngay...",
    "Khuyến nghị 2: Năng lực/Tài sản khan hiếm nào cần TÍCH LŨY...",
    "Khuyến nghị 3: Vị thế đòn bẩy nào cần xây dựng..."
  ]
}
"""


def analyze_macro_radar(
    trend_description: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Optional[Dict[str, Any]]:
    """Phân tích một xu hướng vĩ mô bằng AI theo công thức First Principles và các quy luật ngầm Elite."""
    cleaned = trend_description.strip()
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
                        system_instruction=MACRO_RADAR_SYSTEM_PROMPT,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    resp = model.generate_content(
                        f"Phân tích xu hướng vĩ mô sau theo First Principles & Chiến lược Elite:\n\n{cleaned}"
                    )
                    if resp and resp.text:
                        txt = resp.text.strip()
                        if txt.startswith("```"):
                            lines = txt.splitlines()
                            if len(lines) >= 2 and lines[-1].startswith("```"):
                                txt = "\n".join(lines[1:-1]).strip()
                        data = json.loads(txt)
                        if isinstance(data, dict):
                            return data
                except Exception:
                    continue
        except Exception:
            continue

    return {"error": "Không thể phân tích qua các Key có sẵn. Vui lòng kiểm tra kết nối mạng."}
