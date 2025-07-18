#### Cấu trúc dự án

    ├── alembic
    ├── alembic.ini
    ├── app
    │   ├── auth
    │   │   ├── email_utils.py                                      #Gửi email xác minh tài khoản hoặc khôi phục mật khẩu qua SMTP
    │   │   └── tokens.                                             #Sinh và kiểm tra JWT tokens cho xác thực người dùng
    │   ├── config.py                                               #Biến môi trường, cài đặt hệ thống (DB URL, LLM API...)
    │   ├── core                                                    
    │   │   ├── constants.py                                        #Biến hằng dùng chung (e.g., roles, cấu hình mặc định)
    │   │   ├── dependencies.py                                     #Inject dependency (current user, token validation) cho route
    │   │   ├── redis.py                                            #Kết nối Redis nếu dùng cache/token blacklist
    │   │   ├── security.                                           #Kiểm tra token.
    │   │   └── utils.py                                            #Hàm tiện ích chung như uuid, time format, gộp văn bản
    │   ├── db
    │   │   ├── database.py                                         
    │   │   ├── models
    │   │   │   ├── chat_model.py                                   #Mô hình lưu lịch sử chat của sinh viên (id, user_id, role, question, answer)
    │   │   │   ├── user_model.py                                   #Mô hình người dùng (admin, student), lưu thông tin, email, mật khẩu, role.
    │   │   │   └── vector_model.py                                 #Mô hình vector embedding (id, content, embedding, metadata).
    │   │   └── schemas
    │   │       ├── chat_schema.py                                  #Schema gửi/nhận dữ liệu chat (question, answer, user_id, role).
    │   │       ├── user_schema.py                                  #Schema tạo user, đăng nhập, trả về thông tin người dùng.
    │   │       └── vector_schema.py                                #Schema embedding (id, content, vector, file metadata).
    │   ├── logger.py                                               #Cấu hình loguru để ghi log hệ thống.
    │   ├── main.py                                                 #Entry point: tạo app FastAPI, gắn route, middleware.
    │   ├── middleware
    │   │   ├── log_request.py                                      #Middleware ghi log tất cả request và thời gian xử lý.
    │   ├── rag
    │   │   ├── chat_pipeline.py                                    #Pipeline thực hiện toàn bộ RAG: retrieve → rerank → prompt → LLM.
    │   │   ├── embedder.py                                         #Tạo embedding từ JSON/PDF, lưu vào PostgreSQL (dùng BGE)
    │   │   ├── llm_chain.py                                        #Tạo prompt và gửi đến LLM (Gemini, OpenRouter).
    │   │   ├── processor_json.py                                   #Xử lý file JSON, chuẩn hóa, phân đoạn và sinh metadata.
    │   │   ├── processor_pdf.py                                    #OCR PDF + phân trang + metadata cho RAG.
    │   │   ├── retriever.py                                        #Truy vấn PostgreSQL vector DB và trả về Top-K documents.
    │   │   ├── text_splitter.py                                    #Chia nhỏ văn bản theo ngữ nghĩa để embedding hiệu quả.
    │   │   └── word_filter.py                                      #Kiểm tra từ cấm trước khi gửi câu hỏi lên LLM.
    │   ├── routers
    │   │   ├── admin.py                                            #API dành riêng cho quản trị viên: tạo user, thống kê, log.
    │   │   ├── auth.py                                             #Đăng ký, đăng nhập, xác thực, đổi mật khẩu.
    │   │   ├── chat.py                                             #API chat cho học sinh/sinh viên, xử lý theo vai trò.
    │   │   └── user.py                                             #API CRUD user, lấy thông tin người dùng hiện tại
    │   └── services
    │       ├── auth_service.py                                     #Logic tạo user, kiểm tra login, mã hóa mật khẩu.
    │       ├── chat_service.py                                     #Logic chính gọi pipeline chat, lưu lịch sử, lọc từ cấm.
    ├── data
    │   ├── admissions_20250623.json                                #Dữ liệu ngành tuyển sinh, dùng làm base knowledge cho học sinh.
    │   ├── admissions_20250623_old.json                            #Dữ liệu ngành tuyển sinh, dùng làm base knowledge cho học sinh.
    │   ├── static
    │   │   └── pdfs                                                #Tài liệu PDF hỗ trợ RAG (trích xuất + OCR + embed).
    │   ├── students_20250623.json                                  #Dữ liệu hướng dẫn sinh viên, cho chatbot sinh viên.
    │   └── word_filter.json                                        #Danh sách từ cấm trong câu hỏi gửi lên LLM.
    ├── logs
    │   └── app.log
    ├── README.md
    ├── requirements.txt
    └── scripts
        ├── create_admin.py                                         #Tạo tài khoản admin đầu tiên qua CLI.
        ├── embed_runner.py                                         #Chạy toàn bộ quy trình embed lại dữ liệu vào DB.
    ├── requirements.txt
    └── Frontend_RAG
        ├── .env
        ├── src
            ├── app
            │   ├── (admin)
            │   │   ├── admin
            │   │   │   ├── dashboard
            │   │   │   │   └── page.tsx                            
            │   │   │   ├── database
            │   │   │   │   └── page.tsx
            │   │   │   └── users
            │   │   │       └── page.tsx
            │   │   └── layout.tsx
            │   ├── change-password
            │   │   └── page.tsx
            │   ├── favicon.ico
            │   ├── forgot-password
            │   │   └── page.tsx
            │   ├── globals.css
            │   ├── layout.tsx
            │   ├── login
            │   │   └── page.tsx
            │   ├── page.tsx
            │   ├── register
            │   │   └── page.tsx
            │   ├── tu-van
            │   │   └── page.tsx
            │   └── (user)
            │       ├── layout.tsx
            │       ├── profile
            │       │   └── page.tsx
            │       └── user
            │           └── home
            │               └── page.tsx
            ├── components
            │   ├── chat
            │   │   └── Chat.tsx
            │   ├── ChatComponent.tsx
            │   ├── emotion
            │   │   ├── cache.ts
            │   │   └── provider.tsx
            │   ├── EmotionProvider.tsx
            │   ├── Footer.tsx
            │   ├── Header.tsx
            │   ├── hooks
            │   │   └── useUser.ts
            │   ├── Icon.tsx
            │   ├── layout
            │   │   ├── admin
            │   │   │   ├── SearchButton.tsx
            │   │   │   ├── Sidebar.tsx
            │   │   │   ├── Topbar.tsx
            │   │   │   ├── UserPagination.tsx
            │   │   │   └── Usertable.tsx
            │   │   └── user
            │   │       ├── Achieve.tsx
            │   │       ├── Hero.tsx
            │   │       ├── Major.tsx
            │   │       ├── NewSection.tsx
            │   │       ├── News.tsx
            │   │       └── RoadPath.tsx
            │   ├── LoadingDot.tsx
            │   ├── store
            │   │   ├── index.tsx
            │   │   └── useUser.ts
            │   └── test.tsx
            ├── config
            │   └── const.ts
            ├── lib
            │   ├── api
            │   │   └── index.ts
            │   ├── db
            │   │   └── db.ts
            │   ├── helper
            │   │   ├── index.ts
            │   │   └── token.ts
            │   └── prisma
            │       └── prisma.ts
            ├── middleware.ts
            ├── services
            │   ├── apis
            │   │   ├── auth.ts
            │   │   ├── chat.ts
            │   │   └── user.ts
            │   └── hooks
            │       ├── hookApi.ts
            │       ├── hookAuth.ts
            │       ├── hookChat.ts
            │       └── hookUser.ts
            └── utils
                └── createEmotionCache.ts

