"""
비동기 데이터베이스 연결 및 세션 관리
"""

import os
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

# 환경변수 로드 (로컬에서만)
if os.getenv("ENV", "local") == "local":
    load_dotenv()

# 데이터베이스 URL (asyncpg 포맷이어야 함)
DATABASE_URL = os.getenv("DATABASE_URL")

print("📴📵🚸🚼 DATABASE_URL in runtime:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경변수가 없습니다.")

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# 비동기 세션팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Base 선언
Base = declarative_base()

# 세션 제공 의존성 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 테이블 자동 생성 제거됨 (Base.metadata.create_all 삭제)
