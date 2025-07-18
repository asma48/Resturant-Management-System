from app.database.database_config import get_db
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from starlette import status
from app.schemas.data_model import CreateEmploye, Token, EmployeInfo, EmployeToken, EmployeTokenResponse, EmployeData, ForgetPassword
from app.models.database_models import Employe
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from ..utils.otp import send_OTP_email 
from app.middlewares.jwt import create_access_token, authenticate_employe, bcrypt_context


db_dependecy = Annotated[Session, Depends(get_db)]

login_router = APIRouter(
    prefix = '/employe',
    tags = ['Empolye']
)

@login_router.post("/sign_up", status_code=status.HTTP_201_CREATED, response_model=EmployeInfo)
def Sign_Up(db: db_dependecy, create_employe: CreateEmploye):
        
        create_employe = Employe(
            name = create_employe.name,
            email = create_employe.email,
            password = bcrypt_context.hash(create_employe.password)     
        )
        db.add(create_employe)
        db.commit()
        db.refresh(create_employe)
        return create_employe


@login_router.post("/log_in")
def Log_In( db: db_dependecy, employetoken: EmployeToken):
    

    employe = authenticate_employe(employetoken.email , employetoken.password, db)
    if not employe:
        return JSONResponse(content={"message": "Unauthorised Employe","status_code":404},
         status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = create_access_token(employetoken.email, timedelta(minutes=50))

    return JSONResponse(content={
        'message':"login succefully","status_code":200,
        "access_token":token,
        "data":{"id" :employe.id,  "email":employe.email}},
                            status_code=status.HTTP_200_OK)


@login_router.put("/forget_password")
def forget_password(email: EmailStr, db: db_dependecy):

    db_employe = db.query(Employe).filter(Employe.email == email).first()
    if not db_employe:
        return JSONResponse(content={
        'message':"Email does not exist","status_code":404},
                    status_code=status.HTTP_404_NOT_FOUND)
    otp = send_OTP_email(email)
    db_employe.otp = otp
    db.commit()
    db.refresh(db_employe)

    return JSONResponse(content={
        'message':"OTP sent Successfully to your email","status_code":200,
        "data":{"Email" :db_employe.email}},status_code=status.HTTP_200_OK)




@login_router.put("/reset_password")
def reset_password(employe:ForgetPassword, db: db_dependecy):
    db_employe = db.query(Employe).filter(Employe.email == employe.email).first()
    if not db_employe:
        return JSONResponse(content={
        'message':"Wrong Email","status_code":404},
                    status_code=status.HTTP_404_NOT_FOUND)
    if employe.otp != db_employe.otp:
        return JSONResponse(content={
        'message':"OTP dose not match","status_code":404,},
                    status_code=status.HTTP_404_NOT_FOUND)
    if employe.new_password != employe.confirm_password:
        return JSONResponse(content={
        'message':"Password and confirm password does not match","status_code":400},
                    status_code=status.HTTP_400_BAD_REQUEST)
    db_employe.password = bcrypt_context.hash(employe.new_password)  
    db_employe.otp = None 
    db.commit()
    db.refresh(db_employe)
    return JSONResponse(content={
        'message':"Password Reset Successfully","status_code":200,
        "data":{"Email" :db_employe.email}},
                            status_code=status.HTTP_200_OK)