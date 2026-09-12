# NGOẠI BẢN KỸ THUẬT
## Bổ sung cho *Chuyện Ngụ Ngôn Đầu Tư XAU*

> Tài liệu này dành cho người đã đọc hết 12 chương chính và muốn đi sâu vào lớp vi cấu trúc.  
> Không còn hình tượng gà – heo – sói. Chỉ còn ngôn ngữ kỹ thuật thuần túy.

---

## 1. Phân biệt Absorption thật và Vacuum / Fake Sweep

### 1.1. Vấn đề cốt lõi
Không phải mọi râu nến dài đều là hấp thụ của Smart Money.  
Có hai loại râu nến trông giống nhau về hình học nhưng bản chất hoàn toàn khác:

| Loại | Đặc điểm | Ý nghĩa |
|------|----------|--------|
| **Absorption thật** | Volume lớn + CVD râu cực mạnh + giá bị giữ lại | Smart Money dùng Limit order nuốt lệnh Market của đám đông |
| **Vacuum Sweep** | Râu dài nhưng Volume thấp hoặc phân bổ đều | Giá trượt qua vùng sổ lệnh mỏng (Liquidity Void), không có lực hấp thụ thật |

### 1.2. Công cụ đo lường

**A. Relative Volume (RVOL)**
```
RVOL = Volume hiện tại / Rolling Median Volume (chu kỳ 14–20)
```
- RVOL ≥ 1.5 → có sự tham gia bất thường của dòng tiền.
- RVOL < 1.0 trong lúc tạo râu dài → nghi ngờ cao là Vacuum.

**B. Wick Volume Ratio (ước lượng khi không có tick data)**
```
Wick Volume Ratio ≈ (Độ dài râu / Toàn bộ biên độ nến) × Volume
```
Hoặc tốt hơn nếu có CVD phân bổ:
```
CVD_Wick = CVD được phân bổ tỷ lệ theo kích thước râu so với thân + râu
```

**C. Điều kiện xác nhận Absorption thật (khuyến nghị)**
1. Râu nến ≥ 1.5 lần thân nến (hoặc râu ≥ 1.5 × ATR/MTR gần nhất).
2. RVOL ≥ 1.5.
3. CVD tại vùng râu cùng chiều với lực hấp thụ (CVD âm mạnh ở lower wick khi bullish absorption).
4. Giá đóng cửa rút về phía ngược lại rõ ràng (không phải Marubozu xuyên thủng).

Nếu thiếu từ 2 điều trở lên → xếp vào nhóm “chưa đủ tin cậy”, đứng ngoài.

---

## 2. Secondary Test (Spring / Test lại)

### 2.1. Bản chất
Sau cú Sweep + Absorption đầu tiên, Smart Money thường **không đẩy giá đi ngay**.  
Họ thường tạo thêm một nhịp test nhẹ (Volume thấp hơn) để:
- Kiểm tra nguồn cung còn lại.
- Quét nốt những người vào lệnh sớm (early buyers/sellers).
- Dụ thêm breakout traders nhảy vào sai hướng.

### 2.2. Đặc điểm nhận diện Secondary Test
- Xảy ra sau cú Sweep có Absorption rõ.
- Biên độ nhỏ hơn hoặc bằng cú Sweep trước.
- Volume và CVD yếu hơn đáng kể so với cú đầu.
- Giá xuyên nhẹ qua đáy/đỉnh cũ rồi nhanh chóng bị kéo ngược lại.
- Thường tạo ra Fair Value Gap nhỏ theo hướng ngược lại với cú Sweep.

### 2.3. Cách hành xử
- **Không vào lệnh** ở cú Sweep đầu tiên nếu chưa có Secondary Test (trừ khi Absorption cực mạnh + Marubozu xác nhận ngay).
- Điểm vào chất lượng cao nhất thường nằm ở khoảnh khắc giá đóng cửa quay lại bên trong biên độ của cú Sweep đầu tiên, xác nhận Secondary Test đã thất bại (trở thành Bear/Bull Trap).

---

## 3. Sự khác biệt theo phiên giao dịch (Session Difference)

### 3.1. Đặc tính thanh khoản theo phiên (GMT+7 tham chiếu)

