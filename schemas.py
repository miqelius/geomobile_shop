from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str = ""

class ProductResponse(ProductCreate):
    id: int
    class Config:
        from_attributes = True
