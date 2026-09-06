import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import re
from pathlib import Path
from pypdf import PdfReader

EN_PDF = r"D:\02_HocTap\elite_thinking\extention_read_english\books\Surely You're Joking, Mr. Feynman!.pdf"
VI_PDF = r"D:\02_HocTap\elite_thinking\extention_read_english\books\1644-feynman-chuyen-that-nhu-dua-thuviensach.vn.pdf"

en_reader = PdfReader(EN_PDF)
vi_reader = PdfReader(VI_PDF)

PARTS_METADATA = [
    {
        "part_id": 1,
        "title_en": "Part 1: FROM FAR ROCKAWAY TO MIT",
        "title_vi": "Phần 1: TỪ FAR ROCKAWAY ĐẾN MIT",
        "chapters": [
            {"id": 1, "slug": "p1_ch1", "title_en": "He Fixes Radios by Thinking!", "title_vi": "Cậu bé sửa radio bằng suy nghĩ", "en_p": (18, 26), "vi_p": (13, 26)},
            {"id": 2, "slug": "p1_ch2", "title_en": "String Beans", "title_vi": "Những trái đậu leo", "en_p": (27, 30), "vi_p": (27, 33)},
            {"id": 3, "slug": "p1_ch3", "title_en": "Who Stole the Door?", "title_vi": "Ai lấy trộm cánh cửa?", "en_p": (31, 40), "vi_p": (34, 49)},
            {"id": 4, "slug": "p1_ch4", "title_en": "Latin or Italian?", "title_vi": "Tiếng La tinh hay tiếng Ý?", "en_p": (41, 43), "vi_p": (50, 53)},
            {"id": 5, "slug": "p1_ch5", "title_en": "Always Trying to Escape", "title_vi": "Luôn tìm cách thoát", "en_p": (44, 50), "vi_p": (54, 64)},
            {"id": 6, "slug": "p1_ch6", "title_en": "The Chief Research Chemist of the Metaplast Corporation", "title_vi": "Sếp nghiên cứu hóa học của công ty Metaplast", "en_p": (51, 56), "vi_p": (65, 74)},
        ]
    },
    {
        "part_id": 2,
        "title_en": "Part 2: THE PRINCETON YEARS",
        "title_vi": "Phần 2: NHỮNG NĂM Ở PRINCETON",
        "chapters": [
            {"id": 1, "slug": "p2_ch1", "title_en": "“Surely You’re Joking, Mr. Feynman!”", "title_vi": "“Chắc là anh đang đùa, Feynman!”", "en_p": (58, 64), "vi_p": (75, 83)},
            {"id": 2, "slug": "p2_ch2", "title_en": "Meeeeeeeeeee!", "title_vi": "Emmmmmm!", "en_p": (65, 66), "vi_p": (84, 87)},
            {"id": 3, "slug": "p2_ch3", "title_en": "A Map of the Cat?", "title_vi": "Bản đồ con mèo?", "en_p": (67, 73), "vi_p": (88, 98)},
            {"id": 4, "slug": "p2_ch4", "title_en": "Monster Minds", "title_vi": "Những bộ óc khủng", "en_p": (74, 77), "vi_p": (99, 104)},
            {"id": 5, "slug": "p2_ch5", "title_en": "Mixing Paints", "title_vi": "Pha màu sơn", "en_p": (78, 80), "vi_p": (105, 108)},
            {"id": 6, "slug": "p2_ch6", "title_en": "A Different Box of Tools", "title_vi": "Một hộp công cụ khác lạ", "en_p": (81, 83), "vi_p": (109, 113)},
            {"id": 7, "slug": "p2_ch7", "title_en": "Mindreaders", "title_vi": "Những người đọc ý nghĩ", "en_p": (84, 86), "vi_p": (114, 117)},
            {"id": 8, "slug": "p2_ch8", "title_en": "The Amateur Scientist", "title_vi": "Nhà khoa học nghiệp dư", "en_p": (87, 94), "vi_p": (118, 128)},
        ]
    },
    {
        "part_id": 3,
        "title_en": "Part 3: FEYNMAN, THE BOMB, AND THE MILITARY",
        "title_vi": "Phần 3: FEYNMAN, BOM VÀ QUÂN ĐỘI",
        "chapters": [
            {"id": 1, "slug": "p3_ch1", "title_en": "Fizzled Fuses", "title_vi": "Những kíp nổ bị xịt", "en_p": (95, 99), "vi_p": (129, 135)},
            {"id": 2, "slug": "p3_ch2", "title_en": "Testing Bloodhounds", "title_vi": "Thử tập đánh hơi", "en_p": (100, 102), "vi_p": (136, 139)},
            {"id": 3, "slug": "p3_ch3", "title_en": "Los Alamos from Below", "title_vi": "Los Alamos nhìn từ bên dưới", "en_p": (103, 127), "vi_p": (140, 180)},
            {"id": 4, "slug": "p3_ch4", "title_en": "Safecracker Meets Safecracker", "title_vi": "Kẻ cắp, bà già gặp nhau", "en_p": (128, 143), "vi_p": (181, 207)},
            {"id": 5, "slug": "p3_ch5", "title_en": "Uncle Sam Doesn’t Need You!", "title_vi": "Chú Sam không cần bạn nữa!", "en_p": (144, 152), "vi_p": (208, 220)},
        ]
    },
    {
        "part_id": 4,
        "title_en": "Part 4: FROM CORNELL TO CALTECH, WITH A TOUCH OF BRAZIL",
        "title_vi": "Phần 4: TỪ CORNELL ĐẾN CALTECH, TẠT THĂM BRAZIL",
        "chapters": [
            {"id": 1, "slug": "p4_ch1", "title_en": "The Dignified Professor", "title_vi": "Giáo sư đạo mạo", "en_p": (153, 161), "vi_p": (221, 234)},
            {"id": 2, "slug": "p4_ch2", "title_en": "Any Questions?", "title_vi": "Có câu hỏi nào không?", "en_p": (162, 166), "vi_p": (235, 241)},
            {"id": 3, "slug": "p4_ch3", "title_en": "I Want My Dollar!", "title_vi": "Tôi muốn 1 đô la của mình!", "en_p": (167, 169), "vi_p": (242, 246)},
            {"id": 4, "slug": "p4_ch4", "title_en": "You Just Ask Them?", "title_vi": "Anh hỏi thẳng họ à?", "en_p": (170, 176), "vi_p": (247, 257)},
            {"id": 5, "slug": "p4_ch5", "title_en": "Lucky Numbers", "title_vi": "Những con số may mắn", "en_p": (177, 182), "vi_p": (258, 266)},
            {"id": 6, "slug": "p4_ch6", "title_en": "O Americano, Outra Vez!", "title_vi": "Lại là tay người Mỹ!", "en_p": (183, 199), "vi_p": (267, 295)},
            {"id": 7, "slug": "p4_ch7", "title_en": "Man of a Thousand Tongues", "title_vi": "Mister ngoại ngữ", "en_p": (200, 205), "vi_p": (296, 297)},
            {"id": 8, "slug": "p4_ch8", "title_en": "Certainly, Mr. Big!", "title_vi": "Tất nhiên rồi ngài Big!", "en_p": (206, 210), "vi_p": (298, 314)},
            {"id": 9, "slug": "p4_ch9", "title_en": "An Offer You Must Refuse", "title_vi": "Những lời mời phải từ chối", "en_p": (211, 217), "vi_p": (315, 322)},
        ]
    },
    {
        "part_id": 5,
        "title_en": "Part 5: THE WORLD OF ONE PHYSICIST",
        "title_vi": "Phần 5: THẾ GIỚI CỦA MỘT NHÀ VẬT LÝ",
        "chapters": [
            {"id": 1, "slug": "p5_ch1", "title_en": "Would You Solve the Dirac Equation?", "title_vi": "Anh sẽ giải phương trình Dirac chứ?", "en_p": (218, 226), "vi_p": (323, 336)},
            {"id": 2, "slug": "p5_ch2", "title_en": "The 7 Percent Solution", "title_vi": "Lời giải 7 phần trăm", "en_p": (227, 234), "vi_p": (337, 348)},
            {"id": 3, "slug": "p5_ch3", "title_en": "Thirteen Times", "title_vi": "Mười ba lần", "en_p": (235, 236), "vi_p": (349, 351)},
            {"id": 4, "slug": "p5_ch4", "title_en": "It Sounds Greek to Me!", "title_vi": "Nghe như tiếng Hy Lạp!", "en_p": (237, 237), "vi_p": (352, 353)},
            {"id": 5, "slug": "p5_ch5", "title_en": "But Is It Art?", "title_vi": "Nhưng đó là hội họa sao?", "en_p": (238, 253), "vi_p": (354, 380)},
            {"id": 6, "slug": "p5_ch6", "title_en": "Is Electricity Fire?", "title_vi": "Điện có phải là lửa không?", "en_p": (254, 261), "vi_p": (381, 392)},
            {"id": 7, "slug": "p5_ch7", "title_en": "Judging Books by Their Covers", "title_vi": "Thẩm định sách bằng bìa", "en_p": (262, 274), "vi_p": (393, 413)},
            {"id": 8, "slug": "p5_ch8", "title_en": "Alfred Nobel’s Other Mistake", "title_vi": "Một sai lầm khác của Alfred Nobel", "en_p": (275, 283), "vi_p": (414, 427)},
            {"id": 9, "slug": "p5_ch9", "title_en": "Bringing Culture to the Physicists", "title_vi": "Mang văn hóa đến cho các nhà Vật lý", "en_p": (284, 287), "vi_p": (428, 434)},
            {"id": 10, "slug": "p5_ch10", "title_en": "Found Out in Paris", "title_vi": "Ngộ ra ở Paris", "en_p": (288, 297), "vi_p": (435, 450)},
            {"id": 11, "slug": "p5_ch11", "title_en": "Altered States", "title_vi": "Những trạng thái khác lạ", "en_p": (298, 304), "vi_p": (451, 461)},
            {"id": 12, "slug": "p5_ch12", "title_en": "Cargo Cult Science", "title_vi": "Ngụy khoa học", "en_p": (305, 314), "vi_p": (462, 474)},
        ]
    }
]

