# MEXC Futures RSI Scanner Bot

Bot Python quét toàn bộ thị trường Futures trên sàn MEXC để tìm kiếm cơ hội Short dựa trên chỉ báo RSI đa khung thời gian.

## Tính năng
- Quét tất cả các cặp Futures USDT.
- Tính RSI trên 7 khung thời gian: 1m, 5m, 15m, 30m, 1h, 4h, 1d.
- Cảnh báo Telegram khi:
  - Có ít nhất 2 khung thời gian có RSI > 80.
  - Cảnh báo đặc biệt khi RSI > 90.
- Anti-Spam: Chỉ cảnh báo lại khi tất cả RSI đã hạ nhiệt (< 75).

## Cài đặt

1. **Cài đặt Python**: Đảm bảo đã cài Python 3.8 trở lên.
2. **Cài thư viện**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình**:
   - Đổi tên file `.env.example` thành `.env`
   - Nhập Token Bot Telegram và Chat ID vào file `.env`
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=-100123456789
   ```

## Chạy Bot
Chạy lệnh sau:
```bash
python main.py
```

## Cấu hình nâng cao
Mở file `config.py` để chỉnh sửa:
- `RSI_OVERBOUGHT`: Ngưỡng quá mua (mặc định 80).
- `MIN_TIMEFRAME_MATCH`: Số lượng khung thời gian cần thỏa mãn (mặc định 2).
