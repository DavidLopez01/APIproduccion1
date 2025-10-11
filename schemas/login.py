from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, constr

# --- Base ---
class LoginBase(BaseModel):
    username: constr(strip_whitespace=True, max_length=100)
    id_user: UUID

# --- Crear login (input) ---
class LoginCreate(LoginBase):
    password: constr(min_length=6, max_length=128)  # Solo input; se hashea en el router

# --- Actualizar login (input) ---
class LoginUpdate(BaseModel):
    username: Optional[constr(strip_whitespace=True, max_length=100)] = None
    password: Optional[constr(min_length=6, max_length=128)] = None
    is_active: Optional[bool] = None

# --- Salida (output) ---
class LoginOut(BaseModel):
    id: int
    username: str
    id_user: UUID
    is_active: bool
    create_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None

    # Pydantic v2: reemplaza orm_mode por from_attributes
    model_config = ConfigDict(from_attributes=True)