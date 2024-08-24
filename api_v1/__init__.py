from fastapi import APIRouter

from .products.views import router as products
from .users.views import router as users


router = APIRouter()
router.include_router(products,
                      prefix='/api/v1')
router.include_router(users,
                      prefix='/api/v1')
