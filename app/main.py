from fastapi import FastAPI
from app.routes.endpoint import menu_router, order_router, category_router, order_Type_router, employe_router
from app.middlewares.auth import router


app = FastAPI()
app.include_router(employe_router)
app.include_router(order_router)
app.include_router(menu_router)
app.include_router(category_router)
app.include_router(order_Type_router)
app.include_router(router)




