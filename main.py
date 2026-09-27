from fastapi import FastAPI, HTTPException

from crud import (
    create_volunteer,
    delete_volunteer,
    get_volunteer,
    list_volunteers,
    update_volunteer,
)
from models import Disponibilidade, Volunteer
from schemas import VolunteerCreate

app = FastAPI(title="Sistema de Gerenciamento de Voluntários")

@app.get("/")
def read_root():
    return {"message": "API funcionando!"}

@app.post("/voluntarios", status_code=201, response_model=Volunteer)
def create(v: VolunteerCreate):
    return create_volunteer(v)

@app.get("/voluntarios", response_model=list[Volunteer])
def list_all(
    disponibilidade: Disponibilidade | None = None,
    cargo: str | None = None
):
    return list_volunteers(disponibilidade, cargo)

@app.get("/voluntarios/{vol_id}", response_model=Volunteer)
def get_one(vol_id: int):
    volunteer = get_volunteer(vol_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    return volunteer

@app.put("/voluntarios/{vol_id}", response_model=Volunteer)
def update(vol_id: int, v: VolunteerCreate):
    updated_volunteer = update_volunteer(vol_id, v)
    if not updated_volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado ou inativo")
    return updated_volunteer

@app.delete("/voluntarios/{vol_id}", status_code=204)
def remove(vol_id: int):
    volunteer = delete_volunteer(vol_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    return
