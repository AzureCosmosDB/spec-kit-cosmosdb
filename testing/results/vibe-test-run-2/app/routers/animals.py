from fastapi import APIRouter, Request, Query
from typing import Optional
router = APIRouter()

@router.get("/")
async def list_animals(request: Request, species: Optional[str] = None): ...

@router.get("/{animal_id}")
async def get_animal(animal_id: str, request: Request): ...

@router.post("/", status_code=201)
async def create_animal(request: Request): ...
