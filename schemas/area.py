# schemas/area.py
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from pydantic import BaseModel, constr

class AreaBase(BaseModel):
    name: constr(strip_whitespace=True, max_length=100)

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=100)] = None
    is_active: Optional[bool] = None

class AreaOut(BaseModel):
    id_area: int
    name: str
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None


    class TuSchema(BaseModel):
        ...
        model_config = ConfigDict(from_attributes=True)