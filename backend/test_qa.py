import asyncio
from app.db.database import SessionLocal
from app.api.qa import ask_question
from app.schemas.qa import QARequest
from app.models.user import User
from sqlalchemy import select

async def run():
    async with SessionLocal() as db:
        user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        if not user:
            print("No user found")
            return
            
        request = QARequest(question="what document?")
        try:
            res = await ask_question(request=request, db=db, current_user=user)
            print(res)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