def clean_lines(text, is_vi=False):
    lines = []
    for l in text.split("\n"):
        l = l.strip()
        if not l:
            lines.append("")
            continue
        if re.match(r"^\d+$", l):
            continue
        if "thuviensach.vn" in l or "Surely You’re Joking" in l or "Adventures of a Curious" in l:
            continue
        l_norm = re.sub(r"[\t]+", " ", l).strip()
        lines.append(l_norm)
    return lines

def extract_paragraphs(lines, is_vi=False):
    paras, cur = [], []
    for l in lines:
        if not l:
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        if cur and cur[-1] and cur[-1][-1] in [".", "!", "?", '"', "”", "’", ":"]:
            if l.startswith("“") or l.startswith('"') or l.startswith("—") or l.startswith("- ") or (l[0].isupper() and len(cur[-1]) < 65):
                paras.append(" ".join(cur))
                cur = [l]
                continue
        cur.append(l)
    if cur:
        paras.append(" ".join(cur))
    
    cleaned = []
    for p in paras:
        p_str = p.strip()
        if len(p_str) > 25 and not any(h in p_str for h in ["PHẦN 1", "PHẦN 2", "PHẦN 3", "PHẦN 4", "PHẦN 5", "Contents", "Mục lục"]):
            cleaned.append(p_str)
    return cleaned

