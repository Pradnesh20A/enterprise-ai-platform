import asyncio
import sys
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.database import engine, Base
from app.models.user import User
from app.models.document import Document, DocumentChunk

async def recreate_tables():
    async with engine.begin() as conn:
        print("Dropping tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
