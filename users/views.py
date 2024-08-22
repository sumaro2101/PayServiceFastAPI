from fastapi import APIRouter

from .schemas import CreateUser
from . import crud


router = APIRouter(prefix='/users',
                   tags=['users'],
                   )


@router.post('/create/')
def create_user(user: CreateUser):
    return crud.create_user(user)
