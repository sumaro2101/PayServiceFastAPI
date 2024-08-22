from fastapi import APIRouter

from .bodyies import CreateUser


router = APIRouter(tags=['users'])


@router.post('/users/')
def create_user(user: CreateUser):
    return {
        'message': 'success',
        'email': user.email,
    }
