# -*- coding: utf-8 -*-
"""
Module Sprint Game: Đấu Trường Gamification Ép Xung Trí Nhớ 10 Phút.
Áp dụng cơ chế Gamified Active Recall & Visual Spatial Association của Dave Farrow:
1. Game Ghép Ảnh Mỏ Neo Trực Quan (Visual Anchor Match)
2. Game Đọc Hoạt Cảnh Dị Biệt Chọn Ảnh (Reverse Image Guess)
3. Đấu Trường Phản Xạ 5 Giây (5-Second Reflex Arena)
"""

from __future__ import annotations
import random
import base64
import os
from typing import Dict, List, Any, Optional

from core.knowledge_vault import get_all_farrow_topics
from core.models_engine import load_unified_farrow_catalog


def get_anchor_image_base64(topic_id: str, chunk_id: str) -> Optional[str]:
    """Lấy dữ liệu base64 của ảnh mỏ neo WebP để render inline an toàn."""
    candidate_paths = [
        os.path.join("assets", "anchors", f"{topic_id}_{chunk_id}.webp"),
        os.path.join("D:/02_HocTap/elite/assets/anchors", f"{topic_id}_{chunk_id}.webp"),
        os.path.join("D:/02_HocTap/elite_thinking/assets/anchors", f"{topic_id}_{chunk_id}.webp"),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None


def get_all_game_chunks() -> List[Dict[str, Any]]:
    """Tổng hợp toàn bộ 39 chunks kèm topic metadata để làm ngân hàng câu hỏi game."""
    all_chunks = []
    topics = get_all_farrow_topics()
    for t in topics:
        for c in t.get("chunks", []):
            item = dict(c)
            item["topic_id"] = t["id"]
            item["topic_title"] = t["title"]
            item["topic_icon"] = t.get("icon", "🧠")
            item["topic_category"] = t.get("category", "")
            all_chunks.append(item)
    return all_chunks


def generate_visual_anchor_question(target_chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Tạo câu hỏi Game 1: Nhìn ảnh mỏ neo -> Chọn đúng Trụ cột & Quy luật."""
    all_chunks = get_all_game_chunks()
    target = target_chunk if target_chunk is not None else random.choice(all_chunks)
    
    distractors = [c for c in all_chunks if c["id"] != target["id"] or c["topic_id"] != target["topic_id"]]
    sampled_distractors = random.sample(distractors, min(3, len(distractors)))
    
    options = []
    options.append({
        "label": f"{target['topic_icon']} {target['topic_title']} — {target['label']}: {target.get('sub_modes', '')}",
        "is_correct": True
    })
    
    for d in sampled_distractors:
        options.append({
            "label": f"{d['topic_icon']} {d['topic_title']} — {d['label']}: {d.get('sub_modes', '')}",
            "is_correct": False
        })
        
    random.shuffle(options)
    img_b64 = get_anchor_image_base64(target["topic_id"], target["id"])
    
    return {
        "type": "visual_match",
        "type_label": "🎮 Nhìn Ảnh Đoán Mô Hình",
        "target": target,
        "image_b64": img_b64,
        "options": options,
        "question_text": "🔍 Bức tranh mỏ neo trực quan này đại diện cho Trụ Cột & Các Nguyên Lý nào?",
    }


def generate_crazy_image_reverse_question(target_chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Tạo câu hỏi Game 2: Đọc Hoạt Cảnh Dị Biệt -> Chọn đúng Bức Ảnh Mỏ Neo."""
    all_chunks = get_all_game_chunks()
    target = target_chunk if target_chunk is not None else random.choice(all_chunks)
    
    distractors = [c for c in all_chunks if c["id"] != target["id"] or c["topic_id"] != target["topic_id"]]
    sampled_distractors = random.sample(distractors, min(3, len(distractors)))
    
    image_options = []
    target_b64 = get_anchor_image_base64(target["topic_id"], target["id"])
    image_options.append({
        "chunk_id": target["id"],
        "topic_id": target["topic_id"],
        "title": f"{target['anchor_icon']} {target['anchor_name']}",
        "image_b64": target_b64,
        "is_correct": True
    })
    
    for d in sampled_distractors:
        d_b64 = get_anchor_image_base64(d["topic_id"], d["id"])
        image_options.append({
            "chunk_id": d["id"],
            "topic_id": d["topic_id"],
            "title": f"{d['anchor_icon']} {d['anchor_name']}",
            "image_b64": d_b64,
            "is_correct": False
        })
        
    random.shuffle(image_options)
    
    return {
        "type": "reverse_image_guess",
        "type_label": "🧠 Đọc Hoạt Cảnh Chọn Ảnh Mỏ Neo",
        "target": target,
        "story": target.get("crazy_image", ""),
        "anchor_name": target.get("anchor_name", ""),
        "image_options": image_options,
        "question_text": "🧠 Dựa vào Hoạt cảnh Dị biệt của Dave Farrow dưới đây, hãy chọn đúng Bức Ảnh Mỏ Neo tương ứng:",
    }


def generate_reflex_duel_question(target_model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Tạo câu hỏi Game 3: Đấu trường Phản xạ 5 giây -> Chọn đúng Mô hình Tinh hoa."""
    catalog = load_unified_farrow_catalog()
    valid_models = [m for m in catalog if m.get("trigger_question") and m.get("first_principle")]
    
    target = target_model if target_model is not None else random.choice(valid_models)
    
    distractors = [m for m in valid_models if m.get("id") != target.get("id")]
    sampled_distractors = random.sample(distractors, min(3, len(distractors)))
    
    options = []
    options.append({
        "id": target.get("id"),
        "label": f"[{target.get('id')}] {target.get('name_vi')} ({target.get('name_en')})",
        "is_correct": True
    })
    for d in sampled_distractors:
        options.append({
            "id": d.get("id"),
            "label": f"[{d.get('id')}] {d.get('name_vi')} ({d.get('name_en')})",
            "is_correct": False
        })
        
    random.shuffle(options)
    
    return {
        "type": "reflex_duel",
        "type_label": "⚡ Đấu Trường Phản Xạ 5 Giây",
        "target": target,
        "trigger_prompt": target.get("trigger_question"),
        "first_principle": target.get("first_principle"),
        "options": options,
        "question_text": f"⚡ Tình huống phản xạ 5 giây:\n👉 \"{target.get('trigger_question')}\"\n\nBạn nên kích hoạt Mô Hình Tinh Hoa nào?",
    }


def generate_game_round(round_size: int = 10, mode: str = "shuffle") -> List[Dict[str, Any]]:
    """
    Tạo danh sách câu hỏi cho cả một vòng chơi (round_size câu).
    - mode == 'shuffle': xáo trộn ngẫu nhiên luân phiên giữa cả 3 thể loại game.
    - mode == 'visual_match': toàn bộ vòng là Game 1.
    - mode == 'reverse_guess': toàn bộ vòng là Game 2.
    - mode == 'reflex_duel': toàn bộ vòng là Game 3.
    Đảm bảo các câu hỏi trong cùng một vòng không bị lặp lại đối tượng (target).
    """
    all_chunks = get_all_game_chunks()
    catalog = load_unified_farrow_catalog()
    valid_models = [m for m in catalog if m.get("trigger_question") and m.get("first_principle")]
    
    questions = []
    
    if mode == "visual_match":
        sampled_chunks = random.sample(all_chunks, min(round_size, len(all_chunks)))
        for ch in sampled_chunks:
            questions.append(generate_visual_anchor_question(target_chunk=ch))
            
    elif mode == "reverse_guess":
        sampled_chunks = random.sample(all_chunks, min(round_size, len(all_chunks)))
        for ch in sampled_chunks:
            questions.append(generate_crazy_image_reverse_question(target_chunk=ch))
            
    elif mode == "reflex_duel":
        sampled_models = random.sample(valid_models, min(round_size, len(valid_models)))
        for m in sampled_models:
            questions.append(generate_reflex_duel_question(target_model=m))
            
    else:  # "shuffle": Vòng chơi hỗn hợp, xáo trộn đa thể loại
        types = ["visual_match", "reverse_guess", "reflex_duel"]
        modes_pool = []
        for i in range(round_size):
            modes_pool.append(types[i % len(types)])
        random.shuffle(modes_pool)
        
        vis_count = modes_pool.count("visual_match")
        rev_count = modes_pool.count("reverse_guess")
        ref_count = modes_pool.count("reflex_duel")
        
        vis_chunks = random.sample(all_chunks, min(vis_count, len(all_chunks))) if vis_count else []
        rem_chunks = [c for c in all_chunks if c not in vis_chunks]
        rev_chunks = random.sample(rem_chunks if len(rem_chunks) >= rev_count else all_chunks, min(rev_count, len(all_chunks))) if rev_count else []
        ref_models = random.sample(valid_models, min(ref_count, len(valid_models))) if ref_count else []
        
        vis_iter = iter(vis_chunks)
        rev_iter = iter(rev_chunks)
        ref_iter = iter(ref_models)
        
        for m_type in modes_pool:
            if m_type == "visual_match":
                target_chunk = next(vis_iter, None)
                questions.append(generate_visual_anchor_question(target_chunk=target_chunk))
            elif m_type == "reverse_guess":
                target_chunk = next(rev_iter, None)
                questions.append(generate_crazy_image_reverse_question(target_chunk=target_chunk))
            else:
                target_model = next(ref_iter, None)
                questions.append(generate_reflex_duel_question(target_model=target_model))
                
    return questions


def get_round_summary(correct_count: int, total_count: int, round_xp: int) -> Dict[str, Any]:
    """Tổng kết thành tích vòng chơi và cấp danh hiệu hiệu suất não bộ."""
    acc_pct = int((correct_count / max(1, total_count)) * 100)
    bonus_xp = 0
    if acc_pct == 100:
        badge = "🌟 BẬC THẦY TUYỆT ĐỐI (PERFECT MASTER)"
        title = "Tâm Trí Thần Tốc - 100% Tuyệt Đối"
        desc = "Bộ não của bạn đã đồng bộ hoàn hảo với phương pháp Dave Farrow. Mọi mỏ neo đều được khắc sâu!"
        bonus_xp = total_count * 40 + 200
    elif acc_pct >= 80:
        badge = "🔥 THỢ SĂN TRÍ NHỚ CẤP CAO (ELITE HUNTER)"
        title = "Phản Xạ Xuất Thần"
        desc = "Bạn đã kích hoạt rất tốt bán cầu não phải và năng lực thị giác không gian."
        bonus_xp = total_count * 25 + 100
    elif acc_pct >= 60:
        badge = "⚡ CHIẾN BINH NÃO PHẢI (SPRINT WARRIOR)"
        title = "Phong Độ Tốt"
        desc = "Bạn đang tiến bộ vững chắc! Hãy tiếp tục duy trì nhịp độ ép xung để nâng cao tỷ lệ phản xạ."
        bonus_xp = total_count * 15 + 50
    else:
        badge = "🌱 TẬP SỰ KIÊN TRÌ (PERSISTENT APPRENTICE)"
        title = "Cần Thêm Mỏ Neo"
        desc = "Hãy quan sát kỹ hơn các bức tranh và hoạt cảnh dị biệt để kích hoạt hồi hải mã sâu hơn."
        bonus_xp = 30
        
    return {
        "correct": correct_count,
        "total": total_count,
        "acc_pct": acc_pct,
        "badge": badge,
        "title": title,
        "desc": desc,
        "bonus_xp": bonus_xp,
        "total_round_xp": round_xp + bonus_xp
    }


def get_user_rank(xp: int) -> Dict[str, str]:
    """Tính cấp bậc người chơi theo điểm kinh nghiệm XP."""
    if xp < 200:
        return {
            "rank": "🌱 Tập Sự Não Phải",
            "badge": "Beginner",
            "next_goal": "200 XP",
            "desc": "Đang làm quen với Lâu Đài Ký Ức và các mỏ neo hình ảnh kỳ quặc."
        }
    elif xp < 500:
        return {
            "rank": "⚡ Thợ Săn Mỏ Neo (Anchor Hunter)",
            "badge": "Intermediate",
            "next_goal": "500 XP",
            "desc": "Phản xạ mỏ neo không gian nhanh nhạy, ghi nhớ các quy luật cốt lõi."
        }
    elif xp < 1000:
        return {
            "rank": "🧠 Kiến Trúc Sư Lâu Đài Ký Ức",
            "badge": "Advanced",
            "next_goal": "1000 XP",
            "desc": "Thành thạo kết nối hình ảnh dị biệt và bóc tách các mô hình Munger."
        }
    else:
        return {
            "rank": "👑 Kỷ Lục Gia Trí Nhớ Dave Farrow",
            "badge": "Grandmaster",
            "next_goal": "Vô Cực",
            "desc": "Tư duy phản xạ 3 giây, chiếm lĩnh toàn bộ mạng lưới tư duy đa ngành!"
        }
