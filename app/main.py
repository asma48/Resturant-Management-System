from fastapi import FastAPI
from app.routes.employe import login_router
from app.routes.menu import menu_router, category_router
from app.routes.order_type import order_Type_router
from app.routes.order import order_router
from app.middlewares.auth import login_router


app = FastAPI()
app.include_router(login_router)
app.include_router(order_router)
app.include_router(menu_router)
app.include_router(category_router)
app.include_router(order_Type_router)

