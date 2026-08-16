from sqlalchemy import Column, Integer, String, Float
from database import Base

class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float, index=True)
    stock = Column(Integer)
    description = Column(String)
