from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import List, Optional, Annotated, Literal
from datetime import datetime
import pycountry



class ItemsBase(BaseModel):
    
    item_name: str
    item_quantity: int

class PlaceOrder(BaseModel):
    items: List[ItemsBase]
    order_type_id: int
    


class Order_Details(BaseModel):
    order_id: int 
    items: List[ItemsBase]
    order_type_id: int
    order_date: datetime
    total_amount:float

class Order_Update(BaseModel):

    items: List[ItemsBase]
    order_type_id: int

class OrderResponse(BaseModel):
    order_id: int
    items: List[ItemsBase]
    order_type_id: int
    total_amount:float


class MenuBase(BaseModel):
    item_name:str 
    category_id:int
    price:float

class MenuUpdate(BaseModel):
    item_id:int
    item_name:Optional[str]
    category_id:Optional[int]
    price:Optional[float]    

class MenuResponse(BaseModel):
    
    item_name: str
    category_id: int
    price: float

class CategoryResponse(BaseModel):   
    category_id: int
    category: str

class CategoryUpdate(BaseModel):   
    category_id: int
    category: str

class Oder_Type_Response(BaseModel):
    order_type_id: int
    oder_type: str



class CreateEmploye(BaseModel):
    name: str
    email: str
    password: str

class EmployeInfo(BaseModel):
    name: str
    id: int
    email: EmailStr

class ForgetPassword(BaseModel):
    email: EmailStr
    otp: Annotated[str, constr(max_length=4)]
    new_password:str
    confirm_password:str


class EmployeToken(BaseModel):
    email: EmailStr
    password: str    

class EmployeTokenResponse(BaseModel):
    id: int 
    name: str 
    access_token: str

class Token(BaseModel):
    access_token: str
    token_type: str


class EmployeData(BaseModel):
    email: EmailStr


class EmployeDelete(BaseModel):
    name: str
    password: str    


class UpdateEmploye(BaseModel):
    name:Optional[str]
    mobile_no: Annotated[Optional[str], constr(pattern=r'^\+?[0-9]{10,15}$')]
    address:Optional[str]
    postal_code: Annotated[Optional[str], constr(pattern=r'^\d{5}$')]
    country:Annotated[Optional[str], constr(min_length=2, max_length=2)]
    @field_validator('country')
    def validate_country(cls, v):
        country_name = pycountry.countries.get(name=v.title())
        if country_name:
            return country_name.name
        return ValueError(f"'{v}' is not a valid country name or ISO code")



    
