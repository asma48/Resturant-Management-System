from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.schemas.data_model import MenuBase, MenuResponse, CategoryResponse,  MenuUpdate,CategoryUpdate
from app.models.database_models import Items,Menu
from datetime import datetime
from app.database.database_config import get_db
from app.middlewares.jwt import get_current_employe, authenticate_employe
from starlette import status




db_session = Annotated[Session, Depends(get_db)]

menu_router  = APIRouter(
    prefix = "/items",
    tags = ["Menu Items"]
)
category_router  = APIRouter(
    prefix = "/category",
    tags = ["Menu Category"]
)

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


