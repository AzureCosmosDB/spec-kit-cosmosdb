from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/animal/{animal_id}")
async def list_applications_for_animal(animal_id: str, request: Request): ...

@router.post("/", status_code=201)
async def submit_application(request: Request): ...
