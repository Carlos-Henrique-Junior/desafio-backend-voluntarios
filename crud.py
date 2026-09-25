from models import Volunteer, Disponibilidade
from schemas import VolunteerCreate
from datetime import datetime
from fastapi import HTTPException
from typing import Optional

# Simulação de banco de dados em memória
db: list[Volunteer] = []
current_id = 1


def reset_database() -> None:
    """Reset the in-memory store for tests and local development."""
    global current_id
    db.clear()
    current_id = 1

def create_volunteer(volunteer_in: VolunteerCreate) -> Volunteer:
    global current_id
    
    # Validação: Verificar se o email já existe e está ativo
    for v in db:
        if v.email == volunteer_in.email and v.active:
            raise HTTPException(status_code=400, detail="Email já registado.")

    # Cria o novo voluntário com os dados recebidos
    new_volunteer = Volunteer(
        id=current_id,
        name=volunteer_in.name,
        email=volunteer_in.email,
        telefone=volunteer_in.telefone,
        cargo_pretendido=volunteer_in.cargo_pretendido,
        disponibilidade=volunteer_in.disponibilidade,
        active=True,
        created_at=datetime.now()
    )
    
    db.append(new_volunteer)
    current_id += 1
    return new_volunteer

def list_volunteers(
    disponibilidade: Optional[Disponibilidade] = None,
    cargo: Optional[str] = None,
) -> list[Volunteer]:
    return [
        volunteer for volunteer in db
        if volunteer.active
        and (disponibilidade is None or volunteer.disponibilidade == disponibilidade)
        and (cargo is None or volunteer.cargo_pretendido == cargo)
    ]

def get_volunteer(vol_id: int) -> Optional[Volunteer]:
    return next((v for v in db if v.id == vol_id and v.active), None)

def update_volunteer(vol_id: int, volunteer_in: VolunteerCreate) -> Optional[Volunteer]:
    for v in db:
        if v.id == vol_id and v.active:
            v.name = volunteer_in.name
            v.email = volunteer_in.email
            v.telefone = volunteer_in.telefone
            v.cargo_pretendido = volunteer_in.cargo_pretendido
            v.disponibilidade = volunteer_in.disponibilidade
            return v
    return None

def delete_volunteer(vol_id: int) -> Optional[Volunteer]:
    for v in db:
        if v.id == vol_id and v.active:
            v.active = False  # Soft delete
            return v
    return None