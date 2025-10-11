from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMjA5RjZGQy1ENDc0LTRGMDItOThGNS05QkVCNUU4NDk2NTIiLCJleHAiOjE3NjAwNzA1NjV9.5UCzhN0t6luDpFhWIW9cnTmZeRUcmyLOuwYO-TI8CEQ"

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("✅ Decodificado OK. payload =", payload)
except Exception as e:
    print("❌ Error al decodificar token:", type(e).__name__, e)