#### PostgreSQL
Để kết nối vào cơ sở dữ liệu PostgreSQL cục bộ:
```bash
psql -U postgres -d chatbot_db -h 127.0.0.1 -p 5432
supersecurepassword

## Tạo bảng
```sql
-- Table: embedding_admissions_20250716
CREATE TABLE IF NOT EXISTS embedding_admissions_20250716 (
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
  chunk_index INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: embedding_students_20250716
CREATE TABLE IF NOT EXISTS embedding_students_20250716 (
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
  chunk_index INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: embedding_pdfs_20250716
CREATE TABLE IF NOT EXISTS embedding_pdfs_20250716 (
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
  page_number INTEGER,
  chunk_index INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  username VARCHAR,
  role VARCHAR DEFAULT 'student',
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE page_views (
  id SERIAL PRIMARY KEY,
  path TEXT NOT NULL,
  viewed_at TIMESTAMP DEFAULT NOW() -- Thời điểm truy cập
);

CREATE TABLE IF NOT EXISTS user_20250627 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR NOT NULL UNIQUE,
  password VARCHAR NOT NULL,
  full_name VARCHAR,
  role VARCHAR DEFAULT 'student',
  is_verified BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  force_password_change BOOLEAN NOT NULL DEFAULT FALSE
);

## .env backend

```env
# Kết nối DB dạng sync - async
DATABASE_URL=postgresql+psycopg2://user:password@host:port/db_name
DATABASE_URL_ASYNC=postgresql+asyncpg://user:password@host:port/db_name

# Số chiều của vector embedding (bge-m3 dùng 1024 chiều)
PGVECTOR_DIM=1024

# Mô hình embedding và LLM
EMBED_MODEL_NAME=BAAI/bge-m3
GEMINI_MODEL=models/gemini-2.0-flash

# Token hết hạn sau 60 phút
JWT_EXPIRE_MINUTES=60
# Domain của API backend
NEXT_PUBLIC_API_BACKEND_DOMAIN=https://your-backend-domain.com

# Chạy backend (FastAPI)
uvicorn app.main:app --reload --port 8000

# Dùng Cloudflared để tạo tunnel ra ngoài
cloudflared tunnel --url http://127.0.0.1:8000

# frontend (Next.js)
npm run dev

https://console.cloud.google.com/auth/clients/710412300912-dft5gs3kocr9el4temggad2fvom9m4b6.apps.googleusercontent.com?inv=1&invt=Ab2XSw&project=chatbot-login-project #thay domain vào đây

uvicorn app.main:app --reload --port 8000
cloudflared tunnel --url http://127.0.0.1:8000
cloudflared tunnel --url http://localhost:3000
npm run dev

