import asyncio
import asyncpg
from app.core.config import settings

async def run():
    dsn = settings.DATABASE_URL.replace('+asyncpg', '')
    conn = await asyncpg.connect(dsn)
    user_id = await conn.fetchval("SELECT id FROM users LIMIT 1")
    await conn.close()
    
    from app.core.security import create_access_token
    import requests
    
    token = create_access_token(user_id)
    r = requests.post('http://localhost:8000/api/v1/qa/ask', 
                      json={'question': 'what document?'}, 
                      headers={'Authorization': f'Bearer {token}'})
    print("STATUS", r.status_code)
    print("BODY", r.text)

asyncio.run(run())
