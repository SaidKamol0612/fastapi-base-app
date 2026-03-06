from typing import Annotated, List

from fastapi import (
    APIRouter,
    status,
    Depends,
    Body,
    Path,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas import user as schemas
from core.config import settings
from db import db_helper
from services import user_service


router = APIRouter(
    prefix=settings.api.v1.users_prefix,
    tags=["User"],
)


async def get_session(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> AsyncSession:
    return session


@router.post(
    "/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: Annotated[
        schemas.UserCreate, Body(..., description="User data to create")
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await user_service.create_user(
        user_data=user_in.model_dump(by_alias=True),
        session=session,
    )


@router.get(
    "/",
    response_model=List[schemas.UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await user_service.get_users(
        session=session,
    )


@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: Annotated[int, Path(..., description="ID of the User")],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await user_service.get_user(
        user_id=user_id,
        session=session,
    )


@router.patch(
    "/{user_id}",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
)
async def update_user_by_id(
    user_id: Annotated[int, Path(..., description="ID of the User")],
    user_in: Annotated[schemas.UserUpdate, Body(..., description="Patched user data")],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await user_service.update_user(
        user_id=user_id,
        user_data=user_in.model_dump(exclude_unset=True),
        session=session,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_by_id(
    user_id: Annotated[int, Path(..., description="ID of the User")],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await user_service.delete_user(
        user_id=user_id,
        session=session,
    )
