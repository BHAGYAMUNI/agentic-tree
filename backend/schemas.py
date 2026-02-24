from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TreeCreate(BaseModel):
    name: str
    tree_data: Optional[Dict[str, Any]] = None

class TreeResponse(BaseModel):
    id: int
    name: str
    tree_data: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class TreeInsertRequest(BaseModel):
    parent_value: Optional[int] = None
    new_value: int
    direction: str

    # basic validation
    def validate_direction(self):
        if self.direction not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls._validate

    @classmethod
    def _validate(cls, values):
        dir = values.get('direction')
        if dir not in ("left", "right"):
            raise ValueError("direction must be 'left' or 'right'")
        return values


class TreeValueRequest(BaseModel):
    value: int


class TreeUpdateNodeRequest(BaseModel):
    node_id: int
    new_value: int


class TreeSearchResponse(BaseModel):
    found: bool
    node_id: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    tree_id: int

class ChatResponse(BaseModel):
    response: str