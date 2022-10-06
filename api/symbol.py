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
# support /update_symbol

# DONE
# Create Datamodel
# update signatures, implementations of methods
# support lower case sector, ticker
# get symbols by sector


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

class SymbolRequest(BaseModel):
    ticker: str
    company: Optional[str]
    sector: Optional[str]
    description: str
    # current_price: Optional[float] = 10.10
    type: Optional[str] = 'stock'


@app.get("/")
async def root():
    return {"message": "Hello from Symbol API!"}


@app.put("/create-symbol")
async def create_symbol(symbolRequest: SymbolRequest):
    created_time = int(time.time())
    item = {
        "ticker": symbolRequest.ticker.lower(),
        "created_time": created_time,
        "company": symbolRequest.company,
        "sector": symbolRequest.sector.lower(),
        "description": symbolRequest.description,
        # "current_price": symbolRequest.current_price,
        "type": symbolRequest.type
        # "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"symbol": item}

@app.get("/get-symbol/{ticker}")
async def get_symbol(ticker: str):
    # Get the symbol from the table.
    table = _get_table()
    response = table.get_item(Key={"ticker": ticker.lower()})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"Symbol {ticker} not found")
    return item


@app.get("/get-symbols-in-sector/{sector}")
async def get_symbols_in_sector(sector: str):
    # List the top N symbols from the table, using the sector index.
    table = _get_table()
    response = table.query(
        IndexName="sector-index",
        KeyConditionExpression=Key("sector").eq(sector),
        ScanIndexForward=False,
        Limit=10,
    )
    symbols = response.get("Items")
    return {"symbols": symbols}

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
    return {"symbols": sectors}

@app.get("/list-symbols")
async def list_symbols():
    # List the sectors from the table, using the sector index.
    table = _get_table()
    response = table.scan(
        # IndexName="sector-index",
        # ProjectionExpression="sector",
        # KeyConditionExpression=Key("sector").eq(sector),
        # ScanIndexForward=False,
        # Limit=10,
    )
    symbols = response.get("Items")
    return {"symbols": symbols}

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


@app.delete("/delete-symbol/{ticker}")
async def delete_symbol(ticker: str):
    # Delete the symbol from the table.
    table = _get_table()
    table.delete_item(Key={"ticker": ticker})
    return {"deleted_ticker": ticker}


def _get_table():
    table_name = os.environ.get("SYMBOL_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
