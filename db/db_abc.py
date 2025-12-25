# from sqlalchemy import select, update as sql_update, delete as sql_delete
from schemas.schemas_abc import AbcModel
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.models import DbAbc
# import asyncio

async def create(request: AbcModel, db: AsyncSession):
    
    new_user = DbAbc(
        abc=request.abc,
    )
    db.add(new_user)
    await db.commit()
    return {"detail": "New User has been successfully added to the database."}


# --------------------------------------------------------------------------