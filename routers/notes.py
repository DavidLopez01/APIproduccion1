# routers/notes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from deps.db import get_db
from schemas.notes import NoteCreate, NoteUpdate, NoteOut
from typing import List

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.get("/", response_model=List[NoteOut])
def list_notes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    q = text("""
        SELECT id, id_user, id_subj, grade, is_active, create_date, modify_date
        FROM notes
        ORDER BY create_date DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
    """)
    rows = db.execute(q, {"offset": offset, "size": size}).mappings().all()
    return rows

@router.get("/{id}", response_model=NoteOut)
def get_note(id: int, db: Session = Depends(get_db)):
    q = text("""
        SELECT id, id_user, id_subj, grade, is_active, create_date, modify_date
        FROM notes WHERE id = :id
    """)
    row = db.execute(q, {"id": id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return row

@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    q = text("""
        INSERT INTO notes (id_user, id_subj, grade, id_user_create)
        OUTPUT INSERTED.id, INSERTED.id_user, INSERTED.id_subj, INSERTED.grade, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        VALUES (:id_user, :id_subj, :grade, NEWID())
    """)
    params = {
        "id_user": str(payload.id_user),
        "id_subj": str(payload.id_subj),
        "grade": payload.grade
    }
    row = db.execute(q, params).mappings().first()
    db.commit()
    return row

@router.put("/{id}", response_model=NoteOut)
def update_note(id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    sets = []
    params = {"id": id}
    if payload.grade is not None:
        sets.append("grade = :grade")
        params["grade"] = payload.grade
    if payload.is_active is not None:
        sets.append("is_active = :is_active")
        params["is_active"] = payload.is_active
    if not sets:
        raise HTTPException(status_code=400, detail="Nada para actualizar")
    sets.append("modify_date = SYSDATETIME()")
    q = text(f"""
        UPDATE notes SET {", ".join(sets)}
        OUTPUT INSERTED.id, INSERTED.id_user, INSERTED.id_subj, INSERTED.grade, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, params).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.commit()
    return row

@router.delete("/{id}", response_model=NoteOut)
def delete_note(id: int, db: Session = Depends(get_db)):
    q = text("""
        UPDATE notes SET is_active = 0, modify_date = SYSDATETIME()
        OUTPUT INSERTED.id, INSERTED.id_user, INSERTED.id_subj, INSERTED.grade, INSERTED.is_active, INSERTED.create_date, INSERTED.modify_date
        WHERE id = :id
    """)
    row = db.execute(q, {"id": id}).mappings().first()
    if not row:
        db.rollback()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.commit()
    return row
