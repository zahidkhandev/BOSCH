from fastapi import FastAPI
from .models import Item

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item}

