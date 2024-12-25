from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from .backends import auth_backend
from .schemas import UserRead, UserCreate
from api_v1.users.user_manager import get_user_manager

from config.models import User


router = APIRouter()


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    (auth_backend,)
)

router.include_router(fastapi_users.get_auth_router(auth_backend),
                      tags=['Auth'],
                      prefix='/auth',
                      )
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate),
                      tags=['Register'],
                      prefix='/register',
                      )
router.include_router(fastapi_users.get_verify_router(UserRead),
                      tags=['Verify'],
                      prefix='/verify',
                      )
router.include_router(fastapi_users.get_reset_password_router(),
                      tags=['Reset'],
                      prefix='/reset',
                      )
