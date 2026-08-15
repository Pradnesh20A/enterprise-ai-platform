import requests
import psycopg2

conn = psycopg2.connect("dbname=enterprise_ai user=postgres")
cur = conn.cursor()
cur.execute("SELECT id FROM users LIMIT 1")
user_id = cur.fetchone()[0]

from app.core.security import create_access_token
token = create_access_token(user_id)

r = requests.post('http://localhost:8000/api/v1/qa/ask', 
                  json={'question': 'what document?'}, 
                  headers={'Authorization': f'Bearer {token}'})
print(r.status_code)
print(r.text)
