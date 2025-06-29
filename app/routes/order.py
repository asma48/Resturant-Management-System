from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.schemas.data_model import MenuBase, PlaceOrder, OrderResponse, Order_Details, MenuResponse, ItemsBase, Order_Update, CategoryResponse, EmployeData, UpdateEmploye, EmployeDelete, MenuUpdate,CategoryUpdate, EmployeInfo
from app.models.database_models import Items,Order, Order_Detail, Order_Type, Bill, Menu, Employe
from datetime import datetime
from app.database.database_config import get_db
from app.middlewares.jwt import get_current_employe, authenticate_employe
from starlette import status


order_router  = APIRouter(
    prefix= "/order",
    tags = ["Order"]
)


db_session = Annotated[Session, Depends(get_db)]


@order_router.post("/placeorder", response_model=OrderResponse)
def take_order(order:PlaceOrder, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):

    db_order_type = db.query(Order_Type).filter(Order_Type.order_type_id == order.order_type_id).first()
    db_order = Order(order_type_id = db_order_type.order_type_id, order_date= datetime.now())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    amount = 0.00
    for item in order.items:
        db_item = db.query(Items).filter(Items.item_name == item.item_name).first()
        if db_item is None:
            raise HTTPException(status_code= 404, detail="Item is not available")
        amount += db_item.price * item.item_quantity
        db_order_detail = Order_Detail(order_id= db_order.order_id, item_id = db_item.item_id, item_quantity = item.item_quantity)
        db.add(db_order_detail)
        db.commit()
        db.refresh(db_order_detail) 
    db_bill = Bill(total_amount = amount, order_id = db_order.order_id)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    order_detail = Order_Details(
    order_id = db_order.order_id,
    items = order.items,
    order_type_id = db_order.order_type_id,
    order_date = db_order.order_date,
    total_amount = db_bill.total_amount
    )
    return order_detail



        
@order_router.get("/orderdetail", response_model=Order_Details)
def order_detail(order_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
 

    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order is None:
            raise HTTPException(status_code= 404, detail="Order does not exist")
    
    db_order_detail = db.query(Order_Detail).filter(Order_Detail.order_id == order_id).all()
    
    items_list = []
    for item in db_order_detail:
        db_order_item = db.query(Items).filter(Items.item_id == item.item_id).first()
        items_list.append(ItemsBase(
            item_name = db_order_item.item_name,
            item_quantity = item.item_quantity
        ))
          
    db_order_bill = db.query(Bill).filter(Bill.order_id == order_id).first()
   
    order_detail = Order_Details(
    order_id = order_id,
    items = items_list,
    order_type_id = db_order.order_type_id,
    order_date = db_order.order_date,
    total_amount = db_order_bill.total_amount
    )

    return order_detail

@order_router.put("/orderupdate")
def update_order_detail(order_id: int, order:Order_Update, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order is None:
            raise HTTPException(status_code= 404, detail="Order does not exist")  

    db_order.order_type_id = order.order_type_id

    db_order_detail = db.query(Order_Detail).filter(Order_Detail.order_id == order_id).all()
    amount = 0.00
    for item in order.items:
        db_item = db.query(Items).filter(Items.item_name == item.item_name).first()
        if db_item is None:
            raise HTTPException(status_code= 404, detail="Item is not available")
        db_item_detail = db.query(Order_Detail).filter(Order_Detail.item_id == db_item.item_id).first()
        
        if db_item_detail is None:
            db_order_update = Order_Detail(item_quantity = item.item_quantity, item_id = db_item.item_id  )
            db.add(db_order_update)
            db.commit()
            db.refresh(db_order_update) 
        
        if item.item_quantity != db_item_detail.item_quantity:
            db_item_detail.item_quantity = item.item_quantity
            db.commit()
            db.refresh(db_item_detail)

    
    db_item_quantity = db.query(Order_Detail).filter(Order_Detail.order_id == order_id).all()
    for item in db_item_quantity:
        db_item = db.query(Items).filter(Items.item_id == item.item_id).first()
        amount += (db_item.price * item.item_quantity)

    
    items_list = []
    for item in db_order_detail:
        db_order_item = db.query(Items).filter(Items.item_id == item.item_id).first()
        items_list.append(ItemsBase(
            item_name = db_order_item.item_name,
            item_quantity = item.item_quantity
        ))

    

    db_bill = db.query(Bill).filter(Bill.order_id == order_id).first()
    db_bill.total_amount = amount
    db.commit()
    db.refresh(db_bill) 

    updated_order_details = OrderResponse(
    order_id = order_id,
    items = items_list,
    order_type_id = db_order.order_type_id,
    order_date = db_order.order_date,
    total_amount = db_bill.total_amount
    )
    return updated_order_details
    


@order_router.delete("/orderdelete")
def delet_order(order_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):

    db_order_detail = db.query(Order_Detail).filter(Order_Detail.order_id == order_id).all()
    for detail in db_order_detail:
        db.delete(detail)
        db.commit()

    db_bill = db.query(Bill).filter(Bill.order_id == order_id).first()
    db.delete(db_bill)
    db.commit()
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order is None:
            raise HTTPException(status_code= 404, detail="Order does not exist")  
    db.delete(db_order)
    db.commit()

    return Response(content="Oder Deleted Successfully",
         status_code=status.HTTP_200_OK)


