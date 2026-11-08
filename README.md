# 📖 HƯỚNG DẪN SỬ DỤNG LUCKY TCP SUPER BOT (OB55)

> **Tài khoản Bot**: `toandin-ZC08` (UID Game: `19054543580` - Server: **VN**)  
> **Quản trị viên (Admin)**: UID `2996528672`  
> **Giao thức**: TCP Sảnh Đội (Online Server) & TCP Kênh Chat (Chat Server)

---

## 📌 MỤC LỤC
1. [Phân Quyền Lệnh (Admin vs Người dùng/Bạn bè)](#1-phân-quyền-lệnh)
2. [Lệnh Quản Trị & Điều Khiển Bot](#2-lệnh-quản-trị--điều-khiển-bot)
3. [Lệnh Tạo Tổ Đội Tự Động (/2, /3, /4, /5, /6)](#3-lệnh-tạo-tổ-đội-tự-động)
4. [Hệ Thống Biểu Cảm (Emote & Evo Gun)](#4-hệ-thống-biểu-cảm-emote--evo-gun)
5. [Hiệu Ứng Hoạt Ảnh & Trang Phục Đặc Biệt](#5-hiệu-ứng-hoạt-ảnh--trang-phục-đặc-biệt)
6. [Nhóm Gói Tin Can Thiệp Nâng Cao (Troll / Lag Packets)](#6-nhóm-gói-tin-can-thiệp-nâng-cao)
7. [Tra Cứu Thông Tin & Tiện Ích](#7-tra-cứu-thông-tin--tiện-ích)
8. [Mini-Games & Tương Tác Vui Nhộn](#8-mini-games--tương-tác-vui-nhộn)
9. [Lưu Ý Quan Trọng Khi Sử Dụng](#9-lưu-ý-quan-trọng)

---

## 1. PHÂN QUYỀN LỆNH

* **Nhóm Quản Trị Viên (Admin Only - UID `2996528672`)**: Các lệnh bật/tắt bot, ép bot vào/rời squad, spam tin nhắn, spam gói tin can thiệp sảnh (`/ban`, `/reject`, `/ice`, `/spm`, `/s1`-`/s5`, `/add`, `/remove`).
* **Nhóm Tự Do (Mọi người & Bạn bè đều dùng được)**: Lệnh tạo team (`/2`–`/6`), múa emote (`/e`, `/evos`, `/rd`, gõ tắt tên emote, gõ số), tra cứu (`/info`, `/check`, `/status`), máy tính, hỏi đáp AI và toàn bộ các minigames giải trí.

---

## 2. LỆNH QUẢN TRỊ & ĐIỀU KHIỂN BOT
*(Chỉ dành riêng cho Admin)*

| Lệnh | Cú pháp | Ví dụ | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| **Bật Bot** | `/on` | `/on` | Kích hoạt bot nhận và xử lý lệnh từ mọi người. |
| **Tắt Bot** | `/off` | `/off` | Tạm dừng bot (bot sẽ im lặng, không phản hồi lệnh). |
| **Vào Tổ Đội** | `/join <mã_đội>` | `/join 1234567` | Bắt bot tự động tham gia vào một phòng qua mã Team Code. |
| **Rời Tổ Đội** | `/exit` hoặc `/leave` | `/exit` | Bắt bot rời khỏi Tổ đội hiện tại ngay lập tức. |
| **Kết bạn** | `/add <uid>` | `/add 2996528672` | Dùng tài khoản bot gửi lời mời kết bạn tới mục tiêu. |
| **Hủy kết bạn** | `/remove <uid>` | `/remove 2996528672` | Xóa kết bạn một UID khỏi danh sách bạn bè của bot. |
| **Nhại Emote** | `/mimic_on` / `/mimic_off` | `/mimic_on` | Bật/tắt chế độ nhại: Ai trong squad múa gì bot múa theo đó. |

---

## 3. LỆNH TẠO TỔ ĐỘI TỰ ĐỘNG
*(Bạn bè & Mọi người đều dùng được)*

Bot có khả năng tự động tạo Tổ đội đúng kích thước và gửi lời mời trực tiếp vào màn hình game cho bạn:

| Lệnh | Kích thước | Mô tả |
| :--- | :--- | :--- |
| `/2` hoặc `/team2` | Team 2 người (Duo) | Bot tạo phòng 2 và mời bạn vào. |
| `/3` hoặc `/team3` | Team 3 người (Trio) | Bot tạo phòng 3 và mời bạn vào. |
| `/4` hoặc `/team4` | Team 4 người (Squad) | Bot tạo phòng 4 và mời bạn vào. |
| `/5` hoặc `/team5` | Team 5 người | Bot tạo phòng 5 và mời bạn vào. |
| `/6` hoặc `/team6` | Team 6 người (CS 6v6) | Bot tạo phòng 6 người và mời bạn vào. |

* **Cách dùng nâng cao**:
  * Gõ `/4`: Bot tự tạo team 4 và mời chính bạn.
  * Gõ `/4 <uid1> <uid2>`: Bot tạo team 4 và mời thêm bạn bè của bạn cùng vào.
* **Cơ chế bảo vệ Admin**: Nếu Bot đang đứng chung tổ đội với Admin, bot sẽ từ chối tạo phòng mới cho người khác để tránh bị "cướp" bot.

---

## 4. HỆ THỐNG BIỂU CẢM (EMOTE & EVO GUN)
*(Điều kiện: Bot và bạn phải đang đứng chung trong 1 Tổ đội)*

### A. Chu kỳ múa súng nâng cấp Evo (`/evos`)
* **`/evos`**: Chỉ Bot và Bạn (Admin) múa lặp lại 21 khẩu súng Evo liên tục.
* **`/evos <uid1> <uid2>...`**: Múa cho Bot, Bạn và các thành viên được chỉ định (hỗ trợ cách nhau bằng dấu cách, dấu `+`, dấu phẩy).
* **`/evos all`**: Tự động phát lệnh múa súng Evo cho **cả phòng cùng múa một lúc**!
* **`/sevos`**: Dừng chu kỳ múa súng Evo.
* **`/evo <uid> <1-21>`**: Múa đơn lẻ một khẩu súng Evo theo số thứ tự từ 1 đến 21.

### B. Chu kỳ múa ngẫu nhiên 386+ Emote (`/rd`)
* **`/rd`**: Bot và Bạn múa ngẫu nhiên đổi động tác liên tục mỗi 4 giây từ kho hơn 386 emote.
* **`/rd <uid1> <uid2>...`**: Múa ngẫu nhiên cho Bot, Bạn và các UID chỉ định.
* **`/rd all`**: Múa ngẫu nhiên cho **toàn bộ thành viên trong phòng**!
* **`/srd`**: Dừng chu kỳ múa ngẫu nhiên.

### C. Múa Emote theo tên & gõ tắt
* **Dùng lệnh `/e`**:
  * `/e <tên_emote>`: Ví dụ `/e ak`, `/e scar`, `/e lol`, `/e money`, `/e flower`.
  * `/e all <tên_emote>`: Múa emote đó cho cả phòng cùng thực hiện!
  * `/e <uid> <tên_emote>`: Ép một UID cụ thể múa.
* **Gõ tắt trực tiếp** *(không cần tiền tố `/`)*:
  * Gõ tên súng/emote: `ak`, `scar`, `mp40`, `m1014`, `xm8`, `famas`, `ump`, `groza`, `fist`, `dance`, `lol`, `sad`, `hi`, `money`, `love`, `chicken`, `dab`, `selfie`, `flower`, `petals`...
  * Gõ số emote: gõ từ `1` đến `20` (ví dụ gõ `1` là múa emote số 1).
  * Gõ múa lặp: `<số>*<số lần>` (ví dụ: `1*5` là múa emote số 1 năm lần liên tiếp).

### D. Spam Emote tốc độ cao
* `/fast <uid> <id_emote>`: Spam nhanh 25 lần một emote.
* `/p <uid> <id_emote> <số lần>`: Tự thiết lập số lần spam emote mong muốn (tối đa 100 lần).

---

## 5. HIỆU ỨNG HOẠT ẢNH & TRANG PHỤC ĐẶC BIỆT

* **`/b <1-13>`**: Đổi ngoại trang Bundle đặc biệt kết hợp hiệu ứng xuất hiện.
* **`/animation [1-12]`**: Xem và kích hoạt hoạt ảnh xuất hiện khi gia nhập sảnh:
  * `1`: Rampage | `2`: Cannibal | `3`: Devil | `4`: Scorpio | `5`: Frostfire
  * `6`: Paradox | `7`: Naruto | `8`: Aurora | `9`: Midnight | `10`: Itachi
  * `11`: Dreamspace | `12`: Eclipse
* **`/sticker`**: Bắn nhãn dán hoạt hình ngẫu nhiên vào khung chat.
* **`/title`** hoặc **`/alltitles`**: Kích hoạt hiệu ứng danh hiệu.
* **`/menu [trang]`**: Mở menu duyệt qua danh sách các ID emote có trong bot.

---

## 6. NHÓM GÓI TIN CAN THIỆP NÂNG CAO (TROLL / LAG PACKETS)
*(Admin Only - Dùng để troll vui trong phòng)*

| Lệnh | Cú pháp | Công dụng & Cơ chế |
| :--- | :--- | :--- |
| **Đóng Băng** | `/ice <uid\|me>`<br>`/ice_stop` | Bắn liên tục emote đóng băng tốc độ cao (0.1s/lần) làm nhân vật bị reset hoạt ảnh liên tục, tạo cảm giác **đứng cứng đờ như bị đông cứng** trong sảnh. |
| **Spam Từ Chối** | `/reject <uid>`<br>`/reject_stop` | Bắn 150 thông báo từ chối kèm đoạn banner nhiều dòng ngắt trang rác làm **tràn bộ nhớ đệm thông báo**, khiến màn hình đối phương bị khựng/lag. |
| **Phá Kênh Chat** | `/ban <uid>`<br>`/ban_stop` | Bắn gói tin xác thực kênh chat giả mạo nhắm vào UID đối phương làm ngắt kết nối kênh chat (Chat Ban) tạm thời. |
| **Spam Mời Đội** | `/spm <uid>`<br>`/stp <uid>` | Tự động gửi lời mời vào tổ đội liên tục mỗi giây tới mục tiêu (dùng `/stp <uid>` để tắt). |
| **Spam Phòng** | `/room <uid> <id_phòng>`<br>`/room_stop` | Bắn liên tục gói tin yêu cầu phòng tuỳ chọn tới người chơi. |
| **Spam Huy Hiệu** | `/s1` đến `/s5 <uid>` | Gửi yêu cầu vào đội kèm hiệu ứng huy hiệu đặc biệt:<br>• `/s1`: Craftland 🏆<br>• `/s2`: V-Badge Lớn 🔥<br>• `/s3`: Điều Hành Viên 👮<br>• `/s4`: V-Badge Nhỏ ⚡<br>• `/s5`: Tuyển Thủ 💎 |
| **Spam Tin Nhắn** | `/msg <nội dung> <số lần>`<br>`/stop msg` | Bắn tin nhắn lặp lại với số lần tuỳ chọn (tối đa 100 lần). |
| **Sóng Tin Nhắn** | `/mg <nội dung> [số lần]` | Bắn tin nhắn theo hiệu ứng từng ký tự đợt sóng. |
| **Vào Tàng Hình** | `/gh <mã_đội> <tên>` | Bot vào squad dưới tên tàng hình (Ghost). |

---

## 7. TRA CỨU THÔNG TIN & TIỆN ÍCH

* **`/info <uid>`**: Tra cứu toàn bộ thông tin tài khoản Free Fire (Tên ingame, Cấp độ, Số lượt Like, Rank Sinh Tồn/Tử Chiến, Huy hiệu, Quân đoàn...).
* **`/check <uid>`**: Kiểm tra tình trạng tài khoản có bị khoá/cấm (Ban check) hay an toàn.
* **`/status <uid>`**: Xem trạng thái của người chơi (Đang Online, Đang trong trận hay Đang trong Squad).
* **`/ai <câu hỏi>`**: Đặt câu hỏi bất kỳ để bot giải đáp tự động.
* **`/mth <biểu thức>`**: Máy tính thông minh (Ví dụ: `/mth (1500 * 25) + 350`).
* **`/help`** hoặc `help`: Hiển thị 4 khung menu trợ giúp đẹp mắt trực tiếp trong game.
* **`/admin`**: Hiển thị bảng thông tin nhà phát triển bot.

---

## 8. MINI-GAMES & TƯƠNG TÁC VUI NHỘN

* **`/joke`**: Kể truyện cười xả stress.
* **`/quiz`**: Câu đố vui kèm sẵn đáp án.
* **`/roll`**: Tung 2 viên xúc xắc tính tổng điểm (từ 2 đến 12).
* **`/dare`**: Tạo thử thách hành động (Dare).
* **`/truth`**: Đặt câu hỏi sự thật (Truth).
* **`/wyr`**: Trò chơi lựa chọn *"Bạn thà chọn điều A hay điều B?"*.
* **`/love <tên>`**: Gửi chuỗi tin nhắn tỏ tình lãng mạn.
* **`/gali <tên>`**: Trêu chọc, gáy khịa đối thủ hài hước.
* **`/rt <tên>`**: Roast / cà khịa vui nhộn.
* **`/praisa <tên>`**: Khen ngợi kỹ năng đồng đội.
* **`/later <tên>`**: Gửi bài thơ tình cảm lãng mạn.
* **`/sadlater <tên>`**: Gửi bài thơ tâm trạng cô đơn.
* **`/luck <tên>`**: Xem bói vận mệnh và tài lộc theo tên.
* **`/zodiac`**: Bói cung hoàng đạo, con số và màu sắc may mắn trong ngày.
* **`/weather`**: Dự báo thời tiết vui nhộn các tỉnh thành.

---

## 9. LƯU Ý QUAN TRỌNG

1. **Hiển thị Emote**: Để nhìn thấy nhân vật múa, bạn và bot **bắt buộc phải ở chung một Tổ đội (Squad)**. Nhắn tin riêng ngoài sảnh chính game sẽ không hiển thị hoạt cảnh.
2. **Tự động nhận lời mời**: Bot được cài đặt tính năng tự động chấp nhận lời mời vào phòng. Bạn chỉ cần tạo Squad rồi bấm nút mời bot trong danh sách bạn bè là bot sẽ tự vào ngay.
3. **Tránh spam quá mức**: Không nên chạy nhiều tiến trình spam (`/spm`, `/reject`, `/ban`) cùng lúc trong thời gian dài để đảm bảo tài khoản bot không bị máy chủ Garena ngắt kết nối (Disconnect socket).
