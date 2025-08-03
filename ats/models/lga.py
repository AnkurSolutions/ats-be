from pydantic import BaseModel

class LgaCreate(BaseModel):
    name: str
    state_id: int

class LgaOut(BaseModel):
    id: int
    name: str
    state_id: int
