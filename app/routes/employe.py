from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.schemas.data_model import UpdateEmploye, EmployeDelete
from app.models.database_models import Employe
from datetime import datetime
from app.database.database_config import get_db
from app.middlewares.auth import get_current_employe, authenticate_employe
from starlette import status
from app.middlewares.auth import login_router 



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