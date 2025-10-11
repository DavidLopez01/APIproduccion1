from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from uuid import UUID
from fastapi.security import HTTPAuthorizationCredentials

from deps.db import get_db
from deps.auth import get_current_user  # Ahora usa Security
from schemas.users import UserCreate, UserUpdate, UserOut
from schemas.auth import CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserOut], summary="Listar usuarios")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    offset = (page - 1) * size
    q = text("""
        SELECT id_user, name, last_name, id_role, birthdate, is_active, create_date, modify_date
        FROM users
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{id_user}", response_model=UserOut, summary="Obtener usuario")
def get_user(
    id_user: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    q = text("""
        SELECT id_user, name, last_name, id_role, birthdate, is_active, create_date, modify_date
        FROM users
        WHERE id_user = :id_user
    """)
    row = db.execute(q, {"id_user": str(id_user)}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return row

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="Crear usuario")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    q = text("""
        INSERT INTO users (id_user, name, last_name, id_role, birthdate, id_user_create)
        OUTPUT INSERTED.id_user, INSERTED.name, INSERTED.last_name, INSERTED.id_role, INSERTED.birthdate,
               INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        VALUES (NEWID(), :name, :last_name, :id_role, :birthdate, NEWID())
    """)
    params = {
        "name": payload.name,
        "last_name": payload.last_name,
        "id_role": payload.id_role,
        "birthdate": payload.birthdate
    }
    row = db.execute(q, params).mappings().first()
    db.commit()
    return row

@router.put("/{id_user}", response_model=UserOut, summary="Actualizar usuario")
def update_user(
    id_user: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    sets = []
    params = {"id_user": str(id_user)}
    if payload.name is not None:
        sets.append("name = :name")
        params["name"] = payload.name
    if payload.last_name is not None:
        sets.append("last_name = :last_name")
        params["last_name"] = payload.last_name
    if payload.id_role is not None:
        sets.append("id_role = :id_role")
        params["id_role"] = payload.id_role
    if payload.birthdate is not None:
        sets.append("birthdate = :birthdate")
        params["birthdate"] = payload.birthdate
    if payload.is_active is not None:
        sets.append("is_active = :is_active")
        params["is_active"] = payload.is_active
    if not sets:
        raise HTTPException(status_code=400, detail="Nada para actualizar")

    sets.append("modify_date = SYSDATETIME()")
    q = text(f"""
        UPDATE users SET {", ".join(sets)}
        OUTPUT INSERTED.id_user, INSERTED.name, INSERTED.last_name, INSERTED.id_role, INSERTED.birthdate,
               INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_user = :id_user
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.commit()
    return row

@router.delete("/{id_user}", response_model=UserOut, summary="Eliminar usuario")
def delete_user(
    id_user: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    q = text("""
        UPDATE users SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id_user, INSERTED.name, INSERTED.last_name, INSERTED.id_role, INSERTED.birthdate,
               INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_user = :id_user
    """)
    row = db.execute(q, {"id_user": str(id_user)}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.commit()
    return row
