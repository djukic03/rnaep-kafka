from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import List
from models import Product
import asyncio, json

app = FastAPI(title="Products Service")
producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')

products_db = {
    1: Product(id=1, name="Laptop", price=1500.0, quantity=10),
    2: Product(id=2, name="Mouse", price=25.0, quantity=50)
}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())

async def consume():
    consumer = AIOKafkaConsumer(
        "order-created", 
        bootstrap_servers='kafka:9092', 
        group_id="products-group"
    )
    await consumer.start()
    await producer.start()
    try:
        async for msg in consumer:
            order = json.loads(msg.value.decode('utf-8'))
            product = products_db.get(order['product_id'])
            
            if product and product.quantity >= order['quantity']:
                product.quantity -= order['quantity']
                await producer.send_and_wait("order-confirmed", json.dumps({
                    "order_id": order['id'],
                    "product_id": product.id
                }).encode('utf-8'))
    finally:
        await consumer.stop()
        
@app.get("/products")
async def get_products():
    return products_db