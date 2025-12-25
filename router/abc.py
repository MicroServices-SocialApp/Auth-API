from fastapi import APIRouter, Depends, status
from db import db_abc
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import get_async_db
from schemas.schemas_abc import AbcModel, AbcDisplay

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/create",
    deprecated=False,
    name='Abc_Creation',
    summary="une phrase qui resume la fonction.",
    description="une decription longue et precise",
    response_model=AbcDisplay,
    status_code=status.HTTP_201_CREATED,
    response_description="Succes de la reponse",
    responses={
        201: {
            "description": "SUCCESS - User has been created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "janedoe",
                        "email": "janedoe@example.com"
                    }
                }
            }
        },
        409: {
            "description": "CONFLICT - Email or Username already exists"
        }
    }
)
async def create(request: AbcModel, db: AsyncSession = Depends(get_async_db)):
    abc = await db_abc.create(request, db)
    return abc

#--------------------------------------------------------------------------