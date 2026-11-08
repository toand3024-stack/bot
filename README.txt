LUCKY TCP BOT - BẢN VIỆT HOÁ & ĐÃ FIX LỖI
==========================================
Cài đặt & Khởi chạy:
    pip install -r requirements.txt
    python main.py

Thư mục gốc      = Bot đã được cập nhật và Việt hoá hoàn chỉnh (chạy file main.py).
Pb2/             = Chứa các tập tin Protobuf hỗ trợ giao thức kết nối.

CÁC TÍNH NĂNG VÀ CẬP NHẬT CHÍNH
-------------------------------
1) Giao thức Squad / Nhóm:
   - Các hàm OpEnSq, cHSq, SEnd_InV, GenJoinSquadsPacket trong xC4.py đã được tối ưu hoá theo phiên bản tương thích cao nhất.
   - Hỗ trợ đổi kích thước phòng tự động theo số lượng thành viên (3/4/5/6 người).

2) Cơ chế Đăng nhập (login_engine.py):
   - Đã cập nhật payload MajorLogin tương thích Free Fire OB55.
   - Sửa lỗi client_ip không tạo đúng định dạng IP ngẫu nhiên.
   - Bổ sung cơ chế phát hiện và cảnh báo tài khoản bị Garena khoá/cấm (Ban reason: Protection Bypass) thay vì thông báo lỗi không rõ ràng.
   - Đã thay thông tin tài khoản bot của bạn vào main.py (BOT_UID và BOT_PASSWORD).

3) Tính năng Tự động tham gia Squad & Chào mừng:
   - Khi có lời mời vào Squad, bot sẽ tự động chấp nhận lời mời và gửi tin nhắn chào mừng (WELCOME_TEXT, giãn cách 30 phút mỗi nhóm để tránh spam).
   - Tối ưu độ trễ gửi tin nhắn chào mừng xuống 1 giây và gửi trực tiếp tới UID chủ phòng (squad owner).

4) Chat Quân đoàn & Menu Trợ giúp:
   - Tối ưu hoá phản hồi tin nhắn trong kênh chat Quân đoàn (Clan Chat).
   - Lệnh /help hiển thị menu các danh mục lệnh (Lệnh game, Biểu cảm, Lệnh giải trí, Thông tin Admin).
   - Tốc độ hiển thị các khung menu được tối ưu còn 0.1s (HELP_DELAY trong bot_core.py).

5) Toàn bộ giao diện Console và tin nhắn phản hồi:
   - Đã được dịch 100% từ tiếng Bangladesh / Bengali sang tiếng Việt chuẩn, rõ ràng, dễ sử dụng.
