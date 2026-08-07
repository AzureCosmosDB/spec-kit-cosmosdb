from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/")
async def list_shelters(request: Request): ...

@router.get("/{shelter_id}")
async def get_shelter(shelter_id: str, request: Request): ...

@router.post("/", status_code=201)
async def create_shelter(request: Request): ...
