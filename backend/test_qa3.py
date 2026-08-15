import requests
import sys

user_id = sys.argv[1]
if not user_id:
    print("no user")
    sys.exit(1)

from app.core.security import create_access_token
token = create_access_token(user_id)

r = requests.post('http://localhost:8000/api/v1/qa/ask', 
                  json={'question': 'what document?'}, 
                  headers={'Authorization': f'Bearer {token}'})
print(r.status_code)
print(r.text)
