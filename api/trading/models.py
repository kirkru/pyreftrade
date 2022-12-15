from pydantic import BaseModel
from typing import Optional
from typing import List

class InstrumentRequest(BaseModel):
    ticker: str
    company: Optional[str]
    sector: Optional[str]
    description: Optional[str]
    # current_price: Optional[float] = 10.10
    type: Optional[str] = 'stock'

class UpdateInstrument(BaseModel):
    company: Optional[str]
    sector: Optional[str]
    description: Optional[str]
    type: Optional[str] = 'stock'

class InstrumentResponse(BaseModel):
    ticker: str
    created_time: str
    company: str
    sector: str
    description: str
    # current_price: Optional[float] = 10.10
    type: Optional[str]

class InstrumentListResponse(BaseModel):
    Instruments: Optional[List[InstrumentResponse]]
    next_token: Optional[str] = None