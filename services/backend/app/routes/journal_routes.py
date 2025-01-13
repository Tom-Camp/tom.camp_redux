from app.models.journals import Journal
from app.routes.user_routes import get_current_user
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/journals", response_model=Journal)
async def create_journal(
    journal: Journal, current_user: str = Depends(get_current_user)
):
    await journal.insert()
    return journal


@router.get("/journals")
async def list_journals():
    journals = await Journal.find_all().to_list()
    return journals


@router.get("/journals/{journal_id}")
async def get_user(journal_id: str):
    journal = await Journal.get(journal_id)
    return journal
