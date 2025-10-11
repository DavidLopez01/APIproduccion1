# deps/auth.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt, JWTError

from deps.db import get_db
from core.config import SECRET_KEY, ALGORITHM
from schemas.auth import CurrentUser

# Esquema Bearer para Swagger
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    token = credentials.credentials
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodificar JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    # Consultar usuario activo
    query = text("""
        SELECT id_user, name, last_name, id_role, is_active
        FROM users
        WHERE id_user = :uid
    """)
    row = db.execute(query, {"uid": user_id}).mappings().first()
    if not row or not row["is_active"]:
        raise credentials_exc

    return CurrentUser(**row)
