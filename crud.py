from datetime import datetime

from fastapi import HTTPException

from models import Disponibilidade, Volunteer
from schemas import VolunteerCreate

# Simulação de banco de dados em memória
db: list[Volunteer] = []
current_id = 1


def reset_database() -> None:
    """Reset the in-memory store for tests and local development."""
    global current_id
    db.clear()
    current_id = 1


def _email_in_use(email: str, exclude_id: int | None = None) -> bool:
    """Check whether an active volunteer already uses the given email."""
    normalized = email.lower()
    return any(
        v.active and v.id != exclude_id and v.email.lower() == normalized
        for v in db
    )


def create_volunteer(volunteer_in: VolunteerCreate) -> Volunteer:
    global current_id

    # Validação: Verificar se o email já existe e está ativo
    if _email_in_use(volunteer_in.email):
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
    disponibilidade: Disponibilidade | None = None,
    cargo: str | None = None,
) -> list[Volunteer]:
    return [
        volunteer for volunteer in db
        if volunteer.active
        and (disponibilidade is None or volunteer.disponibilidade == disponibilidade)
        and (cargo is None or volunteer.cargo_pretendido == cargo)
    ]


def get_volunteer(vol_id: int) -> Volunteer | None:
    return next((v for v in db if v.id == vol_id and v.active), None)


def update_volunteer(vol_id: int, volunteer_in: VolunteerCreate) -> Volunteer | None:
    volunteer = get_volunteer(vol_id)
    if volunteer is None:
        return None

    if _email_in_use(volunteer_in.email, exclude_id=vol_id):
        raise HTTPException(status_code=400, detail="Email já registado.")

    volunteer.name = volunteer_in.name
    volunteer.email = volunteer_in.email
    volunteer.telefone = volunteer_in.telefone
    volunteer.cargo_pretendido = volunteer_in.cargo_pretendido
    volunteer.disponibilidade = volunteer_in.disponibilidade
    return volunteer


def delete_volunteer(vol_id: int) -> Volunteer | None:
    volunteer = get_volunteer(vol_id)
    if volunteer is None:
        return None
    volunteer.active = False  # Soft delete
    return volunteer
