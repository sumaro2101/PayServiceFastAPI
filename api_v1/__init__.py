from fastapi import APIRouter

from .products.views import router as products
from .users.views import router as users
from .posts.views import router as posts
from .orders.views import router as orders
from .auth.views import router as auth
from .basket.views import router as basket
from .payments.views import router as payment
from .promos.views import router as promos


router = APIRouter()

router.include_router(products,
                      prefix='/api/v1')
router.include_router(users,
                      prefix='/api/v1')
router.include_router(posts,
                      prefix='/api/v1')
router.include_router(orders,
                      prefix='/api/v1')
router.include_router(auth,
                      prefix='/api/v1')
router.include_router(basket,
                      prefix='/api/v1')
router.include_router(payment,
                      prefix='/api/v1')
router.include_router(promos,
                      prefix='/api/v1')
