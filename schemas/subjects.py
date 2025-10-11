# schemas/subjects.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict
from pydantic import BaseModel, constr, conint

class SubjectBase(BaseModel):
    name: constr(strip_whitespace=True, max_length=100)
    credits: conint(ge=0, le=99)
    id_area: Optional[int] = None

class SubjectCreate(SubjectBase):
    pass  # id_subj lo genera NEWID()

class SubjectUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=100)] = None
    credits: Optional[conint(ge=0, le=99)] = None
    id_area: Optional[int] = None
    is_active: Optional[bool] = None

class SubjectOut(BaseModel):
    id_subj: UUID
    name: str
    credits: int
    id_area: Optional[int] = None
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None


class TuSchema(BaseModel):
    ...
    model_config = ConfigDict(from_attributes=True)