# schemas/roles.py
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from pydantic import BaseModel, constr

class RoleBase(BaseModel):
    name: constr(strip_whitespace=True, max_length=100)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=100)] = None
    is_active: Optional[bool] = None

class RoleOut(BaseModel):
    id: int
    name: str
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None


class TuSchema(BaseModel):
    ...
    model_config = ConfigDict(from_attributes=True)