def align_into_cards(en_paras, vi_paras):
    N = len(en_paras)
    M = len(vi_paras)
    if N == 0:
        return []
    if M == 0:
        return [{"section_id": i+1, "title": f"Đoạn {i+1}", "en": p, "vi": "", "vocab": []} for i, p in enumerate(en_paras)]
    
    en_lens = [len(p.split()) for p in en_paras]
    vi_lens = [len(p.split()) for p in vi_paras]
    total_en = sum(en_lens) or 1
    total_vi = sum(vi_lens) or 1
    
    cum_en = []
    c = 0
    for l in en_lens:
        c += l
        cum_en.append(c / total_en)
        
    cards = []
    vi_idx = 0
    
    for i in range(N):
        target_progress = cum_en[i]
        matched_vi = []
        
        while vi_idx < M:
            cur_vi_progress = (sum(vi_lens[:vi_idx + 1])) / total_vi
            matched_vi.append(vi_paras[vi_idx])
            vi_idx += 1
            if cur_vi_progress >= target_progress and i < N - 1:
                break
                
        if i == N - 1 and vi_idx < M:
            while vi_idx < M:
                matched_vi.append(vi_paras[vi_idx])
                vi_idx += 1
                
        cards.append({
            "section_id": i + 1,
            "title": f"Phần {i + 1}",
            "en": en_paras[i],
            "vi": "\n\n".join(matched_vi) if matched_vi else "",
            "vocab": []
        })
    return cards

