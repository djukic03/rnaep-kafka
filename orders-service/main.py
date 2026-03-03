from fastapi import FastAPI, HTTPException
from typing import List
from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager
from models import Order

producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await producer.start()
    yield
    await producer.stop()

app = FastAPI(title="Orders Service", lifespan=lifespan)

orders_db: List[Order] = []

@app.get("/orders")
async def get_orders():
    return orders_db

@app.post("/orders", response_model=Order)
async def create_order(order: Order):
    orders_db.append(order)
    try:
        await producer.send_and_wait("order-created", order.model_dump_json().encode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return order