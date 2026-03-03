from fastapi import FastAPI, HTTPException
from typing import List
from aiokafka import AIOKafkaProducer
from models import Order

app = FastAPI(title="Orders Service")
producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')

orders_db: List[Order] = []

@app.on_event("startup")
async def startup_event():
    await producer.start()

@app.get("/orders")
async def get_orders():
    return orders_db

@app.post("/orders", response_model=Order)
async def create_order(order: Order):
    orders_db.append(order)

    await producer.send_and_wait("order-created", order.model_dump_json().encode('utf-8'))

    return order