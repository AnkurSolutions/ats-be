from pydantic import BaseModel

class StateCreate(BaseModel):
    name: str
    code: str | None = None

class StateOut(BaseModel):
    id: int
    name: str
    code: str | None
