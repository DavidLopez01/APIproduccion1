# schemas/users.py
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict
from pydantic import BaseModel, constr, conint

class UserBase(BaseModel):
    name: constr(strip_whitespace=True, max_length=50)
    last_name: constr(strip_whitespace=True, max_length=50)
    id_role: conint(gt=0)
    birthdate: date

class UserCreate(UserBase):
    pass  # id_user lo genera NEWID() en SQL Server

class UserUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=50)] = None
    last_name: Optional[constr(strip_whitespace=True, max_length=50)] = None
    id_role: Optional[conint(gt=0)] = None
    birthdate: Optional[date] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id_user: UUID
    name: str
    last_name: str
    id_role: int
    birthdate: date
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None

class TuSchema(BaseModel):
    ...
    model_config = ConfigDict(from_attributes=True)