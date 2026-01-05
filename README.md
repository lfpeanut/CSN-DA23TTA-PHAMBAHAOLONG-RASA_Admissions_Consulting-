# TVU Admissions Consulting Chatbot (Rasa) + Website

Chatbot tư vấn nhập học cho tân sinh viên **Trường Đại học Trà Vinh (TVU)** được xây dựng bằng **Rasa** và tích hợp lên website (HTML/CSS/JS hoặc rasa-webchat widget).

---

## 1) Yêu cầu hệ thống

- **Python 3.10.x** (khuyến nghị 3.10.8+)
- **pip** (đi kèm Python)
- **Git** (để clone/push repo)
- (Tuỳ chọn) VS Code để chỉnh sửa file YAML/HTML
- (Tuỳ chọn) Ngrok/Cloudflare Tunnel nếu muốn public bot ra internet để nhúng vào web online

> Lưu ý: Rasa thường ổn định nhất với Python 3.10. Không khuyến nghị dùng Python 3.12.

---

## 2) Cài Python 3.10 (Windows)

1. Tải Python 3.10 từ trang chính thức.
2. Khi cài đặt nhớ tick:
   - ✅ **Add python.exe to PATH**
3. Kiểm tra sau khi cài:
```bash
python --version
pip --version
```
---


## 3) Tạo môi trường ảo

python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip


## 4) Tải rasa 
pip install rasa
- Kiểm tra version
rasa --version
pip install rasa-sdk

## 5)Cấu trúc dự án
.
├─ data/
│  ├─ nlu.yml
│  ├─ rules.yml
│  └─ stories.yml
├─ actions/               # nếu có custom actions
│  └─ actions.py
├─ domain.yml
├─ config.yml
├─ credentials.yml
├─ endpoints.yml          # nếu có actions server
├─ models/                # model sau khi train (có thể không push lên git)
└─ web/
   ├─ index.html
   ├─ styles.css
   └─ app.js              # nếu dùng REST UI

## 6) Train model và chạy
rasa train
rasa run --enable-api --cors "*" --port 5005
rasa run actions --port 5055
## 7) Tích hợp chatbot vào website

Bạn có 2 cách phổ biến:

Cách A (khuyến nghị): Nhúng widget rasa-webchat (Socket.IO)
Bước 1: Bật socketio trong credentials.yml
rest:

socketio:
  session_persistence: true

Bước 2: Nhúng vào file web/index.html (trước </body>)
<script src="https://cdn.jsdelivr.net/npm/rasa-webchat/lib/index.js"></script>
<script>
  WebChat.default(
    {
      initPayload: "/greet",
      customData: { language: "vi" },
      socketUrl: "http://localhost:5005",
      socketPath: "/socket.io/",
      title: "Tư vấn nhập học TVU",
      subtitle: "Online 24/7"
    },
    null
  );
</script>

## 8) Chạy website local (khuyến nghị để tránh lỗi CORS)

Vào thư mục web:

cd web
python -m http.server 8080


