from fastapi import FastAPI, HTTPException
from typing import List
import requests
from models import Order

app = FastAPI(title="Orders Service")

orders_db: List[Order] = []

PRODUCTS_URL = "http://products-service:8000/products"
NOTIFICATIONS_URL = "http://notifications-service:8000/notifications"

@app.get("/orders", response_model=List[Order])
def get_orders():
    return orders_db

@app.post("/orders", response_model=Order)
def create_order(order: Order):
    response = requests.get(f"{PRODUCTS_URL}/{order.product_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Product not found")

    product = response.json()
    if product["quantity"] < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    requests.put(f"{PRODUCTS_URL}/{order.product_id}/reduce", params={"quantity": order.quantity})

    orders_db.append(order)

    requests.post(NOTIFICATIONS_URL, json={
        "order_id": order.id,
        "product_id": order.product_id,
        "message": f"Order {order.id} for product {order.product_id} has been placed."
    })

    return order