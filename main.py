from fastapi import FastAPI

from products.views import router as products
from users.views import router as users


app = FastAPI()
app.include_router(products)
app.include_router(users)

@app.get('/')
def hello_index():
    return {
        'message': 'Hello index!',
    }
