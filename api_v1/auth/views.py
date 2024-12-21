from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from .backends import auth_backend
from .schemas import UserRead, UserCreate
from api_v1.users.user_manager import get_user_manager

from config.models import User


router = APIRouter(prefix='/auth',
                   tags=['Auth'])


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    (auth_backend,)
)

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_reset_password_router())
