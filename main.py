import os
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from crud import (
    create_volunteer,
    delete_volunteer,
    get_volunteer,
    list_volunteers,
    update_volunteer,
)
from database import Base, create_database_engine, create_session_factory
from db_models import VolunteerRecord  # Registers the ORM table with Base.metadata.
from models import Disponibilidade, Volunteer
from schemas import VolunteerCreate


def create_app(database_url: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        resolved_database_url = database_url or os.getenv("DATABASE_URL")
        if not resolved_database_url:
            raise RuntimeError(
                "DATABASE_URL is required; configure a PostgreSQL connection string."
            )

        engine = create_database_engine(resolved_database_url)
        Base.metadata.create_all(bind=engine)
        application.state.session_factory = create_session_factory(engine)
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="Sistema de Gerenciamento de Voluntários",
        lifespan=lifespan,
    )

    def get_db(request: Request) -> Generator[Session, None, None]:
        session_factory = getattr(request.app.state, "session_factory", None)
        if session_factory is None:
            raise RuntimeError("Database session is not initialized.")
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    @application.get("/")
    def read_root():
        return {"message": "API funcionando!"}

    @application.post("/voluntarios", status_code=201, response_model=Volunteer)
    def create(
        volunteer: VolunteerCreate,
        db: Session = Depends(get_db),
    ):
        return create_volunteer(db, volunteer)

    @application.get("/voluntarios", response_model=list[Volunteer])
    def list_all(
        disponibilidade: Disponibilidade | None = None,
        cargo: str | None = None,
        db: Session = Depends(get_db),
    ):
        return list_volunteers(db, disponibilidade, cargo)

    @application.get("/voluntarios/{vol_id}", response_model=Volunteer)
    def get_one(
        vol_id: int,
        db: Session = Depends(get_db),
    ):
        volunteer = get_volunteer(db, vol_id)
        if not volunteer:
            raise HTTPException(status_code=404, detail="Voluntário não encontrado")
        return volunteer

    @application.put("/voluntarios/{vol_id}", response_model=Volunteer)
    def update(
        vol_id: int,
        volunteer: VolunteerCreate,
        db: Session = Depends(get_db),
    ):
        updated_volunteer = update_volunteer(db, vol_id, volunteer)
        if not updated_volunteer:
            raise HTTPException(status_code=404, detail="Voluntário não encontrado ou inativo")
        return updated_volunteer

    @application.delete("/voluntarios/{vol_id}", status_code=204)
    def remove(
        vol_id: int,
        db: Session = Depends(get_db),
    ):
        volunteer = delete_volunteer(db, vol_id)
        if not volunteer:
            raise HTTPException(status_code=404, detail="Voluntário não encontrado")
        return None

    return application


app = create_app()
