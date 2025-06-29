from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.database_models import Order_Type, Bill, Menu, Employe
from datetime import datetime
from app.database.database_config import get_db

from starlette import status
from app.middlewares.auth import login_router 
from app.middlewares.auth import get_current_employe, authenticate_employe


db_session = Annotated[Session, Depends(get_db)]


order_Type_router  = APIRouter(
    prefix = "/order_type",
    tags = ["Order Type"]
)





@order_Type_router.post("/")
def order_type(order_type: str, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_order_type = Order_Type(order_type = order_type)
    db.add(db_order_type)
    db.commit()
    db.refresh(db_order_type)  
    return db_order_type



