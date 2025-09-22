from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    tags: list[str] = []

