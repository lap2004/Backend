chatbot/
├── app/                            # 🧠 Toàn bộ backend logic FastAPI
│   ├── __init__.py
│   ├── main.py                     # ✅ Entry Point FastAPI
│   ├── config.py                   # ✅ Load .env, thiết lập config
│   ├── logger.py                   # ✅ Log hệ thống dùng Loguru

│   ├── core/                       # ⚙️ Logic lõi & tiện ích
│   │   ├── constants.py            # Enum, Role, BotType...
│   │   ├── security.py             # Xử lý JWT, mật khẩu
│   │   └── utils.py                # Hàm tiện ích chung

│   ├── auth/                       # 🔐 Xác thực & Email
│   │   ├── tokens.py               # JWT tạo & xác minh
│   │   └── email_utils.py          # Gửi mail verify

│   ├── routers/                    # 🌐 Định tuyến API
│   │   ├── auth.py                 # /auth/signup, /login
│   │   └── chat.py                 # /chat/student, /chat/admission

│   ├── services/                   # 📦 Logic nghiệp vụ
│   │   ├── auth_service.py         # Đăng nhập / đăng ký
│   │   └── chat_service.py         # Gọi pipeline + lưu log

│   ├── middleware/                 # 🛡️ Middleware cho app
│   │   └── log_request.py          # Ghi log mỗi request

│   ├── db/                         # 🗃️ Kết nối & mô hình CSDL
│   │   ├── database.py             # Kết nối PostgreSQL
│   │   ├── models/                 # SQLAlchemy ORM
│   │   │   ├── user_model.py
│   │   │   ├── chat_model.py
│   │   │   └── vector_model.py
│   │   └── schemas/                # Pydantic Schemas
│   │       ├── user_schema.py
│   │       ├── chat_schema.py
│   │       └── vector_schema.py

│   ├── rag/                        # 🔍 RAG (Retrieval-Augmented Generation)
│   │   ├── embedder.py             # Tạo vector embedding
│   │   ├── processor_json.py       # Xử lý file JSON
│   │   ├── processor_pdf.py        # Xử lý PDF
│   │   ├── retriever.py            # Truy vấn vector
│   │   ├── llm_chain.py            # Gọi LLM như Gemini
│   │   ├── chat_pipeline.py        # Pipeline xử lý câu hỏi
│   │   ├── word_filter.py          # Lọc từ nhạy cảm
│   │   └── text_splitter.py        # Chia đoạn văn bản (tuỳ chọn)

├── scripts/                        # 🛠️ Script chạy ngoài
│   └── embed_runner.py             # Chạy nhúng dữ liệu vào DB

├── data/                           # 📂 Dữ liệu thô
│   ├── admissions.json
│   ├── students.json
│   └── static/
│       └── pdfs/                   # Tài liệu PDF

├── alembic/                        # ⚙️ Migration DB (nếu dùng)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini

├── .env                            # Biến môi trường
├── requirements.txt                # Dependencies
├── README.md                       # Mô tả dự án

psql -U postgres -d chatbot_db -h 127.0.0.1 -p 5432
supersecurepassword

CREATE TABLE IF NOT EXISTS embedding_admissions_20250627 (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    type TEXT,
    field TEXT,
    source TEXT,
    title_raw TEXT,
    ma_nganh TEXT,
    doi_tuong TEXT,
    chunk_index INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS embedding_students_20250627 (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    type TEXT,
    field TEXT,
    source TEXT,
    title_raw TEXT,
    ma_nganh TEXT,
    doi_tuong TEXT,
    chunk_index INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS embedding_pdfs_20250627 (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    type TEXT,
    field TEXT,
    source TEXT,
    title_raw TEXT,
    ma_nganh TEXT,
    doi_tuong TEXT,
    filename TEXT,
    file_type TEXT,
    page_number INT,
    chunk_index INT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'student',           -- Nên thêm trường role để phân biệt admin/student
    is_active BOOLEAN DEFAULT TRUE,        -- Nên thêm để đánh dấu tài khoản còn hoạt động
    is_verified BOOLEAN DEFAULT FALSE,     -- Nếu bạn có dùng xác minh email
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- <<== sửa tên thành "password", bỏ hash
    full_name TEXT,
    role TEXT DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