print("Building FULL 5-part Feynman bilingual book dataset...")
full_dataset = {
    "book_id": "feynman_joking",
    "title_en": "Surely You're Joking, Mr. Feynman!",
    "title_vi": "Chuyện Thật Như Đùa (Richard P. Feynman)",
    "author": "Richard P. Feynman",
    "category": "Elite Thinking & Ultralearning",
    "description": "Toàn văn 5 Phần (40 Chương) song ngữ Anh - Việt đối xứng, tối ưu hóa cho phương pháp Siêu Học (Ultralearning).",
    "parts": []
}

total_chaps = 0
total_sections = 0

for p_meta in PARTS_METADATA:
    part_obj = {
        "part_id": p_meta["part_id"],
        "title_en": p_meta["title_en"],
        "title_vi": p_meta["title_vi"],
        "chapters": []
    }
    
    for ch in p_meta["chapters"]:
        raw_en = ""
        for p in range(ch["en_p"][0] - 1, min(ch["en_p"][1], len(en_reader.pages))):
            raw_en += en_reader.pages[p].extract_text() or ""
            raw_en += "\n"
            
        raw_vi = ""
        for p in range(ch["vi_p"][0] - 1, min(ch["vi_p"][1], len(vi_reader.pages))):
            raw_vi += vi_reader.pages[p].extract_text() or ""
            raw_vi += "\n"
            
        p_en = extract_paragraphs(clean_lines(raw_en))
        p_vi = extract_paragraphs(clean_lines(raw_vi, is_vi=True), is_vi=True)
        
        cards = align_into_cards(p_en, p_vi)
        total_chaps += 1
        total_sections += len(cards)
        
        part_obj["chapters"].append({
            "id": ch["id"],
            "slug": ch["slug"],
            "title_en": ch["title_en"],
            "title_vi": ch["title_vi"],
            "summary_vi": f"Chương {ch['id']} thuộc {p_meta['title_vi']}.",
            "sections": cards
        })
        print(f"  P{p_meta['part_id']} Ch{ch['id']:02d}: {ch['title_en'][:25]:25} | Cards: {len(cards):2d}")
        
    full_dataset["parts"].append(part_obj)

# Save JSON
out_path = Path(r"D:\02_HocTap\elite_thinking\data\bilingual_books\feynman_surely_youre_joking.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(full_dataset, f, ensure_ascii=False, indent=2)

file_kb = out_path.stat().st_size / 1024
print(f"\n=======================================================")
print(f"FULL BOOK GENERATED SUCCESSFULLY!")
print(f"Total Parts: {len(full_dataset['parts'])}")
print(f"Total Chapters: {total_chaps}")
print(f"Total Bilingual Cards: {total_sections}")
print(f"File Size: {file_kb:.1f} KB")
print(f"Location: {out_path}")
print(f"=======================================================")
