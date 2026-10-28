from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db_models import VolunteerRecord
from models import Disponibilidade, Volunteer
from schemas import VolunteerCreate


def _to_api_model(record: VolunteerRecord) -> Volunteer:
    return Volunteer(
        id=record.id,
        name=record.name,
        email=record.email,
        telefone=record.telefone,
        cargo_pretendido=record.cargo_pretendido,
        disponibilidade=Disponibilidade(record.disponibilidade),
        active=record.active,
        created_at=record.created_at,
    )


def _email_in_use(
    db: Session,
    email: str,
    exclude_id: int | None = None,
) -> bool:
    statement = select(VolunteerRecord.id).where(
        VolunteerRecord.active.is_(True),
        func.lower(VolunteerRecord.email) == email.lower(),
    )
    if exclude_id is not None:
        statement = statement.where(VolunteerRecord.id != exclude_id)
    return db.scalar(statement.limit(1)) is not None


def _commit_or_raise_email_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já registado.") from error


def create_volunteer(db: Session, volunteer_in: VolunteerCreate) -> Volunteer:
    if _email_in_use(db, volunteer_in.email):
        raise HTTPException(status_code=400, detail="Email já registado.")

    record = VolunteerRecord(
        name=volunteer_in.name,
        email=volunteer_in.email,
        telefone=volunteer_in.telefone,
        cargo_pretendido=volunteer_in.cargo_pretendido,
        disponibilidade=volunteer_in.disponibilidade.value,
        active=True,
    )
    db.add(record)
    _commit_or_raise_email_conflict(db)
    db.refresh(record)
    return _to_api_model(record)


def list_volunteers(
    db: Session,
    disponibilidade: Disponibilidade | None = None,
    cargo: str | None = None,
) -> list[Volunteer]:
    statement = select(VolunteerRecord).where(VolunteerRecord.active.is_(True))
    if disponibilidade is not None:
        statement = statement.where(
            VolunteerRecord.disponibilidade == disponibilidade.value
        )
    if cargo is not None:
        statement = statement.where(VolunteerRecord.cargo_pretendido == cargo)
    records = db.scalars(statement.order_by(VolunteerRecord.id)).all()
    return [_to_api_model(record) for record in records]


def get_volunteer(db: Session, vol_id: int) -> Volunteer | None:
    record = db.scalar(
        select(VolunteerRecord).where(
            VolunteerRecord.id == vol_id,
            VolunteerRecord.active.is_(True),
        )
    )
    return _to_api_model(record) if record is not None else None


def update_volunteer(
    db: Session,
    vol_id: int,
    volunteer_in: VolunteerCreate,
) -> Volunteer | None:
    record = db.scalar(
        select(VolunteerRecord).where(
            VolunteerRecord.id == vol_id,
            VolunteerRecord.active.is_(True),
        )
    )
    if record is None:
        return None

    if _email_in_use(db, volunteer_in.email, exclude_id=vol_id):
        raise HTTPException(status_code=400, detail="Email já registado.")

    record.name = volunteer_in.name
    record.email = volunteer_in.email
    record.telefone = volunteer_in.telefone
    record.cargo_pretendido = volunteer_in.cargo_pretendido
    record.disponibilidade = volunteer_in.disponibilidade.value
    _commit_or_raise_email_conflict(db)
    db.refresh(record)
    return _to_api_model(record)


def delete_volunteer(db: Session, vol_id: int) -> Volunteer | None:
    record = db.scalar(
        select(VolunteerRecord).where(
            VolunteerRecord.id == vol_id,
            VolunteerRecord.active.is_(True),
        )
    )
    if record is None:
        return None

    record.active = False
    db.commit()
    db.refresh(record)
    return _to_api_model(record)