| Phiên | Thời gian (GMT+7) | Đặc điểm | Hệ quả thực chiến |
|-------|-------------------|----------|-------------------|
| **Á** | 05:00 – 12:00 | Thanh khoản mỏng, dễ tạo Vacuum Sweep | RVOL ngưỡng cần cao hơn. Nhiều râu giả. Nên giảm size hoặc đứng ngoài |
| **Âu** | 14:00 – 18:00 | Thanh khoản tăng dần | Bắt đầu có tín hiệu sạch hơn |
| **Mỹ** | 19:30 – 02:00 | Thanh khoản dày nhất, biến động thật | Tín hiệu Absorption đáng tin cậy nhất. Ưu tiên giao dịch |
| **Giao thoa Âu-Mỹ** | 19:30 – 22:00 | Thanh khoản cực đại | Khung giờ vàng cho XAU |

### 3.2. Điều chỉnh thực tế
- **Phiên Á**: Chỉ giao dịch khi RVOL cực cao (thường ≥ 2.0) và có Secondary Test rõ. Nếu không thì bỏ qua.
- **Phiên Mỹ**: Có thể hạ nhẹ ngưỡng RVOL (1.3–1.5) vì thanh khoản nền đã cao.
- Không dùng chung một bộ thông số cố định cho mọi phiên.

---

## 4. Thứ tự lọc tín hiệu khuyến nghị (Checklist kỹ thuật)

Áp dụng theo đúng thứ tự gà nhỏ đã học ở Chương 12, nhưng phiên bản số hóa:

1. **Lực (Volume / CVD / RVOL)**  
   - Có râu nến đạt tiêu chuẩn hình học không?  
   - RVOL có đủ lớn không?  
   - CVD râu có xác nhận hấp thụ không?

2. **Trạng thái nén (Compression)**  
   - Biên độ có đang thắt chặt so với các đoạn trước không?  
   - Time Compression (số nến M1 trong mỗi Range bar) có tăng bất thường không?

3. **Secondary Test**  
   - Đã có nhịp test lại sau cú Sweep chưa?  
   - Nhịp test có Volume yếu và bị từ chối không?

4. **Tốc độ & Hướng**  
   - Velocity / Acceleration có bắt đầu tăng đúng hướng kỳ vọng không?  
   - Có Marubozu hoặc nến xác nhận mạnh xuất hiện không?

5. **Ngữ cảnh phiên**  
   - Đang ở phiên nào? Có cần nâng/hạ ngưỡng lọc không?

Chỉ khi đi hết 5 bước và tất cả đều “xanh” thì mới xem xét vào lệnh theo quy tắc quản trị vốn ở Chương 11.

---

## 5. Các ngưỡng tham khảo (có thể tinh chỉnh)

| Chỉ số | Ngưỡng tham khảo | Ghi chú |
|--------|------------------|--------|
| RVOL | ≥ 1.5 (Á: ≥ 2.0) | Rolling Median 14–20 |
| Tỷ lệ Râu / Thân | ≥ 1.5 | Hoặc Râu ≥ 1.5 × MTR |
| CVD râu | Vượt xa MAD của CVD râu gần nhất | Dùng Modified Z-score nếu có thể |
| Compression | Biên độ giảm dần + Time Compression tăng | Quan sát trên Range chart |
| Secondary Test Volume | Thấp hơn rõ rệt so với cú Sweep | Thường < 60–70% volume cú đầu |

---

## 6. Lưu ý cuối

- Tất cả ngưỡng trên chỉ là điểm xuất phát. Thị trường XAU thay đổi chế độ (regime) theo thời gian. Cần theo dõi hiệu suất và điều chỉnh.
- Ưu tiên **đứng ngoài** khi tín hiệu mâu thuẫn hơn là cố tìm cách vào lệnh.
- Ngoại bản này không thay thế việc quan sát trực tiếp Order Flow / Footprint nếu bạn có dữ liệu tick chất lượng cao. Khi có dữ liệu tốt hơn, hãy ưu tiên dữ liệu đó.

---

**Hết Ngoại bản kỹ thuật.**

*Tài liệu này bổ sung lớp vi cấu trúc còn thiếu trong bộ ngụ ngôn chính, giúp người đọc có thể nâng cấp hệ thống từ mức hiểu bản chất lên mức thực chiến có bộ lọc rõ ràng.*
