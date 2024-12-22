from typing import Annotated

from fastapi import HTTPException, Path, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.models import Post
from config.database import db_connection
from . import crud
from .common import ErrorCode


async def get_post_by_id(
    post_id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(db_connection.session_geter),
) -> Post:
    product = await crud.get_post(
        session=session,
        post_id=post_id,
        )
    if product:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorCode.POST_NOT_FOUND,
        )
