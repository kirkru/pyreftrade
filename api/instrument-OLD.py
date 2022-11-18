import os
import time
from unicodedata import decimal
import boto3
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key

app = FastAPI()
handler = Mangum(app)

# TODO
# get sectors - added a global secondary index
# support /update_instrument

# DONE
# Create Datamodel
# update signatures, implementations of methods
# support lower case sector, ticker
# get instruments by sector


'''
Request sample
{
  "ticker": "QQQ",
  "company": "Tech ETF",
  "sector": "Technology",
  "description": "ETF for tech",
  "type": "stock"
}

{
  "ticker": "XLE",
  "company": "Energy ETF",
  "sector": "Energy",
  "description": "ETF for energy",
  "type": "stock"
}
'''

class InstrumentRequest(BaseModel):
    ticker: str
    company: Optional[str]
    sector: Optional[str]
    description: str
    # current_price: Optional[float] = 10.10
    type: Optional[str] = 'stock'


@app.get("/")
async def root():
    return {"message": "Hello from Instrument API!"}


@app.put("/create-instrument")
async def create_instrument(instrumentRequest: InstrumentRequest):
    created_time = int(time.time())
    item = {
        "ticker": instrumentRequest.ticker.lower(),
        "created_time": created_time,
        "company": instrumentRequest.company,
        "sector": instrumentRequest.sector.lower(),
        "description": instrumentRequest.description,
        # "current_price": instrumentRequest.current_price,
        "type": instrumentRequest.type
        # "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"instrument": item}

@app.get("/get-instrument/{ticker}")
async def get_instrument(ticker: str):
    # Get the instrument from the table.
    table = _get_table()
    response = table.get_item(Key={"ticker": ticker.lower()})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} not found")
    return item


@app.get("/get-instruments-in-sector/{sector}")
async def get_instruments_in_sector(sector: str):
    # List the top N instruments from the table, using the sector index.
    table = _get_table()
    response = table.query(
        IndexName="sector-index",
        KeyConditionExpression=Key("sector").eq(sector),
        ScanIndexForward=False,
        Limit=10,
    )
    instruments = response.get("Items")
    return {"instruments": instruments}

@app.get("/get-sectors")
async def get_sectors():
    # List the sectors from the table, using the sector index.
    table = _get_table()
    response = table.scan(
        # IndexName="sector-index",
        ProjectionExpression="sector",
        # KeyConditionExpression=Key("sector").eq(sector),
        # ScanIndexForward=False,
        # Limit=10,
    )
    sectors = response.get("Items")
    return {"sectors": sectors}

@app.get("/list-instruments")
async def list_instruments():
    # List the sectors from the table, using the sector index.
    table = _get_table()
    response = table.scan(
        # IndexName="sector-index",
        # ProjectionExpression="sector",
        # KeyConditionExpression=Key("sector").eq(sector),
        # ScanIndexForward=False,
        # Limit=10,
    )
    instruments = response.get("Items")
    return {"instruments": instruments}

# @app.put("/update-symbol")
# async def update_symbol(symbolRequest: SymbolRequest):
#     # Update the symbol in the table.
#     table = _get_table()
#     table.update_item(
#         Key={"ticker": symbolRequest.ticker},
#         UpdateExpression="SET description = :description",
#         # UpdateExpression="SET description = :description, current_price = :current_price",
#         ExpressionAttributeValues={
#             ":description": symbolRequest.description,
#             # ":current_price": symbolRequest.current_price,
#         },
#         ReturnValues="ALL_NEW",
#     )
#     return {"updated_ticker": symbolRequest.ticker}


@app.delete("/delete-instrument/{ticker}")
async def delete_instrument(ticker: str):
    # Delete the instrument from the table.
    table = _get_table()
    table.delete_item(Key={"ticker": ticker})
    return {"deleted_instrument": ticker}


def _get_table():
    table_name = os.environ.get("INSTRUMENT_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
