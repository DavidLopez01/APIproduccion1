from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from schemas.area import AreaCreate, AreaUpdate, AreaOut
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from core.security import verificar_token  # ✅ Importación correcta

router = APIRouter(prefix="/areas", tags=["Areas"])

@router.get("/", response_model=List[AreaOut])
def list_areas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verificar_token)  # ✅ Token requerido
):
    offset = (page - 1) * size
    q = text("""
        SELECT id_area, name, is_active, create_date, modify_date
        FROM area
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{id_area}", response_model=AreaOut)
def get_area(
    id_area: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verificar_token)  # ✅ Token requerido
):
    q = text("""
        SELECT id_area, name, is_active, create_date, modify_date
        FROM area WHERE id_area = :id_area
    """)
    row = db.execute(q, {"id_area": id_area}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    return row

@router.post("/", response_model=AreaOut, status_code=status.HTTP_201_CREATED)
def create_area(
    payload: AreaCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verificar_token)  # ✅ Token requerido
):
    q = text("""
        INSERT INTO area (name, id_user_create)
        OUTPUT INSERTED.id_area, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        VALUES (:name, NEWID())
    """)
    row = db.execute(q, {"name": payload.name}).mappings().first()
    db.commit()
    return row

@router.put("/{id_area}", response_model=AreaOut)
def update_area(
    id_area: int,
    payload: AreaUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verificar_token)  # ✅ Token requerido
):
    sets = []
    params = {"id_area": id_area}
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
        UPDATE area SET {", ".join(sets)}
        OUTPUT INSERTED.id_area, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_area = :id_area
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Área no encontrada")
    db.commit()
    return row

@router.delete("/{id_area}", response_model=AreaOut)
def delete_area(
    id_area: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verificar_token)  # ✅ Token requerido
):
    q = text("""
        UPDATE area SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id_area, INSERTED.name, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_area = :id_area
    """)
    row = db.execute(q, {"id_area": id_area}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Área no encontrada")
    db.commit()
    return row
