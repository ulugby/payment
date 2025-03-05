from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from payment.settings import DB_URL

# Database URL orqali ulanishni sozlash
engine = create_async_engine(DB_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Helper funksiyasi so'rovni bajarish uchun
async def execute_query(query):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(text(query))
            await session.commit()
            return result