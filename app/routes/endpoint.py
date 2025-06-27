from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.schemas.data_model import MenuBase, PlaceOrder, OrderResponse, Order_Details, MenuResponse, ItemsBase, Order_Update, CategoryResponse, EmployeData, UpdateEmploye, EmployeDelete, MenuUpdate,CategoryUpdate, EmployeInfo
from app.models.database_models import Items,Order, Order_Detail, Order_Type, Bill, Menu, Employe
from datetime import datetime
from app.database.database_config import get_db
from app.middlewares.auth import get_current_employe, authenticate_employe
from starlette import status
from app.middlewares.auth import login_router 

employe_router  = APIRouter(
    prefix= "/employe",
    tags = ["Account Settings"]
)

order_router  = APIRouter(
    prefix= "/order",
    tags = ["Order"]
)

menu_router  = APIRouter(
    prefix = "/items",
    tags = ["Menu Items"]
)
category_router  = APIRouter(
    prefix = "/category",
    tags = ["Menu Category"]
)
order_Type_router  = APIRouter(
    prefix = "/order_type",
    tags = ["Order Type"]
)


db_session = Annotated[Session, Depends(get_db)]


@login_router.get('/')
def get_employe(db: db_session,current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_employe = db.query(Employe).filter(Employe.email == current_employe.email).first()
    
    return JSONResponse(content= {"Message" : "Current Employe ", 
                                  "data": {"id": db_employe.id, "name": db_employe.name, "email": db_employe.email }},
                                                            status_code=status.HTTP_200_OK)

@login_router.get("/list_of_employes")
def list_of_employes(db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_all_employes = db.query(Employe).all()
    return JSONResponse(content= {"message":"Here is list of employes", "data": {db_all_employes}},
                                                            status_code=status.HTTP_200_OK)


@login_router.put('/update/{id}')
def update_employe(id:int, employe:UpdateEmploye, current_employe: Annotated[dict, Depends(get_current_employe)], db: db_session):
    
    db_update_employe = db.query(Employe).filter(Employe.id == id).first() 
    if employe != db_update_employe:
        db_update_employe.name = employe.name
        db_update_employe.mobile_num = employe.mobile_no
        db_update_employe.address = employe.address
        db_update_employe.postal_code = employe.postal_code
        db_update_employe.country = employe.country        
        db.commit()
        db.refresh(db_update_employe) 
    
    return JSONResponse(content={
        'message':"Employe Updated Successfully","satus_code":200,
        "data":{"name":db_update_employe.name, "email": db_update_employe.email}},
                            status_code=status.HTTP_200_OK)


@login_router.delete("/delete employe")
def delete_employe_account(delete_employe:EmployeDelete, current_employe: Annotated[dict, Depends(get_current_employe)], db:db_session):
    if authenticate_employe(delete_employe.name, delete_employe.password):           
        db_employe = db.query(Employe).filter(Employe.name == delete_employe.name).first()
        db.delete(db_employe)
        db.commit()
    return JSONResponse(content= {"message":"Employe Deleted Successfully", "status_code": 200},
                                                            status_code=status.HTTP_200_OK)



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



@menu_router.post("/menu", response_model=MenuResponse)
def menu_item(menu:MenuBase, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_category = db.query(Menu).filter(Menu.category_id == menu.category_id).first()
    if db_category is None:
        raise HTTPException(status_code= 404, detail="Category does not exist")
    
    db_item_name = db.query(Items).filter(Items.item_name == menu.item_name).first()
    if db_item_name is not None:
        raise HTTPException(status_code= 404, detail="Item already exist")
    db_item = Items(item_name = menu.item_name, category_id = menu.category_id, price = menu.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return menu

@menu_router.get("/menu_list", response_model=List[MenuResponse])
def menu_item_list(db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):

    db_item = db.query(Items).all()
    return db_item


@menu_router.get("/menu_item", response_model=MenuResponse)
def menu_item_by_id(item_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_item = db.query(Items).filter(Items.item_id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code= 404, detail="Item does not exist")
    return db_item

@menu_router.put("/menu_update")
def menu_item_by_id(item:MenuUpdate, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_item = db.query(Items).filter(Items.item_id == item.item_id).first()
    if db_item is None:
        raise HTTPException(status_code= 404, detail="Item does not exist")
    if db_item.item_name != item.item_name:
        db_item.item_name = item.item_name
    if db_item.category_id != item.category_id:
        db_item.category_id = item.category_id
    if db_item.price != item.price:
        db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return JSONResponse(content={
        'message':"Item Updated Successfully",
        "data":{"id" : db_item.item_id, "Item Name":db_item.item_name, "Category id": db_item.category_id, "price": db_item.price}},
                            status_code=status.HTTP_200_OK)

@menu_router.delete("/delete_menu-item")
def delete_item(item_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_menu_item = db.query(Items).filter(Items.item_id == item_id).first()
    if db_menu_item is None:
        raise HTTPException(status_code= 404, detail="Item does not exist")
    db.delete(db_menu_item)
    db.commit()
    return Response(content="Item Deleted Successfully" , status_code=status.HTTP_200_OK)



@category_router.post("/create_category")
def create_category(category: str, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_category = Menu(category = category)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return Response(content="Category Added Successfully" , status_code=status.HTTP_200_OK)

@category_router.get("/category_list", response_model=List[CategoryResponse] )
def category_list(db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):

    db_category = db.query(Menu).all()
    return db_category

@category_router.get("/category", response_model=CategoryResponse)
def category(category_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_category = db.query(Menu).filter(Menu.category_id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code= 404, detail="Category does not exist")
    return db_category


@category_router.put("/category_update")
def menu_item_by_id(category:CategoryUpdate, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_category = db.query(Menu).filter(Menu.category_id == category.category_id).first()
    if db_category is None:
        raise HTTPException(status_code= 404, detail="Category does not exist")
    if db_category.category_id != category.category_id:
        db_category.category_id = category.category_id
    if db_category.category != category.category:
        db_category.category = category.category
    db.commit()
    db.refresh(db_category)

    return JSONResponse(content={
        'message':"Category Updated Successfully",
        "data":{"id" : db_category.category_id, "Category":db_category.category}},
                            status_code=status.HTTP_200_OK)




@category_router.delete("/delete_category")
def delete_item(category_id: int, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_category = db.query(Menu).filter(Menu.category_id == category_id).first()
    if db_category is None:
            raise HTTPException(status_code= 404, detail="Category does not exist")
    db.delete(db_category)
    db.commit()
    return Response(content="category deleted Successfully", status_code=status.HTTP_200_OK)




@order_Type_router.post("/")
def order_type(order_type: str, db:db_session, current_employe: Annotated[dict, Depends(get_current_employe)]):
    db_order_type = Order_Type(order_type = order_type)
    db.add(db_order_type)
    db.commit()
    db.refresh(db_order_type)  
    return db_order_type



