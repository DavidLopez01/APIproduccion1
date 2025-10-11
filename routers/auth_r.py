# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from core.security import verify_password, create_access_token, needs_rehash, hash_password
from schemas.auth import Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/token", response_model=Token)
def login_for_access_token(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    # Traemos login y usuario activo
    q = text("""
        SELECT l.id, l.username, l.password_hash, l.id_user, l.is_active, u.is_active AS user_active
        FROM login l
        INNER JOIN users u ON u.id_user = l.id_user
        WHERE l.username = :username
    """)
    row = db.execute(q, {"username": payload.username}).mappings().first()

    if not row or not row["is_active"] or not row["user_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales inválidas"
        )

    # Verifica contraseña (bcrypt primero; fallback SHA-256 legacy)
    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales inválidas"
        )

    # Upgrade silencioso de hash si es necesario
    try:
        if needs_rehash(row["password_hash"]):
            new_hash = hash_password(payload.password)
            db.execute(
                text("UPDATE login SET password_hash = :ph WHERE id = :id"),
                {"ph": new_hash, "id": row["id"]}
            )
            db.commit()
    except Exception:
        pass  # no bloqueamos login si falla

    # Emitimos JWT con id_user como 'sub'
    access_token = create_access_token({"sub": str(row["id_user"])})
    return {"access_token": access_token, "token_type": "bearer"}
