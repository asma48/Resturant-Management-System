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







SECRET_KEY = 'dr53h35hbtbt5ngbr45nrth45rth5ngr5'
ALGORITHM = 'HS256'


bcrypt_context =  CryptContext(schemes= ['bcrypt'], deprecated= 'auto')

bearer_scheme = HTTPBearer()

def authenticate_employe(email:str, password: str, db):
    employe = db.query(Employe).filter(Employe.email == email).first()
    if not employe:
        return JSONResponse(content={"message":"Incorrect Email Address", "status_code":404}, 
                        status_code=status.HTTP_404_NOT_FOUND)
    if not bcrypt_context.verify(password, employe.password):
        return JSONResponse(content={"message":"Incorrect Password", "status_code":404}, 
                        status_code=status.HTTP_404_NOT_FOUND)
    return employe


def create_access_token(email: str, expire_delta: timedelta):
    encode = {'sub': email }
    expires = datetime.now() + expire_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



def get_current_employe(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):

    token = credentials.credentials
    try:    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get('sub')
        if email is None:
            return JSONResponse(content={
            'message':"Unauthorised Employe","status_code":401},
                        status_code=status.HTTP_401_UNAUTHORIZED)
        return EmployeData(email = email)
    except JWTError:
        return JSONResponse(content={
            'message':"Unauthorised Employe","status_code":401},
                    status_code=status.HTTP_401_UNAUTHORIZED)

