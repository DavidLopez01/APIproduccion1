# routers/subjects.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from schemas.subjects import SubjectCreate, SubjectUpdate, SubjectOut
from typing import List
from uuid import UUID

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("/", response_model=List[SubjectOut])
def list_subjects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    q = text("""
        SELECT id_subj, name, credits, id_area, is_active, create_date, modify_date
        FROM subjects
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{id_subj}", response_model=SubjectOut)
def get_subject(id_subj: UUID, db: Session = Depends(get_db)):
    q = text("""
        SELECT id_subj, name, credits, id_area, is_active, create_date, modify_date
        FROM subjects WHERE id_subj = :id_subj
    """)
    row = db.execute(q, {"id_subj": str(id_subj)}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return row

@router.post("/", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    q = text("""
        INSERT INTO subjects (id_subj, name, credits, id_area, id_user_create)
        OUTPUT INSERTED.id_subj, INSERTED.name, INSERTED.credits, INSERTED.id_area, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        VALUES (NEWID(), :name, :credits, :id_area, NEWID())
    """)
    params = {
        "name": payload.name,
        "credits": payload.credits,
        "id_area": payload.id_area
    }
    row = db.execute(q, params).mappings().first()
    db.commit()
    return row

@router.put("/{id_subj}", response_model=SubjectOut)
def update_subject(id_subj: UUID, payload: SubjectUpdate, db: Session = Depends(get_db)):
    sets = []
    params = {"id_subj": str(id_subj)}
    if payload.name is not None:
        sets.append("name = :name")
        params["name"] = payload.name
    if payload.credits is not None:
        sets.append("credits = :credits")
        params["credits"] = payload.credits
    if payload.id_area is not None:
        sets.append("id_area = :id_area")
        params["id_area"] = payload.id_area
    if payload.is_active is not None:
        sets.append("is_active = :is_active")
        params["is_active"] = payload.is_active
    if not sets:
        raise HTTPException(status_code=400, detail="Nada para actualizar")
    sets.append("modify_date = SYSDATETIME()")
    q = text(f"""
        UPDATE subjects SET {", ".join(sets)}
        OUTPUT INSERTED.id_subj, INSERTED.name, INSERTED.credits, INSERTED.id_area, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_subj = :id_subj
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    db.commit()
    return row

@router.delete("/{id_subj}", response_model=SubjectOut)
def delete_subject(id_subj: UUID, db: Session = Depends(get_db)):
    q = text("""
        UPDATE subjects SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id_subj, INSERTED.name, INSERTED.credits, INSERTED.id_area, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id_subj = :id_subj
    """)
    row = db.execute(q, {"id_subj": str(id_subj)}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    db.commit()
    return row