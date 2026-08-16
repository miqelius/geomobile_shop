import secrets
from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db
from models import ProductDB
from schemas import ProductResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoMobile Professional API", version="2.1")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# ადმინისტრირების მონაცემები (შეგიძლია შეცვალო სურვილისამებრ)
ADMIN_USER = "admin"
ADMIN_PASS = "geomobile2026"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="არასწორი მომხმარებელი ან პაროლი",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def seed_database():
    db = next(get_db())
    if db.query(ProductDB).count() == 0:
        brands = ["iPhone", "Samsung", "Xiaomi", "Google Pixel", "OnePlus"]
        for i in range(1, 13):
            brand = brands[i % len(brands)]
            db.add(ProductDB(
                name=f"{brand} Flagship Model #{i}",
                category="მობილური",
                price=float(800 + (i * 45)),
                stock=(i % 10) + 2,
                description=f"პრემიუმ სმარტფონი მაღალი წარმადობით."
            ))
        db.commit()

seed_database()

# მთავარი კატალოგი
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    # გასწორდა: request გადადის პირველ პოზიციაზე
    return templates.TemplateResponse(request, "index.html", {"products": products})

# პროდუქტის შეძენა (მარაგის შემცირება 1-ით)
@app.post("/buy/{product_id}")
def buy_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product and product.stock > 0:
        product.stock -= 1
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# დაცული ადმინ პანელი (ითხოვს ლოგინს და პაროლს)
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, username: str = Depends(verify_admin), db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    # გასწორდა: request გადადის პირველ პოზიციაზე
    return templates.TemplateResponse(request, "admin.html", {"products": products})

# დაცული პროდუქტის დამატება
@app.post("/admin/add")
def add_product_admin(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    username: str = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    new_product = ProductDB(
        name=name,
        category=category,
        price=price,
        stock=stock,
        description="ადმინ პანელიდან დამატებული პროდუქტი."
    )
    db.add(new_product)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# REST API
@app.get("/api/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()
