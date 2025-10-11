# routers/login.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from schemas.login import LoginCreate, LoginUpdate, LoginOut
from typing import List
from uuid import UUID
import hashlib

router = APIRouter(prefix="/login", tags=["Login"])

def hash_password(raw: str) -> str:
    # Reemplaza por passlib[bcrypt] si está disponible
    return hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()

@router.get("/", response_model=List[LoginOut])
def list_logins(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    q = text("""
        SELECT id, username, id_user, is_active, create_date, modify_date
        FROM login
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{id}", response_model=LoginOut)
def get_login(id: int, db: Session = Depends(get_db)):
    q = text("""
        SELECT id, username, id_user, is_active, create_date, modify_date
        FROM login WHERE id = :id
    """)
    row = db.execute(q, {"id": id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Registro de login no encontrado")
    return row

@router.post("/", response_model=LoginOut, status_code=status.HTTP_201_CREATED)
def create_login(payload: LoginCreate, db: Session = Depends(get_db)):
    # Enforce unique username (db también tiene UNIQUE)
    exists_q = text("SELECT 1 FROM login WHERE username = :u")
    if db.execute(exists_q, {"u": payload.username}).first():
        raise HTTPException(status_code=409, detail="El username ya existe")

    q = text("""
        INSERT INTO login (username, password_hash, id_user, id_user_create)
        OUTPUT INSERTED.id, INSERTED.username, INSERTED.id_user, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        SELECT :username, :password_hash, :id_user, NEWID()
    """)
    params = {
        "username": payload.username,
        "password_hash": hash_password(payload.password),
        "id_user": str(payload.id_user),
    }
    row = db.execute(q, params).mappings().first()
    db.commit()
    return row

@router.put("/{id}", response_model=LoginOut)
def update_login(id: int, payload: LoginUpdate, db: Session = Depends(get_db)):
    sets = []
    params = {"id": id}
    if payload.username is not None:
        # check uniqueness
        exists_q = text("SELECT 1 FROM login WHERE username = :u AND id <> :id")
        if db.execute(exists_q, {"u": payload.username, "id": id}).first():
            raise HTTPException(status_code=409, detail="El username ya está en uso")
        sets.append("username = :username")
        params["username"] = payload.username
    if payload.password is not None:
        sets.append("password_hash = :password_hash")
        params["password_hash"] = hash_password(payload.password)
    if payload.is_active is not None:
        sets.append("is_active = :is_active")
        params["is_active"] = payload.is_active
    if not sets:
        raise HTTPException(status_code=400, detail="Nada para actualizar")

    sets.append("modify_date = SYSDATETIME()")
    q = text(f"""
        UPDATE login SET {", ".join(sets)}
        OUTPUT INSERTED.id, INSERTED.username, INSERTED.id_user, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Registro de login no encontrado")
    db.commit()
    return row

@router.delete("/{id}", response_model=LoginOut)
def delete_login(id: int, db: Session = Depends(get_db)):
    q = text("""
        UPDATE login SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id, INSERTED.username, INSERTED.id_user, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, {"id": id}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Registro de login no encontrado")
    db.commit()
    return row