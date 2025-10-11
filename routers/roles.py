# routers/roles.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from schemas.roles import RoleCreate, RoleUpdate, RoleOut
from typing import List

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=List[RoleOut])
def list_roles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    q = text("""
        SELECT id, name, is_active, create_date, modify_date
        FROM roles
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    q = text("SELECT id, name, is_active, create_date, modify_date FROM roles WHERE id = :id")
    row = db.execute(q, {"id": role_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return row

@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    q = text("""
        INSERT INTO roles (name, id_user_create)
        OUTPUT INSERTED.id, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        VALUES (:name, NEWID())
    """)
    row = db.execute(q, {"name": payload.name}).mappings().first()
    db.commit()
    return row

@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    # Build dynamic set
    sets = []
    params = {"id": role_id}
    if payload.name is not None:
        sets.append("name = :name")
        params["name"] = payload.name
    if payload.is_active is not None:
        sets.append("is_active = :is_active")
        params["is_active"] = payload.is_active
    if not sets:
        raise HTTPException(status_code=400, detail="Nada para actualizar")

    sets.append("modify_date = SYSDATETIME()")
    q = text(f"""
        UPDATE roles SET {", ".join(sets)}
        OUTPUT INSERTED.id, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.commit()
    return row

@router.delete("/{role_id}", response_model=RoleOut)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    q = text("""
        UPDATE roles SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, {"id": role_id}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.commit()
