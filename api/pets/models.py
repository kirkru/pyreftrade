from pydantic import BaseModel
from typing import Optional
from typing import List

class PetResponse(BaseModel):
    id: str
    name: str
    kind: str


class CreatePayload(BaseModel):
    name: str
    kind: str


class UpdatePayload(BaseModel):
    name: Optional[str]
    kind: Optional[str]


class PetListResponse(BaseModel):
    pets: List[PetResponse]
    next_token: str = None