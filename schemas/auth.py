# schemas/auth.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)

class CurrentUser(BaseModel):
    id_user: UUID
    name: str
    last_name: str
    id_role: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

# 👇 Necesario para /auth/token con JSON
class LoginRequest(BaseModel):
    username: str
    password: str