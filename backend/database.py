from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Dùng sqlite, nó sẽ tự tạo 1 file tên là auction.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./auction.db"

# connect_args={"check_same_thread": False} là bắt buộc khi dùng SQLite với FastAPI
engine = create_engine (
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()

# Hàm tạo session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
