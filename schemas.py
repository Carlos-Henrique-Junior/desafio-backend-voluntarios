from pydantic import BaseModel, EmailStr, Field

from models import Disponibilidade


class VolunteerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    telefone: str = Field(pattern=r"^\d{10,11}$")
    cargo_pretendido: str = Field(min_length=1, max_length=100)
    disponibilidade: Disponibilidade
