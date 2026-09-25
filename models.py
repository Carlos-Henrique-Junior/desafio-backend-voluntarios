from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from pydantic import Field


class Disponibilidade(str, Enum):
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"

class Volunteer(BaseModel):
    id: int
    name: str
    email: EmailStr
    telefone: str
    cargo_pretendido: str
    disponibilidade: Disponibilidade
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)