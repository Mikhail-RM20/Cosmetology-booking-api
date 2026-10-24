from fastapi import Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_current_access_token, oauth2_scheme
from schemas import EntryIn, EntryOut
from database import get_db
from typing import Annotated
from src import new_entry

router = APIRouter()

@router.post("/cosmetology/new_entry", response_model=EntryOut, status_code=status.HTTP_201_CREATED)
async def cosmetology_new_entry(
        entry_data: EntryIn,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_access_token(token=token)
    create_entry = await new_entry(db=db, entry_data=entry_data, id_user=user_id)

    return EntryOut(
        message=f"{create_entry['user_name']} {create_entry['user_surname']}, вы записаны."
                f"\nПроцедура: {create_entry['procedure_name']}."
                f"\nДата: {create_entry['entry_date'].strftime('%d.%m.%Y')}."
                f"\nВремя: {create_entry['entry_time'].strftime('%H:%M')}."
                f"\n"
                f"\nС Уважением, Иван Игоревич."
    )