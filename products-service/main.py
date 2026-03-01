from fastapi import FastAPI, HTTPException
from typing import List
from models import Product

app = FastAPI(title="Products Service")

products_db: List[Product] = [
    Product(id=1, name="Laptop", price=1500.0, quantity=10),
    Product(id=2, name="Mouse", price=25.0, quantity=50)
]

@app.get("/products", response_model=List[Product])
def get_products():
    return products_db

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}/reduce", response_model=Product)
def reduce_quantity(product_id: int, quantity: int):
    for product in products_db:
        if product.id == product_id:
            if product.quantity < quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            product.quantity -= quantity
            return product
    raise HTTPException(status_code=404, detail="Product not found")