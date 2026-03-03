from fastapi import FastAPI
from typing import List
from models import Notification
from aiokafka import AIOKafkaConsumer
import asyncio, json

app = FastAPI(title="Notifications Service")

notifications_db: List[Notification] = []

@app.get("/notifications", response_model=List[Notification])
def get_notifications():
    return notifications_db

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())
    
async def consume():
    consumer = AIOKafkaConsumer(
        "order-confirmed", 
        bootstrap_servers='kafka:9092',
        group_id="notifications-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))
            notification = Notification(order_id=data['order_id'], product_id=data['product_id'], message=f"Order {data['order_id']} for product {data['product_id']} has been placed.")
            notifications_db.append(notification)
    finally:
        await consumer.stop()