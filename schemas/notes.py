# schemas/notes.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import ConfigDict
from pydantic import BaseModel, condecimal

class NoteBase(BaseModel):
    id_user: UUID
    id_subj: UUID
    grade: condecimal(max_digits=4, decimal_places=2)

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    grade: Optional[condecimal(max_digits=4, decimal_places=2)] = None
    is_active: Optional[bool] = None

class NoteOut(BaseModel):
    id: int
    id_user: UUID
    id_subj: UUID
    grade: Decimal
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None


class TuSchema(BaseModel):
    ...
    model_config = ConfigDict(from_attributes=True)
