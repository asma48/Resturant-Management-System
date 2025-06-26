from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Menu(Base):
    __tablename__='category'

    category_id = Column(Integer, primary_key= True, index= True)
    category = Column(String, unique=True, index=True)


class Items(Base):
    __tablename__ = 'item'
    
    item_id = Column(Integer, primary_key= True)
    item_name = Column(String, index=True)
    price = Column(Float, index=True)
    category_id = Column(Integer, ForeignKey('category.category_id'), index=True)



class Order(Base): 
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_date = Column(DateTime, index=True)
    order_type_id = Column(Integer, ForeignKey('ordertype.order_type_id'), index = True )


class Order_Detail(Base):
    __tablename__ = 'orderdetail'

    serial = Column(Integer, primary_key = True)
    order_id = Column(Integer,ForeignKey('orders.order_id'), index= True)
    item_id = Column(Integer, ForeignKey('item.item_id'))
    item_quantity = Column(Integer, index=True)

class Order_Type(Base):
    __tablename__ = 'ordertype'

    order_type_id = Column(Integer, primary_key=True)
    order_type = Column(String, index=True)

class Bill(Base):
    __tablename__ = 'bill'
    bill_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    total_amount = Column(String, index=True)


class Employe(Base):
    __tablename__ = 'employe'

    id = Column(Integer, primary_key=True)
    name = Column(String, index = True)
    email = Column(String, index = True, unique=True)
    password = Column(String, index =True)
    address = Column(String, index=True)
    postal_code = Column(String(10), index= True)
    mobile_num = Column(String(15), index = True)
    country = Column(String(60), index =True)
    otp = Column(String(4), index =True)



