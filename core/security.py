# core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt  # pip install "python-jose[cryptography]"
import hashlib

from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# --- Passlib (bcrypt) + compatibilidad con hashes antiguos ---
try:
    from passlib.context import CryptContext
    from passlib.exc import UnknownHashError

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(raw: str) -> str:
        # Siempre generamos bcrypt para lo nuevo
        return pwd_context.hash(raw)

    def _verify_bcrypt(raw: str, stored: str) -> Optional[bool]:
        try:
            return pwd_context.verify(raw, stored)
        except UnknownHashError:
            # El hash no es bcrypt ni reconocido por passlib (probablemente legacy)
            return None
        except Exception:
            return False

    def verify_password(raw: str, stored: str) -> bool:
        """
        Verifica primero bcrypt (passlib). Si el hash no es reconocido,
        hace fallback a legacy SHA-256 (hex).
        """
        ok = _verify_bcrypt(raw, stored)
        if ok is True:
            return True
        if ok is False:
            return False

        # Fallback legacy: SHA-256 hexdigest (compatible con seed SQL Server)
        legacy = hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
        return stored.upper() == legacy

    def needs_rehash(stored: str) -> bool:
        """
        Indica si debemos reescribir el hash (por ejemplo, si es legacy SHA-256
        o un bcrypt con parámetros antiguos).
        """
        try:
            return pwd_context.needs_update(stored)
        except Exception:
            # Si passlib no reconoce el formato (legacy), conviene migrarlo
            return True

except Exception:
    # Sin passlib instalado: usar SHA-256 plano (SOLO pruebas)
    def hash_password(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_password(raw: str, stored: str) -> bool:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest() == stored

    def needs_rehash(stored: str) -> bool:
        # No podemos mejorar sin passlib
        return False

# --- JWT ---
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene ID de usuario",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

