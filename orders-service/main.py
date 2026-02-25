from fastapi import FastAPI, HTTPException 
from typing import List 
import requests 
from models import Order 

app = FastAPI(title="Orders Service") 

orders_db: List[Order] = [] 

PRODUCTS_URL = "http://products-service:8000/products" 

@app.get ("/orders", response_model=List[Order]) 
def get_orders(): 
    return orders_db 

@app. post ("/orders", response_model=Order) 
def create_order(order: Order):
    response = requests.get(f"{PRODUCTS_URL}/{order.product_id}") 
    if response. status_code != 200: 
        raise HTTPException(status_code=404, detail="Product not found") 
    orders_db. append(order) 
    return order 